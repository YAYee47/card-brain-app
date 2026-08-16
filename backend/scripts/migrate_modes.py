import asyncio
import sqlite3
import json
from app.db.database import AsyncSessionLocal
from app.models.cards import Card
from app.models.card_benefits import CardBenefit
from sqlalchemy import select

def apply_schema_changes():
    print("Applying schema changes via sqlite3...")
    conn = sqlite3.connect("card_brain.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE cards ADD COLUMN mode_config TEXT;")
    except Exception as e:
        print("cards table already has mode_config:", e)

    try:
        cursor.execute("ALTER TABLE card_benefits ADD COLUMN required_mode VARCHAR(50);")
    except Exception as e:
        print("card_benefits table already has required_mode:", e)
        
    try:
        cursor.execute("ALTER TABLE transactions ADD COLUMN card_mode VARCHAR(50);")
    except Exception as e:
        print("transactions table already has card_mode:", e)
    
    conn.commit()
    conn.close()
    print("Schema changes applied.")

async def update_unicard_data():
    print("Updating Unicard data...")
    async with AsyncSessionLocal() as session:
        # Find Unicard
        res = await session.execute(select(Card).where(Card.card_name.like('%Unicard%')))
        card = res.scalar_one_or_none()
        if not card:
            print("Unicard not found.")
            return

        # Update mode_config
        mode_cfg = {
            "modes": ["簡單選", "任意選", "UP選"],
            "scope": "monthly"
        }
        card.mode_config = json.dumps(mode_cfg, ensure_ascii=False)
        
        # Find and update its benefits
        res2 = await session.execute(select(CardBenefit).where(CardBenefit.card_id == card.id))
        benefits = res2.scalars().all()
        for b in benefits:
            if "簡單選" in b.channel_name:
                b.required_mode = "簡單選"
            elif "任意選" in b.channel_name:
                b.required_mode = "任意選"
            elif "UP選" in b.channel_name:
                b.required_mode = "UP選"
        
        await session.commit()
        print("Unicard data updated.")

if __name__ == "__main__":
    apply_schema_changes()
    asyncio.run(update_unicard_data())
