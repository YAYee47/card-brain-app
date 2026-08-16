from pydantic import BaseModel
from typing import Optional, List

class RecommendRequest(BaseModel):
    """消費決策推薦請求 Schema"""
    amount: float           # 消費金額 (台幣)
    channel_name: str       # 支付通道 (如：Apple Pay, LINE Pay, 通用)

class RecommendedCardOut(BaseModel):
    """單張卡片推薦試算結果回傳 Schema"""
    user_card_id: int
    card_id: int
    bank_name: str
    card_name: str
    
    billing_cycle_date: int
    channel_name: str
    base_rate: float
    bonus_rate: float
    monthly_cap_ntd: Optional[float]
    used_amount_ntd: float
    remaining_cap_ntd: Optional[float]
    estimated_base_cashback: float
    estimated_bonus_cashback: float
    estimated_total_cashback: float
    is_capped: bool
    score: float

class RecommendResponse(BaseModel):
    """推薦引擎完整回應 Schema"""
    amount: float
    channel_name: str
    results: List[RecommendedCardOut]
    top_card: Optional[RecommendedCardOut]
    results_with_registration: List[RecommendedCardOut] = []
    top_card_with_registration: Optional[RecommendedCardOut] = None
