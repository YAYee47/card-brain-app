from dataclasses import dataclass, field
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user_cards import UserCard
from app.models.cards import Card
from app.models.card_benefits import CardBenefit
from app.models.monthly_usage import MonthlyUsage
from app.services.billing_cycle import get_current_billing_cycle
from app.utils.string_matching import build_search_keywords, is_benefit_matched
@dataclass
class RecommendedCard:
    """單張卡片的推薦試算結果"""
    user_card_id: int
    card_id: int
    bank_name: str
    card_name: str
    
    billing_cycle_date: int
    channel_name: str
    base_rate: float
    bonus_rate: float
    monthly_cap_ntd: Optional[float]
    # 本帳單週期已消耗金額
    used_amount_ntd: float
    # 本帳單週期剩餘可加碼金額 (None = 無上限)
    remaining_cap_ntd: Optional[float]
    # 本次消費預估獲得基礎回饋 (NTD)
    estimated_base_cashback: float
    # 本次消費預估獲得加碼回饋 (NTD，受剩餘額度限制)
    estimated_bonus_cashback: float
    # 本次消費預估獲得總回饋 (NTD)
    estimated_total_cashback: float
    # 加碼額度是否已滿封頂
    is_capped: bool
    # 排序分數 (越高越優先)
    score: float = field(init=False)

    def __post_init__(self):
        # 以總回饋金作為主排序依據，無上限卡片給予略低優先（避免把有限額度卡埋在後面）
        self.score = self.estimated_total_cashback


async def get_recommendations(
    db: AsyncSession,
    amount: float,
    channel_name: str,
    exclude_registration: bool = False,
) -> list[RecommendedCard]:
    """
    消費決策推薦引擎核心邏輯：
    1. 取得使用者所有啟用中的信用卡
    2. 為每張卡找出「最符合支付通道」的權益規則
    3. 查詢當前帳單週期的已消耗額度
    4. 計算本次消費的預估基礎 + 加碼回饋
    5. 依照預估總回饋金排序後回傳
    """
    # 取得所有啟用中的使用者卡片（含卡片主表與權益）
    result = await db.execute(
        select(UserCard)
        .where(UserCard.is_active == True)
        .options(
            selectinload(UserCard.card).selectinload(Card.benefits)
        )
    )
    user_cards = result.scalars().all()

    if not user_cards:
        return []

    recommendations: list[RecommendedCard] = []

    for user_card in user_cards:
        card = user_card.card
        benefits = card.benefits

        # 找出本次支付通道對應的最優權益規則
        # 將前端長字串映射成資料庫權益規則的關鍵字
        search_keywords = build_search_keywords(channel_name)
        matched_benefits: list[CardBenefit] = []

        # 精確比對：通道名稱包含關鍵字即視為符合
        for b in benefits:
            if is_benefit_matched(b, search_keywords, channel_name, exclude_registration):
                matched_benefits.append(b)

        # 針對同一張卡片中，如果有多個規則符合，且他們的 (基本回饋, 加碼回饋, 上限) 完全相同，
        # 就只保留名稱最短的那一個，避免畫面上出現兩筆一樣的回饋（例如「蝦皮購物(UP選)」跟「百大指定消費-UP選...」）
        if matched_benefits:
            deduped = {}
            for b in matched_benefits:
                key = (float(b.base_rate), float(b.bonus_rate), float(b.monthly_cap_ntd) if b.monthly_cap_ntd else None)
                if key not in deduped:
                    deduped[key] = b
                else:
                    if len(b.channel_name) < len(deduped[key].channel_name):
                        deduped[key] = b
            matched_benefits = list(deduped.values())
        # fallback: 使用「通用」或「國內一般消費」通道
        if not matched_benefits:
            for b in benefits:
                if b.channel_name.startswith("[JCB活動]"):
                    continue
                if "通用" in b.channel_name or "國內一般消費" in b.channel_name:
                    matched_benefits.append(b)
                    break

        if not matched_benefits:
            continue  # 此卡無任何適用通道，跳過

        # 計算當前帳單週期
        cycle_start, cycle_end = get_current_billing_cycle(user_card.billing_cycle_date)

        # 查詢本帳單週期已消耗金額 (跨所有通道)
        usage_result = await db.execute(
            select(MonthlyUsage).where(
                and_(
                    MonthlyUsage.user_card_id == user_card.id,
                    MonthlyUsage.cycle_start_date == cycle_start,
                    MonthlyUsage.cycle_end_date == cycle_end,
                )
            )
        )
        usages = usage_result.scalars().all()
        usage_map = {u.card_benefit_id: u for u in usages}

        for matched_benefit in matched_benefits:
            b_usage = usage_map.get(matched_benefit.id)
            used_amount = float(b_usage.used_amount_ntd) if b_usage else 0.0

            # 計算剩餘加碼額度
            monthly_cap_cashback = float(matched_benefit.monthly_cap_ntd) if matched_benefit.monthly_cap_ntd else None
            remaining_cap = None
            max_spend = None
            if monthly_cap_cashback is not None:
                max_spend = monthly_cap_cashback / (float(matched_benefit.bonus_rate) / 100) if matched_benefit.bonus_rate > 0 else 0
                remaining_cap = max(0.0, max_spend - used_amount)

            # ── 試算本次消費的預估回饋 ──────────────────────────────
            # 基礎回饋：無封頂限制
            estimated_base = round(amount * float(matched_benefit.base_rate) / 100, 2)

            # 加碼回饋：受剩餘加碼額度限制
            bonus_amount_full = round(amount * float(matched_benefit.bonus_rate) / 100, 2)
            if remaining_cap is not None:
                # 加碼以「剩餘可享加碼消費金額」為上限
                effective_bonus_spending = min(amount, remaining_cap)
                estimated_bonus = round(effective_bonus_spending * float(matched_benefit.bonus_rate) / 100, 2)
            else:
                estimated_bonus = bonus_amount_full

            estimated_total = round(estimated_base + estimated_bonus, 2)
            is_capped = (remaining_cap is not None and remaining_cap <= 0)

            recommendations.append(RecommendedCard(
                user_card_id=user_card.id,
                card_id=card.id,
                bank_name=card.bank_name,
                card_name=card.card_name,
                
                billing_cycle_date=user_card.billing_cycle_date,
                channel_name=matched_benefit.channel_name,
                base_rate=float(matched_benefit.base_rate),
                bonus_rate=float(matched_benefit.bonus_rate),
                monthly_cap_ntd=max_spend,
                used_amount_ntd=used_amount,
                remaining_cap_ntd=remaining_cap,
                estimated_base_cashback=estimated_base,
                estimated_bonus_cashback=estimated_bonus,
                estimated_total_cashback=estimated_total,
                is_capped=is_capped,
            ))

    # 以預估總回饋金降序排序，額度已滿的卡片置底
    recommendations.sort(key=lambda r: (not r.is_capped, r.score), reverse=True)
    return recommendations
