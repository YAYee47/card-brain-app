import asyncio
from datetime import datetime
from app.db.database import AsyncSessionLocal
from app.models.user_cards import UserCard
from app.models.cards import Card
from app.schemas.transactions import TransactionCreate
from app.api.v1.endpoints.transactions import create_transaction
from app.models.transactions import Transaction
from sqlalchemy import select, delete

async def main():
    async with AsyncSessionLocal() as db:
        print("1. Cleaning up transactions...")
        await db.execute(delete(Transaction))
        await db.commit()

        print("2. Finding Unicard user_card...")
        res = await db.execute(
            select(UserCard).join(Card).where(Card.card_name.like('%Unicard%'))
        )
        user_card = res.scalar_one_or_none()
        if not user_card:
            print("Unicard UserCard not found. Run init_db and onboard first.")
            return
        
        print("3. Creating Transaction on Aug 3 (任意選)...")
        payload1 = TransactionCreate(
            user_card_id=user_card.id,
            channel_name="momo購物",
            category="娛樂",
            merchant_name="Apple",
            original_amount=1000,
            currency="TWD",
            source_type="MANUAL",
            card_mode="任意選",
            transacted_at="2026-08-03T10:00:00"
        )
        txn1 = await create_transaction(payload1, db)
        print(f"  -> txn1 created: Mode={txn1.card_mode}, Cashback={txn1.earned_cashback_ntd}")
        
        print("4. Creating Transaction on Aug 18 (UP選)...")
        payload2 = TransactionCreate(
            user_card_id=user_card.id,
            channel_name="momo購物",
            category="娛樂",
            merchant_name="Apple",
            original_amount=2000,
            currency="TWD",
            source_type="MANUAL",
            card_mode="UP選",
            transacted_at="2026-08-18T10:00:00"
        )
        txn2 = await create_transaction(payload2, db)
        print(f"  -> txn2 created: Mode={txn2.card_mode}, Cashback={txn2.earned_cashback_ntd}")
        
        print("5. Verifying retroactive update on txn1...")
        res = await db.execute(select(Transaction).where(Transaction.id == txn1.id))
        txn1_updated = res.scalar_one()
        print(f"  -> txn1 updated: Mode={txn1_updated.card_mode}, Cashback={txn1_updated.earned_cashback_ntd}")
        
        if txn1_updated.card_mode == "UP選" and txn1_updated.earned_cashback_ntd == 45.0:
            print("SUCCESS! Retroactive update works correctly.")
        else:
            print("FAILED! Retroactive update failed.")

if __name__ == "__main__":
    asyncio.run(main())
