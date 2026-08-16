from pydantic import BaseModel
from typing import Optional, List

class BenefitUsage(BaseModel):
    """單一支付通道的加碼額度使用狀態"""
    channel_name: str
    base_rate: float
    bonus_rate: float
    monthly_cap_ntd: Optional[float]
    used_amount_ntd: float
    remaining_cap_ntd: Optional[float]
    used_pct: float          # 0.0 ~ 100.0
    is_warning: bool         # 使用率 >= 80%
    is_capped: bool          # 使用率 >= 100%

class CardDashboard(BaseModel):
    """單張卡片的儀表板資料"""
    user_card_id: int
    card_id: int
    bank_name: str
    card_name: str
    
    billing_cycle_date: int
    cycle_start_date: str    # YYYY-MM-DD
    cycle_end_date: str      # YYYY-MM-DD
    total_used_ntd: float    # 本週期總消費台幣
    total_cashback_ntd: float  # 本週期預估已賺回饋
    benefits: List[BenefitUsage]

class DashboardSummary(BaseModel):
    """儀表板總覽回應"""
    total_cashback_ntd: float      # 所有卡片本週期合計預估回饋
    total_spent_ntd: float         # 所有卡片本週期合計消費
    cards_count: int
    cards: List[CardDashboard]
    last_updated: str              # ISO datetime
