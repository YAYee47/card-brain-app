from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ── OCR 端點 Schema ────────────────────────────────────────────

class OcrResultOut(BaseModel):
    """OCR 辨識結果回應 Schema"""
    amount: Optional[float] = None
    currency: str = "TWD"
    merchant_name: Optional[str] = None
    transaction_date: Optional[str] = None
    channel_name: Optional[str] = None
    category: Optional[str] = None
    confidence: str = "low"
    raw_text: Optional[str] = None

# ── 交易記帳 Schema ────────────────────────────────────────────

class TransactionCreate(BaseModel):
    """新增交易記帳請求 Schema"""
    user_card_id: int
    channel_name: str
    card_mode: Optional[str] = None
    category: str = "其他"
    merchant_name: Optional[str] = None
    original_amount: float
    currency: str = "TWD"
    source_type: str = "MANUAL"   # QR_CODE / AI_RECEIPT_VISION / AI_SCREENSHOT_VISION / MANUAL
    card_mode: Optional[str] = None
    transacted_at: Optional[str] = None  # ISO datetime 字串，若為空則使用當下時間

class TransactionOut(BaseModel):
    """交易記帳回應 Schema"""
    id: int
    user_card_id: int
    channel_name: str
    card_mode: Optional[str] = None
    category: str
    merchant_name: Optional[str]
    original_amount: float
    currency: str
    ntd_amount: float
    exchange_rate: float
    earned_cashback_ntd: float
    source_type: str
    card_mode: Optional[str]
    transacted_at: str

    model_config = {"from_attributes": True}
