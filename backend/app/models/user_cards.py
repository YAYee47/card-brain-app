from datetime import datetime
from sqlalchemy import Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class UserCard(Base):
    """
    使用者持有信用卡設定表
    每一筆記錄代表使用者持有並啟用追蹤的一張信用卡，
    同時儲存使用者自訂的帳單結帳日
    """
    __tablename__ = "user_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # 關聯到 users 表
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    # 關聯到 cards 主表
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("cards.id"), nullable=False)
    # 每月帳單結帳日 1~31 (由使用者於 Onboarding 流程設定)
    billing_cycle_date: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # 是否啟用此卡片的額度追蹤
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="user_cards")
    card = relationship("Card", backref="user_cards")
    monthly_usages = relationship("MonthlyUsage", back_populates="user_card", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user_card", cascade="all, delete-orphan")
