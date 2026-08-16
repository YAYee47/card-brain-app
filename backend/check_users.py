import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_IW1dt5pAgyFU@ep-aged-moon-aznivm4q.c-3.ap-southeast-1.aws.neon.tech/neondb"

async def check():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        users = (await conn.execute(text("SELECT id, nickname, device_uuid, is_guest, created_at FROM users"))).fetchall()
        print(f"Total {len(users)} Users in DB:")
        for u in users:
            print(" - User:", u)
            ucs = (await conn.execute(text(f"SELECT id, card_id FROM user_cards WHERE user_id = {u[0]}"))).fetchall()
            txs = (await conn.execute(text(f"SELECT id, original_amount, merchant_name FROM transactions WHERE user_id = {u[0]}"))).fetchall()
            print(f"   --> Cards: {len(ucs)}, Transactions: {len(txs)}")

asyncio.run(check())
