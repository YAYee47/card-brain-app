import asyncio
from app.db.database import AsyncSessionLocal
from app.models.card_benefits import CardBenefit
from app.models.cards import Card
from sqlalchemy import select

async def f():
    async with AsyncSessionLocal() as s:
        res = await s.execute(select(Card).where(Card.card_name.like('%Unicard%')))
        card = res.scalar_one_or_none()
        r = await s.execute(select(CardBenefit).where(CardBenefit.card_id==card.id))
        for b in r.scalars():
            print(f"Name: {b.channel_name}, Mode: {b.required_mode}")

asyncio.run(f())
