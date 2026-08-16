import asyncio

from app.api.v1.endpoints import recommend as recommend_endpoint
from app.schemas.recommend import RecommendRequest
from app.services.recommend import RecommendedCard


def _rec(
    user_card_id,
    card_id,
    channel_name,
    total,
    is_capped,
):
    return RecommendedCard(
        user_card_id=user_card_id,
        card_id=card_id,
        bank_name="Bank",
        card_name=f"Card {card_id}",
        billing_cycle_date=10,
        channel_name=channel_name,
        base_rate=1.0,
        bonus_rate=2.0,
        monthly_cap_ntd=None,
        used_amount_ntd=0.0,
        remaining_cap_ntd=None,
        estimated_base_cashback=1.0,
        estimated_bonus_cashback=2.0,
        estimated_total_cashback=total,
        is_capped=is_capped,
    )


def test_recommend_endpoint_maps_results_and_top_cards(monkeypatch):
    calls = []

    async def _fake_get_recommendations(db, amount, channel_name, exclude_registration=False):
        calls.append((db, amount, channel_name, exclude_registration))
        if exclude_registration:
            return [
                _rec(1, 101, "LINE Pay 國內", 10.0, False),
                _rec(2, 102, "LINE Pay 備選", 8.0, False),
            ]
        return [_rec(3, 103, "LINE Pay 含登錄", 12.0, False)]

    monkeypatch.setattr(recommend_endpoint, "get_recommendations", _fake_get_recommendations)

    payload = RecommendRequest(amount=1234.0, channel_name="LINE Pay")
    db = object()

    result = asyncio.run(recommend_endpoint.recommend_card(payload, db=db))

    assert len(calls) == 2
    assert calls[0] == (db, 1234.0, "LINE Pay", True)
    assert calls[1] == (db, 1234.0, "LINE Pay", False)

    assert result.amount == 1234.0
    assert result.channel_name == "LINE Pay"

    assert len(result.results) == 2
    assert result.top_card is not None
    assert result.top_card.user_card_id == 1
    assert result.top_card.channel_name == "LINE Pay 國內"

    assert len(result.results_with_registration) == 1
    assert result.top_card_with_registration is not None
    assert result.top_card_with_registration.user_card_id == 3
    assert result.top_card_with_registration.channel_name == "LINE Pay 含登錄"


def test_recommend_endpoint_handles_empty_lists(monkeypatch):
    async def _fake_get_recommendations(_db, _amount, _channel_name, _exclude_registration=False):
        return []

    monkeypatch.setattr(recommend_endpoint, "get_recommendations", _fake_get_recommendations)

    payload = RecommendRequest(amount=500.0, channel_name="國內一般消費")
    result = asyncio.run(recommend_endpoint.recommend_card(payload, db=object()))

    assert result.results == []
    assert result.results_with_registration == []
    assert result.top_card is None
    assert result.top_card_with_registration is None


def test_list_channels_returns_supported_channels():
    result = asyncio.run(recommend_endpoint.list_channels())
    assert result == recommend_endpoint.SUPPORTED_CHANNELS
