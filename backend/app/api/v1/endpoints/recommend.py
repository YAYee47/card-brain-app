from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.recommend import RecommendRequest, RecommendResponse, RecommendedCardOut
from app.services.recommend import get_recommendations

router = APIRouter()

# 系統支援的支付通道清單
SUPPORTED_CHANNELS = [
    "國內一般消費",
    "國外消費",
    "行動支付 (Apple Pay/Google Pay)",
    "LINE Pay",
    "網購 (momo/PChome等)",
    "蝦皮購物 (Shopee)",
    "淘寶 (Taobao)",
    "日本海外消費",
    "App Store / Google Play 遊戲課金",
]

@router.post("/recommend", response_model=RecommendResponse, summary="消費決策推薦試算")
async def recommend_card(
    payload: RecommendRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    核心消費推薦引擎：
    - 輸入「消費金額 (NTD)」與「支付通道」
    - 根據各卡當前帳單週期已消耗額度，試算並排序預估回饋最高的卡片
    - 額度已滿封頂的卡片自動置底
    """
    # 1. 預設結果（排除需登錄的活動）
    results_no_reg = await get_recommendations(db, payload.amount, payload.channel_name, exclude_registration=True)
    
    # 2. 包含登錄活動的結果
    results_with_reg = await get_recommendations(db, payload.amount, payload.channel_name, exclude_registration=False)

    def _map_to_out(results_list):
        return [
            RecommendedCardOut(
                user_card_id=r.user_card_id,
                card_id=r.card_id,
                bank_name=r.bank_name,
                card_name=r.card_name,
                
                billing_cycle_date=r.billing_cycle_date,
                channel_name=r.channel_name,
                base_rate=r.base_rate,
                bonus_rate=r.bonus_rate,
                monthly_cap_ntd=r.monthly_cap_ntd,
                used_amount_ntd=r.used_amount_ntd,
                remaining_cap_ntd=r.remaining_cap_ntd,
                estimated_base_cashback=r.estimated_base_cashback,
                estimated_bonus_cashback=r.estimated_bonus_cashback,
                estimated_total_cashback=r.estimated_total_cashback,
                is_capped=r.is_capped,
                score=r.score,
            )
            for r in results_list
        ]

    results_out = _map_to_out(results_no_reg)
    results_with_reg_out = _map_to_out(results_with_reg)

    return RecommendResponse(
        amount=payload.amount,
        channel_name=payload.channel_name,
        results=results_out,
        top_card=results_out[0] if results_out else None,
        results_with_registration=results_with_reg_out,
        top_card_with_registration=results_with_reg_out[0] if results_with_reg_out else None,
    )

@router.get("/recommend/channels", response_model=List[str], summary="取得支援的支付通道清單")
async def list_channels():
    """
    回傳系統支援的支付通道清單，供前端下拉選單使用
    """
    return SUPPORTED_CHANNELS
