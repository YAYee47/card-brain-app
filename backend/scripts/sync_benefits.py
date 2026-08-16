import asyncio
import os
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from app.db.database import AsyncSessionLocal
from app.models.cards import Card
from app.models.card_benefits import CardBenefit
from datetime import date, datetime

# 定義 Gemini 輸出的 JSON Schema
class BenefitRule(BaseModel):
    channel_name: str = Field(description="通路名稱，例如：國內一般消費、網購、日本消費、百大特店、蝦皮購物、淘寶等")
    base_rate: float = Field(description="基礎回饋百分比，例如 1.0 代表 1%")
    bonus_rate: float = Field(description="加碼回饋百分比，例如 2.0 代表 2%")
    monthly_cap_ntd: float | None = Field(description="加碼回饋的每月上限金額(台幣)，若無上限則為 null", default=None)

class CardBenefitsResponse(BaseModel):
    benefits: list[BenefitRule]

async def fetch_page_content(url: str) -> tuple[str, list[bytes]]:
    """抓取網頁的純文字內容與圖片(為了 vision)"""
    print(f"  [HTTP] Fetching {url} ...")
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 移除不必要的標籤
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
                
            text = soup.get_text(separator='\n', strip=True)
            
            # 尋找前 3 張可能的 DM 圖片 (避免太多圖片導致 token 爆掉)
            images_data = []
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src')
                if src and ('jpg' in src.lower() or 'png' in src.lower() or 'jpeg' in src.lower()):
                    if src.startswith('/'):
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        src = f"{parsed.scheme}://{parsed.netloc}{src}"
                    elif not src.startswith('http'):
                        continue
                        
                    try:
                        img_resp = await client.get(src)
                        if img_resp.status_code == 200:
                            images_data.append((img_resp.content, img_resp.headers.get('content-type', 'image/jpeg')))
                            if len(images_data) >= 3:
                                break
                    except Exception as e:
                        print(f"  [Warning] Failed to fetch image {src}: {e}")
                        
            return text, images_data
    except Exception as e:
        print(f"  [Error] Failed to fetch {url}: {e}")
        return "", []

async def process_card_id(db, client: genai.Client, card_id: int):
    from sqlalchemy import select
    result = await db.execute(select(Card).where(Card.id == card_id))
    card = result.scalar_one_or_none()
    if not card or not card.benefit_url:
        print(f"Skipping card_id {card_id}: No URL or not found")
        return

    print(f"\nProcessing {card.bank_name} {card.card_name} ...")
    urls = [u.strip() for u in card.benefit_url.split(',')]
    
    all_text = ""
    all_images = []
    for url in urls:
        if not url: continue
        text, images = await fetch_page_content(url)
        all_text += f"\n--- Content from {url} ---\n{text}\n"
        all_images.extend(images)
        
    if not all_text.strip():
        print("  [Error] No text extracted. Skipping.")
        return

    print("  [Gemini] Analyzing content with Gemini Vision...")
    
    # 準備 Gemini 內容
    contents = [
        types.Part.from_text(
            text=f"以下是【{card.bank_name} {card.card_name}】信用卡的官方網頁文字，"
                 f"其中可能包含圖片(DM)。請分析這些資料，提取出該卡片的所有「消費回饋權益規則」。\n\n"
                 f"注意：\n"
                 f"1. 如果是百大特店、任意選等，請拆分成不同的 rule。\n"
                 f"2. 找尋「蝦皮」、「momo」、「淘寶」、「App Store」等特定通路的加碼。\n"
                 f"3. 確保包含「國內一般消費」與「國外消費」的基本回饋。\n"
                 f"網頁文字：\n{all_text[:15000]}" # 限制文字長度避免過長
        )
    ]
    
    for img_bytes, mime_type in all_images[:3]:
        contents.append(types.Part.from_bytes(data=img_bytes, mime_type=mime_type))
        
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CardBenefitsResponse,
                temperature=0.1
            )
        )
        
        result_json = response.text
        data = CardBenefitsResponse.model_validate_json(result_json)
        
        # 刪除舊權益
        from sqlalchemy import delete
        await db.execute(delete(CardBenefit).where(CardBenefit.card_id == card.id))
        
        # 寫入新權益
        for b in data.benefits:
            new_benefit = CardBenefit(
                card_id=card.id,
                channel_name=b.channel_name,
                base_rate=b.base_rate,
                bonus_rate=b.bonus_rate,
                monthly_cap_ntd=b.monthly_cap_ntd,
                effective_date=date.today()
            )
            db.add(new_benefit)
            print(f"  [+] Added Rule: {b.channel_name} (Base: {b.base_rate}%, Bonus: {b.bonus_rate}%, Cap: {b.monthly_cap_ntd})")
            
        card.last_synced_at = datetime.now()
        await db.commit()
        print("  [Success] Database updated.")
        
    except Exception as e:
        print(f"  [Error] Gemini analysis failed: {e}")
        await db.rollback()

async def main():
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.")
        return
        
    client = genai.Client(api_key=api_key)
    
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(Card.id))
        card_ids = result.scalars().all()
        
        for cid in card_ids:
            await process_card_id(db, client, cid)

if __name__ == "__main__":
    asyncio.run(main())
