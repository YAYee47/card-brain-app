from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class User(Base):
    """
    使用者表 (會員系統)
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_uuid: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    is_guest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 關聯
    user_cards = relationship("UserCard", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    monthly_usages = relationship("MonthlyUsage", back_populates="user", cascade="all, delete-orphan")
    app_alerts = relationship("AppAlert", back_populates="user", cascade="all, delete-orphan")
