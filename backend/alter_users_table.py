import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_IW1dt5pAgyFU@ep-aged-moon-aznivm4q.c-3.ap-southeast-1.aws.neon.tech/neondb"

async def alter_table():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)"))
        print("Column password_hash added successfully!")

asyncio.run(alter_table())
