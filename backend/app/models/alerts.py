from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.database import Base


class AppAlert(Base):
    """使用者通知警報表 (爬蟲差異 + 額度警告)"""
    __tablename__ = "app_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, default=1)

    # 警報類型：BENEFIT_CHANGE / QUOTA_WARNING / QUOTA_CAPPED / CRAWL_DONE
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # 嚴重程度：INFO / WARNING / CRITICAL
    severity: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)

    # 關聯卡片（可為 null，代表系統級警報）
    card_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("cards.id"), nullable=True)
    user_card_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user_cards.id"), nullable=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # 差異詳細資料 (JSON 字串)
    diff_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    user = relationship("User", back_populates="app_alerts")

class BenefitSnapshot(Base):
    """權益快照表 — 每次爬蟲完成後儲存一份快照，供差異比對使用"""
    __tablename__ = "benefit_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("cards.id"), nullable=False)
    channel_name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_rate: Mapped[float] = mapped_column(nullable=False)
    bonus_rate: Mapped[float] = mapped_column(nullable=False)
    monthly_cap_ntd: Mapped[float | None] = mapped_column(nullable=True)
    # 快照來源：SEED / CRAWLER / MANUAL
    source: Mapped[str] = mapped_column(String(20), default="SEED", nullable=False)
    snapshotted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
