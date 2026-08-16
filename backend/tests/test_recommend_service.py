import asyncio
from types import SimpleNamespace

import app.models.alerts  # noqa: F401
from app.services import recommend as recommend_service


class _DummyScalars:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class _DummyExecuteResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return _DummyScalars(self._items)


class _FakeAsyncSession:
    def __init__(self, execute_results):
        self._execute_results = list(execute_results)

    async def execute(self, _query):
        if not self._execute_results:
            raise AssertionError("Unexpected db.execute call")
        return _DummyExecuteResult(self._execute_results.pop(0))


def _benefit(benefit_id, channel_name, base_rate=1.0, bonus_rate=0.0, monthly_cap_ntd=None):
    return SimpleNamespace(
        id=benefit_id,
        channel_name=channel_name,
        base_rate=base_rate,
        bonus_rate=bonus_rate,
        monthly_cap_ntd=monthly_cap_ntd,
    )


def _user_card(user_card_id, card_id, benefits, billing_cycle_date=10):
    card = SimpleNamespace(
        id=card_id,
        bank_name="Test Bank",
        card_name=f"Card {card_id}",
        benefits=benefits,
    )
    return SimpleNamespace(id=user_card_id, billing_cycle_date=billing_cycle_date, card=card)


def _usage(benefit_id, used_amount_ntd):
    return SimpleNamespace(card_benefit_id=benefit_id, used_amount_ntd=used_amount_ntd)


def _run_get_recommendations(db, amount, channel_name, exclude_registration=False):
    return asyncio.run(
        recommend_service.get_recommendations(
            db,
            amount,
            channel_name,
            exclude_registration=exclude_registration,
        )
    )


def test_no_active_cards_returns_empty_list():
    db = _FakeAsyncSession([[]])
    result = _run_get_recommendations(db, amount=1000, channel_name="LINE Pay")
    assert result == []


def test_exclude_registration_filters_registration_benefit_and_can_return_empty(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    uc = _user_card(
        1,
        101,
        [_benefit(1, "LINE Pay(需登錄)", base_rate=1.0, bonus_rate=6.0)],
    )

    db_include = _FakeAsyncSession([[uc], []])
    included = _run_get_recommendations(db_include, 1000, "line pay", exclude_registration=False)
    assert len(included) == 1
    assert included[0].channel_name == "LINE Pay(需登錄)"

    db_exclude = _FakeAsyncSession([[uc]])
    excluded = _run_get_recommendations(db_exclude, 1000, "line pay", exclude_registration=True)
    assert excluded == []


def test_uber_eats_input_does_not_match_uber_benefit(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefits = [
        _benefit(1, "Uber Eats 加碼", base_rate=1.0, bonus_rate=9.0),
        _benefit(2, "Uber 交通加碼", base_rate=1.0, bonus_rate=12.0),
    ]
    uc = _user_card(1, 101, benefits)
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, 1000, "uber eats")
    assert len(result) == 1
    assert result[0].channel_name == "Uber Eats 加碼"


def test_uber_input_excludes_uber_eats_benefit(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefits = [
        _benefit(1, "Uber Eats 加碼", base_rate=1.0, bonus_rate=10.0),
        _benefit(2, "Uber 交通加碼", base_rate=1.0, bonus_rate=5.0),
    ]
    uc = _user_card(1, 101, benefits)
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, 1000, "uber")
    assert len(result) == 1
    assert result[0].channel_name == "Uber 交通加碼"


def test_line_pay_excludes_overseas_labels(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefits = [
        _benefit(1, "LINE Pay 海外加碼", base_rate=1.0, bonus_rate=10.0),
        _benefit(2, "LINE Pay 國內加碼", base_rate=1.0, bonus_rate=4.0),
    ]
    uc = _user_card(1, 101, benefits)
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, 500, "line pay")
    assert len(result) == 1
    assert result[0].channel_name == "LINE Pay 國內加碼"


def test_traffic_excludes_japan_card_without_japan_keywords(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefits = [
        _benefit(1, "日本三大交通卡 8%", base_rate=1.0, bonus_rate=8.0),
        _benefit(2, "交通 通用加碼", base_rate=1.0, bonus_rate=2.0),
    ]
    uc = _user_card(1, 101, benefits)
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, 600, "交通")
    assert len(result) == 1
    assert result[0].channel_name == "交通 通用加碼"


def test_traffic_allows_japan_card_with_suica_keyword(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefits = [_benefit(1, "日本三大交通卡 8%", base_rate=1.0, bonus_rate=8.0)]
    uc = _user_card(1, 101, benefits)
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, 600, "suica 交通卡")
    assert len(result) == 1
    assert result[0].channel_name == "日本三大交通卡 8%"


def test_dedupe_keeps_shortest_channel_name_for_same_rate_and_cap(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", ["蝦皮"])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefits = [
        _benefit(1, "百大指定消費-UP選蝦皮購物加碼", base_rate=1.0, bonus_rate=4.0, monthly_cap_ntd=200),
        _benefit(2, "蝦皮購物", base_rate=1.0, bonus_rate=4.0, monthly_cap_ntd=200),
    ]
    uc = _user_card(1, 101, benefits)
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, 1000, "蝦皮")
    assert len(result) == 1
    assert result[0].channel_name == "蝦皮購物"


def test_fallback_uses_generic_and_skips_jcb_activity(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefits = [
        _benefit(1, "[JCB活動] 國內一般消費", base_rate=1.0, bonus_rate=5.0),
        _benefit(2, "通用回饋", base_rate=1.0, bonus_rate=1.0),
    ]
    uc = _user_card(1, 101, benefits)
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, 500, "完全不會命中的通道")
    assert len(result) == 1
    assert result[0].channel_name == "通用回饋"


def test_cap_usage_math_and_is_capped_behavior(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    capped_benefit = _benefit(1, "momo 網購", base_rate=1.0, bonus_rate=10.0, monthly_cap_ntd=100)
    uc = _user_card(1, 101, [capped_benefit])
    usages = [_usage(1, 1000)]  # max_spend = 100 / 10% = 1000, remaining = 0
    db = _FakeAsyncSession([[uc], usages])

    result = _run_get_recommendations(db, 200, "momo")
    assert len(result) == 1
    rec = result[0]
    assert rec.monthly_cap_ntd == 1000.0
    assert rec.used_amount_ntd == 1000.0
    assert rec.remaining_cap_ntd == 0.0
    assert rec.estimated_base_cashback == 2.0
    assert rec.estimated_bonus_cashback == 0.0
    assert rec.estimated_total_cashback == 2.0
    assert rec.is_capped is True


def test_bonus_rate_zero_with_cap_sets_remaining_zero(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefit = _benefit(1, "國內一般消費", base_rate=1.0, bonus_rate=0.0, monthly_cap_ntd=300)
    uc = _user_card(1, 101, [benefit])
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, 1000, "國內一般消費")
    assert len(result) == 1
    rec = result[0]
    assert rec.monthly_cap_ntd == 0
    assert rec.remaining_cap_ntd == 0.0
    assert rec.estimated_bonus_cashback == 0.0
    assert rec.is_capped is True


def test_rounding_and_no_cap_full_bonus(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefit = _benefit(1, "Apple Pay", base_rate=1.23, bonus_rate=2.34, monthly_cap_ntd=None)
    uc = _user_card(1, 101, [benefit])
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, 333, "apple pay")
    assert len(result) == 1
    rec = result[0]
    assert rec.estimated_base_cashback == 4.1
    assert rec.estimated_bonus_cashback == 7.79
    assert rec.estimated_total_cashback == 11.89
    assert rec.is_capped is False


def test_sorting_prefers_non_capped_even_if_score_lower(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    capped = _user_card(
        1,
        101,
        [_benefit(1, "momo", base_rate=1.0, bonus_rate=10.0, monthly_cap_ntd=100)],
    )
    non_capped = _user_card(
        2,
        102,
        [_benefit(2, "momo", base_rate=1.0, bonus_rate=1.0, monthly_cap_ntd=None)],
    )
    usages_for_capped = [_usage(1, 1000)]
    usages_for_non_capped = []
    db = _FakeAsyncSession([[capped, non_capped], usages_for_capped, usages_for_non_capped])

    result = _run_get_recommendations(db, 1000, "momo")
    assert len(result) == 2
    assert result[0].user_card_id == 2
    assert result[1].user_card_id == 1


def test_negative_amount_keeps_current_math_behavior(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefit = _benefit(1, "國內一般消費", base_rate=1.0, bonus_rate=2.0)
    uc = _user_card(1, 101, [benefit])
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, -100, "國內一般消費")
    assert len(result) == 1
    assert result[0].estimated_base_cashback == -1.0
    assert result[0].estimated_bonus_cashback == -2.0
    assert result[0].estimated_total_cashback == -3.0


def test_excludes_custom_business_labels(monkeypatch):
    monkeypatch.setattr(recommend_service, "UNICARD_MERCHANTS", [])
    monkeypatch.setattr(
        recommend_service,
        "get_current_billing_cycle",
        lambda _d: ("2026-08-01", "2026-08-31"),
    )

    benefits = [
        _benefit(1, "LINE Pay 新戶 10%", base_rate=1.0, bonus_rate=10.0),
        _benefit(2, "LINE Pay 大大等級 8%", base_rate=1.0, bonus_rate=8.0),
        _benefit(3, "LINE Pay 簡單選 7%", base_rate=1.0, bonus_rate=7.0),
        _benefit(4, "LINE Pay DAWAY VIP 9%", base_rate=1.0, bonus_rate=9.0),
        _benefit(5, "LINE Pay DAWAY GO 6%", base_rate=1.0, bonus_rate=6.0),
        _benefit(6, "LINE Pay 手續費減免", base_rate=1.0, bonus_rate=99.0),
        _benefit(7, "[JCB活動] LINE Pay", base_rate=1.0, bonus_rate=99.0),
    ]
    uc = _user_card(1, 101, benefits)
    db = _FakeAsyncSession([[uc], []])

    result = _run_get_recommendations(db, 1000, "line pay")
    assert len(result) == 1
    assert result[0].channel_name == "LINE Pay DAWAY GO 6%"
