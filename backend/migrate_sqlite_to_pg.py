import asyncio
import sqlite3
from datetime import datetime, date
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.db.database import Base
from app.models import users, cards, card_benefits, user_cards, transactions, monthly_usage, alerts

NEON_URL = "postgresql+asyncpg://neondb_owner:npg_IW1dt5pAgyFU@ep-aged-moon-aznivm4q.c-3.ap-southeast-1.aws.neon.tech/neondb"

def parse_date(val):
    if not val:
        return None
    if isinstance(val, date):
        return val
    try:
        return datetime.strptime(val[:10], "%Y-%m-%d").date()
    except:
        return None

def parse_datetime(val):
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    try:
        # Handle '2026-08-15 00:00:00.000000' or '2026-08-15 19:01:24' or ISO
        clean_val = val.replace("T", " ")
        if "." in clean_val:
            return datetime.strptime(clean_val[:26], "%Y-%m-%d %H:%M:%S.%f")
        return datetime.strptime(clean_val[:19], "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return None

async def migrate():
    print("1. Connecting to Neon PostgreSQL...")
    engine = create_async_engine(NEON_URL, echo=False)
    
    print("2. Re-creating tables in PostgreSQL...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("   Tables created successfully.")
    
    print("3. Reading data from SQLite backup (card_brain_backup.db)...")
    s_conn = sqlite3.connect("card_brain_backup.db")
    s_conn.row_factory = sqlite3.Row
    s_cur = s_conn.cursor()
    
    tables = [
        "users",
        "cards",
        "card_benefits",
        "user_cards",
        "transactions",
        "monthly_usage",
        "app_alerts"
    ]
    
    async with engine.begin() as conn:
        for tbl in tables:
            try:
                s_cur.execute(f"SELECT * FROM {tbl}")
                rows = s_cur.fetchall()
                if not rows:
                    print(f"   Table {tbl}: 0 rows.")
                    continue
                
                cols = list(rows[0].keys())
                col_names = ", ".join(cols)
                placeholders = ", ".join([f":{col}" for col in cols])
                insert_stmt = text(f"INSERT INTO {tbl} ({col_names}) VALUES ({placeholders})")
                
                records = []
                for row in rows:
                    r = dict(row)
                    # Convert types based on table and columns
                    for k, v in r.items():
                        if k in ("is_active", "is_resolved", "is_guest", "is_capped", "is_warning") or k.startswith("is_"):
                            r[k] = bool(v) if v is not None else False
                        elif k in ("effective_date", "expiry_date", "cycle_start_date", "cycle_end_date"):
                            r[k] = parse_date(v)
                        elif k in ("created_at", "updated_at", "transacted_at", "last_synced_at"):
                            r[k] = parse_datetime(v)
                    records.append(r)
                
                await conn.execute(insert_stmt, records)
                print(f"   Successfully migrated {len(records)} rows into {tbl}.")
                
                # Fix PostgreSQL auto-increment sequence
                if "id" in cols:
                    try:
                        seq_query = text(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), coalesce(max(id), 1), max(id) IS NOT NULL) FROM {tbl};")
                        await conn.execute(seq_query)
                    except Exception as e:
                        pass
            except Exception as ex:
                print(f"   Error migrating {tbl}: {ex}")
                raise ex
                
    s_conn.close()
    await engine.dispose()
    print("Migration to Neon PostgreSQL completed with 100% SUCCESS!")

if __name__ == "__main__":
    asyncio.run(migrate())
