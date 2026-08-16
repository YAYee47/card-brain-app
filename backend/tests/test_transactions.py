import pytest
import asyncio
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.transactions import Transaction
# We will use mock objects to avoid needing actual DB models for unit tests of the calculation logic
from app.services.transaction_service import calculate_txn_cashback

class _DummyExecuteResult:
    def __init__(self, item):
        self._item = item
    def scalar_one_or_none(self):
        return self._item

class _FakeAsyncSession:
    def __init__(self, usage_results):
        self.usage_results = usage_results
        self.added_items = []
        
    async def execute(self, _query):
        res = self.usage_results.pop(0) if self.usage_results else None
        return _DummyExecuteResult(res)
        
    def add(self, item):
        self.added_items.append(item)

def _benefit(id, channel_name, base_rate, bonus_rate, monthly_cap_ntd=None, required_mode=None):
    return SimpleNamespace(
        id=id,
        channel_name=channel_name,
        base_rate=base_rate,
        bonus_rate=bonus_rate,
        monthly_cap_ntd=monthly_cap_ntd,
        required_mode=required_mode
    )

def _transaction(amount, channel_name, mode=None):
    return SimpleNamespace(
        ntd_amount=amount,
        channel_name=channel_name,
        card_mode=mode,
        transacted_at=datetime(2026, 8, 15),
        earned_cashback_ntd=0.0
    )

def _user_card(id=1, billing_cycle_date=1):
    return SimpleNamespace(
        id=id,
        billing_cycle_date=billing_cycle_date
    )

def _usage(used_amount, earned_cashback):
    return SimpleNamespace(
        used_amount_ntd=used_amount,
        earned_cashback_ntd=earned_cashback
    )

@pytest.mark.asyncio
async def test_calculate_txn_cashback_generic_match():
    benefits = [
        _benefit(2, "國內一般消費", 1.0, 0.0)
    ]
    txn = _transaction(1000, "UnknownStore")
    uc = _user_card()
    session = _FakeAsyncSession([])
    
    result = await calculate_txn_cashback(txn, uc, benefits, session)
    assert result.earned_cashback_ntd == 10.0

@pytest.mark.asyncio
async def test_calculate_txn_cashback_lakole():
    benefits = [
        _benefit(1, "嚴選日系名店 (UNIQLO、GU、大創)", 1.0, 4.0, 500)
    ]
    txn = _transaction(1000, "Lakole")
    uc = _user_card()
    session = _FakeAsyncSession([None])
    
    result = await calculate_txn_cashback(txn, uc, benefits, session)
    assert result.earned_cashback_ntd == 50.0  # 1% base + 4% bonus = 5% = 50

@pytest.mark.asyncio
async def test_calculate_txn_cashback_app_store():
    benefits = [
        _benefit(1, "App Store (設定自動扣繳)", 1.0, 9.0, 500)
    ]
    txn = _transaction(100, "App Store")
    uc = _user_card()
    session = _FakeAsyncSession([None])
    
    result = await calculate_txn_cashback(txn, uc, benefits, session)
    assert result.earned_cashback_ntd == 10.0  # 1% base + 9% bonus = 10% = 10
    assert len(session.added_items) == 1

@pytest.mark.asyncio
async def test_calculate_txn_cashback_specific_match_with_cap():
    # 測試加碼達上限的情況 (回饋金上限 500，加碼 5% => 額度 10000)
    db = _FakeAsyncSession([_usage(9000, 450)]) # 已經用掉 9000
    txn = _transaction(2000, "LINE Pay")
    uc = _user_card()
    benefits = [
        _benefit(1, "國內一般消費", 1.0, 0.0),
        _benefit(2, "LINE Pay", 1.0, 5.0, monthly_cap_ntd=500.0)
    ]
    
    result = await calculate_txn_cashback(txn, uc, benefits, db)
    
    # 刷 2000，基本 1% = 20
    # 加碼 5%，剩餘額度 = 10000 - 9000 = 1000。
    # 只有 1000 享加碼 5% = 50。
    # 總回饋 = 20 + 50 = 70。
    assert result.earned_cashback_ntd == 70.0

@pytest.mark.asyncio
async def test_calculate_txn_cashback_required_mode():
    db = _FakeAsyncSession([None, None])
    txn_mode1 = _transaction(1000, "日本", mode="MODE1")
    txn_mode2 = _transaction(1000, "日本", mode="MODE2")
    uc = _user_card()
    benefits = [
        _benefit(1, "日本", 1.0, 5.0, required_mode="MODE1"),
        _benefit(2, "日本", 1.0, 8.0, required_mode="MODE2")
    ]
    
    res1 = await calculate_txn_cashback(txn_mode1, uc, benefits, db)
    assert res1.earned_cashback_ntd == 60.0 # 1000 * 6%
    
    res2 = await calculate_txn_cashback(txn_mode2, uc, benefits, db)
    assert res2.earned_cashback_ntd == 90.0 # 1000 * 9%
