import os
import re
import json
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from pydantic import BaseModel
from google import genai
from google.genai import types

class ScrapedBenefit(BaseModel):
    channel_name: str
    base_rate: float
    bonus_rate: float
    monthly_cap_ntd: Optional[float] = None  # 僅為加碼回饋的封頂金額，基礎回饋永遠無上限

GEMINI_SYSTEM_PROMPT = """
你是一個專業的台灣信用卡權益擷取助手。
請閱讀以下的信用卡官方網頁文字，根據使用者的「專屬條件」，精確提取該卡片目前所有的回饋權益，並以 JSON 陣列 (Array) 格式回傳。
不要加任何額外說明文字或 Markdown 區塊。

回傳的 JSON Array 每個物件必須包含以下欄位：
- "channel_name": <字串，盡量列出具體的通路/商家名稱，而非只寫「指定通路」。
    例如：如果優惠適用蝦皮、momo、PChome，則應列出 "蝦皮/momo/PChome" 或拆成多筆。
    對於「國內一般消費」、「國外一般消費」等通用通路，就直接寫通用名稱即可。>
- "base_rate": <浮點數，基礎回饋率 %，例如 1.0。基礎回饋永遠沒有上限。>
- "bonus_rate": <浮點數，加碼回饋率 %，例如 2.0。如果沒有加碼填 0.0>
- "monthly_cap_ntd": <數字或 null，這是「加碼回饋」每月或每期的封頂回饋金額(台幣)。
    注意：此欄位「只」是加碼回饋的上限。基礎回饋永遠無上限。
    若加碼無上限填 null。
    若 bonus_rate 為 0.0（即只有基礎回饋），此欄位必須填 null。>

嚴格規則：
1. 嚴格遵守使用者的限制條件（例如「忽略新戶加碼」、「舊戶身分」）。
2. 若網頁上寫「最高 5% (含基本 1% + 加碼 4%)」，請拆分為 base_rate: 1.0, bonus_rate: 4.0。
3. 若某個優惠活動在網頁上明確標示「已額滿」、「登錄已額滿」、「名額已滿」，請完全不要列出該活動。
4. 若該卡有多種加碼方案可疊加，請分成多筆記錄（不同的 channel_name）。
5. 「國外交易服務費」或「海外手續費」是銀行向持卡人收取的費用（通常 1.5%），不是回饋。如果網頁提到「免收國外交易服務費」或「回饋抵海外手續費」，請將其列為獨立一筆，channel_name 寫明「國外交易手續費減免」，base_rate: 0, bonus_rate: 1.5, monthly_cap_ntd 依網頁說明填入。不要將其與消費回饋混合計算。
6. 使用者已經設定所有信用卡為「帳戶自動轉帳扣繳 + 電子帳單」，因此符合所有需要「設定自動扣繳」或「電子帳單」的加碼條件。
7. channel_name 中的具體商家/通路名稱請盡量完整列出，這對後續的消費比對至關重要。例如不要只寫「指定網購」，而要寫「蝦皮/momo/PChome/酷澎」。如果通路太多（超過 10 個），可以列出前 8 個最常見的，再加「等」。
8. 不要列出「JCB APP 限定活動」或「需透過特定 APP（如 MyJapan+）登錄」的活動。這類活動由系統另行處理。
9. 如果某個優惠活動需要事先登錄（例如「需登錄」、「需至官網登錄」、「每半年登錄」），請在 channel_name 的末尾加上「(需登錄)」標記。例如：「日本指定商店(需登錄)」。這是系統用來區分已登錄/未登錄活動的依據，非常重要。
"""

async def fetch_webpage_text(url: str) -> str:
    """抓取網頁並提取純文字"""
    async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 移除 script, style, header, footer 等非內容標籤
        for script in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            script.extract()

        text = soup.get_text(separator='\n')
        # 簡單清理多餘空白
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        # 限制字數，避免超過 prompt 限制
        return text[:15000]


async def fetch_multiple_pages(urls: list[str]) -> str:
    """抓取多個網頁並合併純文字"""
    all_text = []
    for url in urls:
        try:
            text = await fetch_webpage_text(url)
            all_text.append(f"=== 來源: {url} ===\n{text}")
        except Exception as e:
            all_text.append(f"=== 來源: {url} === (抓取失敗: {e})")
    return "\n\n".join(all_text)


async def scrape_card_benefits(card_name: str, url, instructions: str, api_key: Optional[str] = None) -> List[ScrapedBenefit]:
    """
    爬取卡片頁面並透過 AI 萃取權益。
    url 可以是單一字串或字串列表（多頁合併爬取）。
    """
    key = api_key
    if not key:
        from app.core.config import settings
        key = settings.GEMINI_API_KEY
    if not key:
        raise ValueError("GEMINI_API_KEY is not set.")

    try:
        if isinstance(url, list):
            page_text = await fetch_multiple_pages(url)
        else:
            page_text = await fetch_webpage_text(url)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

    client = genai.Client(api_key=key)

    url_display = url if isinstance(url, str) else ", ".join(url)
    user_prompt = f"""
卡片名稱：{card_name}
網址：{url_display}
使用者專屬條件：{instructions}

以下是從網頁抓取到的文字內容：
-------------------
{page_text}
-------------------
請輸出符合要求的 JSON Array：
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                types.Content(parts=[
                    types.Part(text=GEMINI_SYSTEM_PROMPT),
                    types.Part(text=user_prompt)
                ])
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        raw = response.text.strip()
        raw = re.sub(r"^```[a-z]*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        parsed_list = json.loads(raw)
        results = []
        for item in parsed_list:
            results.append(ScrapedBenefit(**item))

        return results
    except Exception as e:
        print(f"AI 解析失敗 ({card_name}): {e}")
        return []
