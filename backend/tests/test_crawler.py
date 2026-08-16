import asyncio
import os
import json
from datetime import datetime
from app.db.seed import INITIAL_CARDS
from app.services.ai_crawler import scrape_card_benefits
from dotenv import load_dotenv

load_dotenv()

# Instructions map per card name
INSTRUCTIONS = {
    "DAWHO現金回饋信用卡": "使用者為舊戶，且符合大戶資格。",
    "現金回饋JCB卡": "使用者為舊戶。",
    "幣倍卡": "使用者為舊戶，持有日幣雙幣卡，且符合大戶資格。",
    "DAWAY卡": "使用者為舊戶，且符合 DAWAY GO 資格。",
    "Unicard": "使用者為舊戶，使用方案2『任意選』。當月需消費超過14900元才建議『UP選』。不須擔心玉山e point餘額問題。",
    "熊本熊卡": "使用者為舊戶，持有『熊本熊日圓雙幣卡(向左左那張)』。請特別標註每半年登錄活動(1/1, 7/1)。",
    "Richart 卡": "使用者為舊戶，有 VISA 與 Master 各一張。權益需列出可手動切換的(Pay著刷、天天刷、大筆刷、好饗刷等)。",
    "傳說對決聯名卡": "使用者為舊戶。",
    "吉鶴卡": "使用者為舊戶。"
}

async def main():
    print("Starting AI Crawl Preview...")
    
    # Check for JCB card
    jcb_url = "https://www.specialoffers.jcb/zh-tw/"
    
    with open('crawler_preview.md', 'w', encoding='utf-8') as f:
        f.write("# 爬蟲測試報告 (AI 解析預覽)\n")
        f.write(f"時間: {datetime.now()}\n\n")
        
        for c in INITIAL_CARDS:
            card_name = c["card_name"]
            url = c.get("benefit_url")
            print(f"Scraping {card_name}...")
            
            if not url:
                f.write(f"## {card_name}\n- 缺少網址，跳過。\n\n")
                continue
                
            urls_to_scrape = [url]
            if card_name == "熊本熊卡":
                urls_to_scrape.append(jcb_url)
                
            instructions = INSTRUCTIONS.get(card_name, "使用者為舊戶。")
            benefits = await scrape_card_benefits(card_name, urls_to_scrape, instructions)
            
            f.write(f"## {card_name}\n")
            f.write(f"- **網址**: {url}\n")
            f.write(f"- **解析條件**: {instructions}\n\n")
            
            if not benefits:
                f.write("- (無資料或解析失敗)\n\n")
            else:
                f.write("| 通路名稱 | 基礎回饋(%) | 加碼回饋(%) | 加碼上限(元) |\n")
                f.write("|---|---|---|---|\n")
                for b in benefits:
                    cap = b.monthly_cap_ntd if b.monthly_cap_ntd is not None else "無上限"
                    f.write(f"| {b.channel_name} | {b.base_rate} | {b.bonus_rate} | {cap} |\n")
            f.write("\n")
            
            await asyncio.sleep(8)
            
    print("Preview dumped to crawler_preview.md")

if __name__ == "__main__":
    asyncio.run(main())
