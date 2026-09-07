import pytest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from app.api.v1.endpoints.transactions import _parse_filter_date, list_transactions

def test_parse_filter_date():
    assert _parse_filter_date(None) is None
    assert _parse_filter_date("") is None
    assert _parse_filter_date("invalid-date") is None
    
    # 10 chars YYYY-MM-DD
    d1 = _parse_filter_date("2026-08-01")
    assert d1 == datetime(2026, 8, 1)
    
    # 19 chars YYYY-MM-DD HH:MM:SS
    d2 = _parse_filter_date("2026-08-31 23:59:59")
    assert d2 == datetime(2026, 8, 31, 23, 59, 59)
    
    # ISO format with T and Z
    d3 = _parse_filter_date("2026-08-15T12:30:00Z")
    assert d3 == datetime(2026, 8, 15, 12, 30, 0)


@pytest.mark.anyio
async def test_list_transactions_date_filtering():
    # 建立假交易資料
    mock_txns = [
        SimpleNamespace(
            id=1,
            user_id=1,
            user_card_id=1,
            channel_name="Apple Pay",
            category="餐飲",
            merchant_name="星巴克",
            original_amount=150.0,
            currency="TWD",
            ntd_amount=150.0,
            exchange_rate=1.0,
            earned_cashback_ntd=5.0,
            source_type="MANUAL",
            transacted_at=datetime(2026, 8, 15, 14, 0, 0),
        )
    ]

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = mock_txns

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    current_user = SimpleNamespace(id=1)

    # 測試帶入 8 月日期區間
    results = await list_transactions(
        db=mock_db,
        current_user=current_user,
        start_date="2026-08-01 00:00:00",
        end_date="2026-08-31 23:59:59",
    )

    assert len(results) == 1
    assert results[0].merchant_name == "星巴克"
    assert results[0].ntd_amount == 150.0
    mock_db.execute.assert_called_once()
