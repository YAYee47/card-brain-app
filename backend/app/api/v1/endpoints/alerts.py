from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.users import User
from app.models.alerts import AppAlert
from app.schemas.alerts import AlertOut, CrawlResultOut
from app.services.diff_engine import run_crawl_and_diff, check_quota_warnings, serialize_alerts

router = APIRouter()


@router.get("/alerts", response_model=List[AlertOut], summary="取得所有警報通知")
async def list_alerts(
    unread_only: bool = Query(False, description="只回傳未讀警報"),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    取得按時間降序排列的警報清單（爬蟲差異 + 額度警告）。
    """
    query = select(AppAlert).where(AppAlert.user_id == current_user.id).order_by(desc(AppAlert.created_at)).limit(limit)
    if unread_only:
        query = query.where(AppAlert.is_read == False)
    result = await db.execute(query)
    alerts = result.scalars().all()
    return serialize_alerts(alerts)


@router.post("/alerts/{alert_id}/read", summary="標記警報為已讀")
async def mark_read(alert_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """標記單一警報為已讀狀態"""
    await db.execute(
        update(AppAlert).where(AppAlert.id == alert_id, AppAlert.user_id == current_user.id).values(is_read=True)
    )
    await db.commit()
    return {"status": "ok"}


@router.post("/alerts/read-all", summary="全部標記已讀")
async def mark_all_read(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """一次標記所有未讀警報為已讀"""
    await db.execute(update(AppAlert).where(AppAlert.is_read == False, AppAlert.user_id == current_user.id).values(is_read=True))
    await db.commit()
    return {"status": "ok"}


@router.post("/crawl", response_model=CrawlResultOut, summary="手動觸發爬蟲與差異比對")
async def trigger_crawl(db: AsyncSession = Depends(get_db)):
    """
    手動觸發一次爬蟲執行（平時由排程自動在月初執行）：
    1. 模擬抓取最新銀行權益資料
    2. 與現有資料比對差異，產生 BENEFIT_CHANGE 警報
    3. 同時掃描額度使用量，產生 QUOTA_WARNING / QUOTA_CAPPED 警報
    """
    crawl_result = await run_crawl_and_diff(db)
    quota_alerts = await check_quota_warnings(db)
    return CrawlResultOut(
        status=crawl_result.get("status", "done"),
        checked=crawl_result.get("checked", 0),
        updated=crawl_result.get("updated", 0),
        alerts_created=crawl_result.get("alerts_created", 0),
        quota_alerts=quota_alerts,
        run_at=crawl_result.get("run_at", datetime.now().isoformat()),
    )
