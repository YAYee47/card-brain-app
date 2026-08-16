import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
import sys
import os

# 確保能讀取到 app module
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from models.cards import Card
from models.card_benefits import CardBenefit

async def export_data():
    engine = create_async_engine("sqlite+aiosqlite:///./card_brain.db", echo=False)
    Session = async_sessionmaker(bind=engine)
    
    data = {"cards": [], "card_benefits": []}
    
    async with Session() as session:
        cards_res = await session.execute(select(Card))
        for c in cards_res.scalars().all():
            data["cards"].append({
                "id": c.id,
                "bank_name": c.bank_name,
                "card_name": c.card_name,
                "card_image_url": c.card_image_url,
                "base_reward_rate": c.base_reward_rate,
                "base_reward_type": c.base_reward_type,
                "mode_config": c.mode_config
            })
            
        benefits_res = await session.execute(select(CardBenefit))
        for b in benefits_res.scalars().all():
            data["card_benefits"].append({
                "id": b.id,
                "card_id": b.card_id,
                "category": b.category,
                "channel_keywords": b.channel_keywords,
                "reward_rate": b.reward_rate,
                "reward_type": b.reward_type,
                "monthly_cap": float(b.monthly_cap) if b.monthly_cap else None,
                "cap_type": b.cap_type,
                "description": b.description,
                "effective_date": b.effective_date.isoformat() if b.effective_date else None,
                "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None,
                "required_mode": b.required_mode
            })
            
    with open("seed_backup.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("Exported backup to seed_backup.json")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(export_data())
