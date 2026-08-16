from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class AlertOut(BaseModel):
    """警報輸出 Schema"""
    id: int
    alert_type: str
    severity: str
    card_id: Optional[int]
    user_card_id: Optional[int]
    title: str
    body: str
    diff_detail: Optional[str]
    is_read: bool
    created_at: str

    model_config = {"from_attributes": True}


class CrawlResultOut(BaseModel):
    """爬蟲執行結果"""
    status: str
    checked: int = 0
    updated: int = 0
    alerts_created: int = 0
    quota_alerts: int = 0
    run_at: str
