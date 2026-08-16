from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Numeric, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class Transaction(Base):
    """
    消費記帳明細表
    記錄每一筆透過 QR Code / AI 視覺 / 截圖 / 手動等四軌方式記帳的交易
    """
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    user_card_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_cards.id"), nullable=False)
    # 支付通道 (如：Apple Pay, LINE Pay, 實體刷卡, 網路消費)
    channel_name: Mapped[str] = mapped_column(Text, nullable=False)
    # 消費分類 (如：餐飲, 購物, 交通, 數位網購, 娛樂, 固定支出)
    category: Mapped[str] = mapped_column(String(50), nullable=True, default="其他")
    # 商家名稱 (由 AI 辨識或使用者手動輸入)
    merchant_name: Mapped[str] = mapped_column(Text, nullable=True)
    # 原始消費金額 (外幣時記錄原始幣值)
    original_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    # 幣別 (如 TWD, JPY, USD)
    currency: Mapped[str] = mapped_column(String(5), nullable=False, default="TWD")
    # 換算台幣金額
    ntd_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    # 採用匯率 (台幣消費固定為 1.0)
    exchange_rate: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False, default=1.0)
    # 本筆交易預計獲得之台幣回饋金 (基礎 + 加碼合計)
    earned_cashback_ntd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    # 記帳來源類型
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    card_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # 實際消費時間
    transacted_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="transactions")
    user_card = relationship("UserCard", back_populates="transactions")
