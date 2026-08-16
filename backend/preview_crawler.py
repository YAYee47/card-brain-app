import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from app.services.ai_crawler import scrape_card_benefits
from app.core.card_profiles import CARD_PROFILES, JCB_SPECIAL_OFFERS

async def main():
    output_lines = ["# 💳 AI 爬蟲全卡片權益預覽\n\n"]
    
    # 處理所有卡片
    for profile in CARD_PROFILES:
        bank = profile['bank_name']
        card = profile['card_name']
        print(f"Scraping {bank} - {card}...")
        
        output_lines.append(f"## {bank} {card}")
        try:
            benefits = await scrape_card_benefits(
                profile["card_name"], 
                profile["url"], 
                profile["instructions"]
            )
            
            if not benefits:
                output_lines.append("> ⚠️ **無法解析或無資料**\n")
            else:
                output_lines.append("| 通路 / 條件 | 基礎回饋 (%) | 加碼回饋 (%) | 每月/每期上限 (NTD) |")
                output_lines.append("|-------------|--------------|--------------|-------------------|")
                for b in benefits:
                    cap = b.monthly_cap_ntd if b.monthly_cap_ntd is not None else "無上限"
                    output_lines.append(f"| {b.channel_name} | {b.base_rate}% | {b.bonus_rate}% | {cap} |")
        except Exception as e:
            output_lines.append(f"> ❌ **執行發生錯誤**: `{e}`\n")
        
        output_lines.append("\n")
        
    # 處理 JCB
    print("Scraping JCB Special Offers...")
    output_lines.append("## JCB 組織通用優惠 (套用於所有 JCB 卡)")
    try:
        benefits = await scrape_card_benefits(
            "JCB 組織優惠", 
            JCB_SPECIAL_OFFERS["url"], 
            JCB_SPECIAL_OFFERS["instructions"]
        )
        if not benefits:
            output_lines.append("> ⚠️ **無法解析或無資料**\n")
        else:
            output_lines.append("| 通路 / 條件 | 基礎回饋 (%) | 加碼回饋 (%) | 每月/每期上限 (NTD) |")
            output_lines.append("|-------------|--------------|--------------|-------------------|")
            for b in benefits:
                cap = b.monthly_cap_ntd if b.monthly_cap_ntd is not None else "無上限"
                output_lines.append(f"| {b.channel_name} | {b.base_rate}% | {b.bonus_rate}% | {cap} |")
    except Exception as e:
        output_lines.append(f"> ❌ **執行發生錯誤**: `{e}`\n")

    # 寫出到 Markdown
    out_path = r"C:\Users\kitty\.gemini\antigravity\brain\3b155dd8-6857-4c93-8133-76e96b302a72\crawler_preview.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    print(f"Report generated at: {out_path}")

if __name__ == "__main__":
    asyncio.run(main())
