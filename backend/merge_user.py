import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_IW1dt5pAgyFU@ep-aged-moon-aznivm4q.c-3.ap-southeast-1.aws.neon.tech/neondb"

async def merge():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Delete empty new user 3
        await conn.execute(text("DELETE FROM users WHERE id = 3"))
        # Update user 1 device_uuid to the iPhone's uuid
        await conn.execute(text("UPDATE users SET device_uuid = '03902712-e60b-47b8-8480-e55851a6ceb3' WHERE id = 1"))
        print("Successfully merged User 1 with iPhone device UUID and deleted duplicate User 3!")

asyncio.run(merge())
