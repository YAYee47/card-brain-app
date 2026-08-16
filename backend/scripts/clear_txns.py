import asyncio
from app.db.database import AsyncSessionLocal
from app.models.transactions import Transaction
from app.models.monthly_usage import MonthlyUsage
from sqlalchemy import delete

async def clear_db():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Transaction))
        await session.execute(delete(MonthlyUsage))
        await session.commit()
        print("Database cleared.")

if __name__ == "__main__":
    asyncio.run(clear_db())
