import asyncio
from app.db.database import AsyncSessionLocal
from app.models.cards import Card
from app.models.card_benefits import CardBenefit
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Card).where(Card.card_name.like('%Unicard%')))
        card = res.scalar_one_or_none()
        if card:
            print(f"Card: {card.bank_name} {card.card_name}")
            res2 = await session.execute(select(CardBenefit).where(CardBenefit.card_id == card.id))
            for b in res2.scalars():
                print(f"- {b.channel_name} (Base: {b.base_rate}%, Bonus: {b.bonus_rate}%)")
        else:
            print("Unicard not found")

if __name__ == "__main__":
    asyncio.run(main())
