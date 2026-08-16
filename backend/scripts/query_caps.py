import asyncio
from app.db.database import AsyncSessionLocal
from app.models.card_benefits import CardBenefit
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CardBenefit))
        benefits = result.scalars().all()
        for b in benefits:
            if b.monthly_cap_ntd is not None:
                print(f"Card {b.card_id} | {b.channel_name} | Base: {b.base_rate} | Bonus: {b.bonus_rate} | Cap: {b.monthly_cap_ntd}")

if __name__ == "__main__":
    asyncio.run(main())
