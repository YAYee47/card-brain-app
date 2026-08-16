import asyncio
from app.db.database import AsyncSessionLocal
from app.models.card_benefits import CardBenefit
from app.models.cards import Card
from sqlalchemy import select, delete

async def main():
    async with AsyncSessionLocal() as session:
        # Get Unicard ID
        res = await session.execute(select(Card).where(Card.card_name.like('%Unicard%')))
        unicard = res.scalar_one_or_none()
        if not unicard:
            print("Unicard not found")
            return
            
        print(f"Unicard ID: {unicard.id}")
        
        # Get all benefits for Unicard
        res = await session.execute(select(CardBenefit).where(CardBenefit.card_id == unicard.id))
        benefits = res.scalars().all()
        
        for b in benefits:
            print(f"ID: {b.id}, Channel: {b.channel_name}")
            
        # Delete specific ones like "蝦皮購物 (UP選)", "LINE Pay (任意選)"
        # Keep the long string "百大指定消費-UP選方案..." and "國內一般消費", "國外"
        # We can delete any where channel_name contains "UP選" or "任意選" or "簡單選"
        # EXCEPT if it starts with "百大指定消費"
        to_delete = []
        for b in benefits:
            if "選" in b.channel_name and not b.channel_name.startswith("百大指定消費"):
                to_delete.append(b.id)
                
        if to_delete:
            print(f"Deleting {len(to_delete)} redundant specific records...")
            await session.execute(delete(CardBenefit).where(CardBenefit.id.in_(to_delete)))
            await session.commit()
            print("Deleted successfully.")
        else:
            print("No redundant records found.")

if __name__ == "__main__":
    asyncio.run(main())
