from datetime import date, datetime
from typing import Optional
from sqlalchemy import Integer, String, Numeric, Date, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class CardBenefit(Base):
    """
    卡片權益規則表
    記錄每張信用卡在各支付通道的基礎回饋率、加碼回饋率與加碼封頂金額
    """
    __tablename__ = "card_benefits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("cards.id"), nullable=False)
    # 適用支付通道名稱 (如：通用, Apple Pay, LINE Pay, 街口支付, 海外消費)
    channel_name: Mapped[str] = mapped_column(Text, nullable=False)
    # 基礎回饋率 (%)，如 0.5 代表 0.5%
    base_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    # 加碼回饋率 (%)，如 5.0 代表 5%
    bonus_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    # 當帳單週期加碼回饋封頂金額 (NTD)，NULL 代表無上限
    monthly_cap_ntd: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # 額外權益限制 (如：需登錄, 指定門市)
    required_mode: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # 本條權益的生效日期，支援權益異動歷史紀錄
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    card = relationship("Card", back_populates="benefits")
