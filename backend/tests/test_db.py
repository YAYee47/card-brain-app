import asyncio
from app.db.database import AsyncSessionLocal
from app.models.card_benefits import CardBenefit
from app.models.cards import Card
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Card).where(Card.card_name.like('%傳說對決%')))
        card = res.scalar_one_or_none()
        if card:
            res2 = await session.execute(select(CardBenefit).where(CardBenefit.card_id == card.id))
            for b in res2.scalars():
                print(f"Channel: {b.channel_name}, Base: {b.base_rate}, Bonus: {b.bonus_rate}")
        else:
            print("Card not found")

if __name__ == "__main__":
    asyncio.run(main())
