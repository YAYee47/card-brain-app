from datetime import date, datetime
from sqlalchemy import Integer, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class MonthlyUsage(Base):
    """
    帳單週期累計消耗表
    根據使用者設定的帳單結帳日動態計算「當前帳單週期」，
    記錄該週期內每張卡片的已消耗台幣金額
    """
    __tablename__ = "monthly_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    user_card_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_cards.id"), nullable=False)
    card_benefit_id: Mapped[int] = mapped_column(Integer, ForeignKey("card_benefits.id"), nullable=False)
    # 本帳單週期起始日 (例如 2026-07-16)
    cycle_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    # 本帳單週期結束日 (例如 2026-08-15)
    cycle_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    # 該週期已消耗的台幣加碼金額 (用於比對加碼封頂)
    used_amount_ntd: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    # 該週期已賺取的預估回饋金 (NTD)
    earned_cashback_ntd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="monthly_usages")
    user_card = relationship("UserCard", back_populates="monthly_usages")
    card_benefit = relationship("CardBenefit")
