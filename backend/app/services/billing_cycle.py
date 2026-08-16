from datetime import date
from typing import Optional, Iterable, Protocol


class SupportsBillingCycle(Protocol):
    billing_cycle_date: int


def validate_billing_cycle_date(billing_cycle_date: int) -> None:
    """Validate that the billing cycle date is inside the supported 1..31 range."""
    if not (1 <= billing_cycle_date <= 31):
        raise ValueError("帳單結帳日必須介於 1 至 31 之間")


def apply_billing_cycle_to_cards(cards: Iterable[SupportsBillingCycle], billing_cycle_date: int) -> None:
    """Apply a billing cycle date to a collection of card-like records in-place."""
    validate_billing_cycle_date(billing_cycle_date)
    for card in cards:
        card.billing_cycle_date = billing_cycle_date


def get_current_billing_cycle(billing_cycle_date: int, today: Optional[date] = None) -> tuple[date, date]:
    """
    根據使用者設定的帳單結帳日，計算「當前帳單週期」的起始與結束日期。
    
    邏輯：若結帳日為 15，則週期為 16 日 ~ 次月 15 日。
    例如今天是 2026-08-11，結帳日 15：
      - 上月 16 (2026-07-16) ~ 本月 15 (2026-08-15) = 當前週期
    """
    if today is None:
        today = date.today()

    year = today.year
    month = today.month

    # 週期起始為「結帳日 + 1 日」
    cycle_start_day = billing_cycle_date + 1

    if today.day > billing_cycle_date:
        # 今天已超過本月結帳日，週期為：本月(billing+1) ~ 次月(billing)
        # 起始日：本月的 cycle_start_day
        if cycle_start_day > 28:
            # 防止 overflow (簡化：若起始日過大，直接取本月 1 日)
            cycle_start_day = 1
        cycle_start = date(year, month, cycle_start_day)
        # 結束日：次月的 billing_cycle_date
        if month == 12:
            cycle_end = date(year + 1, 1, billing_cycle_date)
        else:
            cycle_end = date(year, month + 1, billing_cycle_date)
    else:
        # 今天尚未達本月結帳日，週期為：上月(billing+1) ~ 本月(billing)
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        if cycle_start_day > 28:
            cycle_start_day = 1
        cycle_start = date(prev_year, prev_month, cycle_start_day)
        cycle_end = date(year, month, billing_cycle_date)

    return cycle_start, cycle_end
