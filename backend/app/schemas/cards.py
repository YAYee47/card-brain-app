from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

# ── Card Schemas ──────────────────────────────────────────────

class CardBenefitOut(BaseModel):
    """卡片權益輸出 Schema"""
    id: int
    channel_name: str
    base_rate: float
    bonus_rate: float
    monthly_cap_ntd: Optional[float] = None
    effective_date: date

    model_config = {"from_attributes": True}

class CardOut(BaseModel):
    """信用卡主表輸出 Schema"""
    id: int
    bank_name: str
    card_name: str
    mode_config: Optional[str] = None
    
    benefit_url: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    benefits: List[CardBenefitOut] = []

    model_config = {"from_attributes": True}

# ── UserCard Schemas ──────────────────────────────────────────

class UserCardCreate(BaseModel):
    """使用者新增持有卡片請求 Schema (Onboarding 使用)"""
    card_id: int
    billing_cycle_date: int  # 1~31

class CustomCardCreate(BaseModel):
    """使用者手動新增全新自訂卡片"""
    bank_name: str
    card_name: str
    benefit_url: Optional[str] = None
    billing_cycle_date: int = 1

class UserCardUpdate(BaseModel):
    """使用者更新卡片設定 Schema"""
    billing_cycle_date: Optional[int] = None
    is_active: Optional[bool] = None

class UserCardOut(BaseModel):
    """使用者持有卡片輸出 Schema"""
    id: int
    card_id: int
    billing_cycle_date: int
    is_active: bool
    card: CardOut

    model_config = {"from_attributes": True}
