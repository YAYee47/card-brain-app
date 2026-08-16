from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.transactions import Transaction
from app.models.user_cards import UserCard
from app.models.card_benefits import CardBenefit
from app.models.monthly_usage import MonthlyUsage
from app.services.billing_cycle import get_current_billing_cycle

from app.utils.string_matching import build_search_keywords, is_benefit_matched

async def calculate_txn_cashback(txn: Transaction, user_card: UserCard, benefits: list[CardBenefit], db: AsyncSession) -> Transaction:
    """
    計算單筆交易的回饋金，並更新 txn.earned_cashback_ntd 與 monthly_usage。
    """
    matched_benefit: Optional[CardBenefit] = None
    search_keywords = build_search_keywords(txn.channel_name)
    
    for b in benefits:
        # 排除掉 required_mode 不符的權益
        if b.required_mode and b.required_mode != txn.card_mode:
            continue
            
        if is_benefit_matched(b, search_keywords, txn.channel_name, exclude_registration=False):
            if matched_benefit is None or b.bonus_rate > matched_benefit.bonus_rate:
                matched_benefit = b

    if matched_benefit is None:
        print(f"DEBUG: No specific channel match. Searching for generic match for {txn.channel_name}")
        for b in benefits:
            if b.required_mode and b.required_mode != txn.card_mode:
                continue
            if b.channel_name.startswith("[JCB活動]"):
                continue
            if "通用" in b.channel_name or "國內一般消費" in b.channel_name:
                matched_benefit = b
                break
    print(f"DEBUG: matched_benefit={matched_benefit.channel_name if matched_benefit else 'None'}")

    earned_cashback = 0.0
    ntd_amount = float(txn.ntd_amount)
    
    cycle_start, cycle_end = get_current_billing_cycle(user_card.billing_cycle_date, txn.transacted_at.date())
    
    # Get current usage for this specific benefit
    usage = None
    if matched_benefit:
        usage_result = await db.execute(
            select(MonthlyUsage).where(
                and_(
                    MonthlyUsage.user_card_id == user_card.id,
                    MonthlyUsage.card_benefit_id == matched_benefit.id,
                    MonthlyUsage.cycle_start_date == cycle_start,
                    MonthlyUsage.cycle_end_date == cycle_end,
                )
            )
        )
        usage = usage_result.scalar_one_or_none()
    
    if matched_benefit:
        used_ntd = float(usage.used_amount_ntd) if usage else 0.0
        
        # monthly_cap_ntd is the MAXIMUM BONUS CASHBACK (e.g. 500 points).
        # We need to find the equivalent max spend limit to calculate remaining spend cap.
        cap = float(matched_benefit.monthly_cap_ntd) if matched_benefit.monthly_cap_ntd else None
        bonus_rate_frac = float(matched_benefit.bonus_rate) / 100.0
        
        spend_cap = (cap / bonus_rate_frac) if (cap and bonus_rate_frac > 0) else None
        remaining_spend_cap = max(0.0, spend_cap - used_ntd) if spend_cap is not None else None

        base_cashback = round(ntd_amount * float(matched_benefit.base_rate) / 100, 2)
        if remaining_spend_cap is not None:
            effective_spend = min(ntd_amount, remaining_spend_cap)
            bonus_cashback = round(effective_spend * bonus_rate_frac, 2)
        else:
            bonus_cashback = round(ntd_amount * bonus_rate_frac, 2)
        earned_cashback = round(base_cashback + bonus_cashback, 2)

    txn.earned_cashback_ntd = earned_cashback
    
    if matched_benefit:
        if usage:
            usage.used_amount_ntd = float(usage.used_amount_ntd) + ntd_amount
            usage.earned_cashback_ntd = float(usage.earned_cashback_ntd) + earned_cashback
        else:
            new_usage = MonthlyUsage(
                user_card_id=user_card.id,
                card_benefit_id=matched_benefit.id,
                cycle_start_date=cycle_start,
                cycle_end_date=cycle_end,
                used_amount_ntd=ntd_amount,
                earned_cashback_ntd=earned_cashback,
            )
            db.add(new_usage)
    return txn
