from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user_cards import UserCard
from app.models.cards import Card
from app.models.card_benefits import CardBenefit
from app.models.monthly_usage import MonthlyUsage
from app.schemas.dashboard import DashboardSummary, CardDashboard, BenefitUsage
from app.services.billing_cycle import get_current_billing_cycle


async def get_dashboard(db: AsyncSession, user_id: int) -> DashboardSummary:
    """
    彙整所有啟用中信用卡的當前帳單週期消費數據：
    - 每張卡片的已消耗金額、預估回饋金
    - 每個加碼通道的使用量與剩餘額度
    - 全卡合計預估回饋金
    """
    result = await db.execute(
        select(UserCard)
        .where(UserCard.is_active == True, UserCard.user_id == user_id)
        .options(selectinload(UserCard.card).selectinload(Card.benefits))
    )
    user_cards = result.scalars().all()

    cards_out: list[CardDashboard] = []
    grand_cashback = 0.0
    grand_spent = 0.0

    for uc in user_cards:
        card = uc.card
        cycle_start, cycle_end = get_current_billing_cycle(uc.billing_cycle_date)

        # 查詢本帳單週期的所有消耗紀錄
        usage_result = await db.execute(
            select(MonthlyUsage).where(
                and_(
                    MonthlyUsage.user_card_id == uc.id,
                    MonthlyUsage.cycle_start_date == cycle_start,
                    MonthlyUsage.cycle_end_date == cycle_end,
                )
            )
        )
        usages = usage_result.scalars().all()
        
        usage_map = {u.card_benefit_id: u for u in usages}
        
        total_used = sum(float(u.used_amount_ntd) for u in usages)
        total_cashback = sum(float(u.earned_cashback_ntd) for u in usages)

        # 為每個有加碼上限的通道計算使用狀態
        benefit_usages: list[BenefitUsage] = []
        for b in card.benefits:
            # cap 是最高加碼回饋金
            cap = float(b.monthly_cap_ntd) if b.monthly_cap_ntd else None
            bonus_rate_frac = float(b.bonus_rate) / 100.0
            
            # 推算該通道的消費額度上限
            spend_cap = (cap / bonus_rate_frac) if (cap and bonus_rate_frac > 0) else None

            # 取得該專屬通道的消耗紀錄
            b_usage = usage_map.get(b.id)
            used = float(b_usage.used_amount_ntd) if b_usage else 0.0
            
            remaining = max(0.0, spend_cap - used) if spend_cap is not None else None
            pct = min((used / spend_cap) * 100, 100.0) if spend_cap else 0.0

            benefit_usages.append(BenefitUsage(
                channel_name=b.channel_name,
                base_rate=float(b.base_rate),
                bonus_rate=float(b.bonus_rate),
                monthly_cap_ntd=spend_cap, # 傳回前端的是消費額度上限，以便 UI 顯示「已用 / 總額度」
                used_amount_ntd=used,
                remaining_cap_ntd=remaining,
                used_pct=round(pct, 1),
                is_warning=pct >= 80.0,
                is_capped=pct >= 100.0,
            ))

        cards_out.append(CardDashboard(
            user_card_id=uc.id,
            card_id=card.id,
            bank_name=card.bank_name,
            card_name=card.card_name,
            
            billing_cycle_date=uc.billing_cycle_date,
            cycle_start_date=cycle_start.isoformat(),
            cycle_end_date=cycle_end.isoformat(),
            total_used_ntd=total_used,
            total_cashback_ntd=total_cashback,
            benefits=benefit_usages,
        ))

        grand_cashback += total_cashback
        grand_spent += total_used

    # 以總回饋金降序排列卡片（回饋最多的排前）
    cards_out.sort(key=lambda c: c.total_cashback_ntd, reverse=True)

    return DashboardSummary(
        total_cashback_ntd=round(grand_cashback, 2),
        total_spent_ntd=round(grand_spent, 2),
        cards_count=len(cards_out),
        cards=cards_out,
        last_updated=datetime.now().isoformat(),
    )
