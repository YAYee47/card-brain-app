from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.users import User
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard import get_dashboard

router = APIRouter()

@router.get("/dashboard", response_model=DashboardSummary, summary="取得儀表板彙整資料")
async def dashboard(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    取得所有啟用中信用卡的當前帳單週期儀表板彙整資料：
    - 各卡片加碼額度使用狀態（已消耗 / 剩餘 / 百分比）
    - 各卡片本週期預估獲得回饋金
    - 全卡合計回饋金與消費金額
    供前端首頁儀表板與離線快取使用。
    """
    return await get_dashboard(db, current_user.id)
