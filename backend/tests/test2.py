import asyncio
from app.db.database import AsyncSessionLocal
from app.models.cards import Card
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Card))
        for c in res.scalars():
            if '傳說' in c.card_name:
                print(f"ID: {c.id}, Bank: {c.bank_name}, Name: {c.card_name}")

if __name__ == "__main__":
    asyncio.run(main())
