from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class Card(Base):
    """
    信用卡主表 (Master Table)
    儲存所有支援追蹤的銀行信用卡基本資訊
    """
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bank_name: Mapped[str] = mapped_column(String(50), nullable=False)
    card_name: Mapped[str] = mapped_column(String(100), nullable=False)
    mode_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    benefit_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
