from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.users import User
from app.schemas.users import UserAuthRequest, UserOut
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/auth", response_model=UserOut, summary="註冊或登入")
async def authenticate_user(payload: UserAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    輕量級會員系統登入與註冊。
    透過 device_uuid 查詢是否有該裝置。
    如果沒有，則建立一個新的 User (包含訪客)。
    特殊邏輯：如果 nickname == 'YAYee' 且資料庫存在尚未綁定 uuid 的 YAYee，則綁定。
    """
    # 1. 嘗試尋找相同的 device_uuid
    result = await db.execute(select(User).where(User.device_uuid == payload.device_uuid))
    user = result.scalar_one_or_none()
    
    if user:
        # 已有帳號，直接回傳 (等於登入)
        return user
        
    # 2. 建立全新帳號或訪客
    new_user = User(
        device_uuid=payload.device_uuid,
        nickname=payload.nickname,
        is_guest=payload.is_guest
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.get("", response_model=list[UserOut], summary="取得所有非訪客使用者清單")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """
    取得目前所有已建立的常規使用者（不含訪客）。
    提供給前端顯示「已儲存身分」列表。
    """
    result = await db.execute(select(User).where(User.is_guest == False))
    return result.scalars().all()

@router.delete("/me", summary="刪除當前帳號 (離開訪客模式用)")
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    刪除當前登入的使用者帳號。
    這會觸發 cascade delete，一併清空該使用者的所有卡片、記帳與提醒紀錄。
    主要供訪客模式「離開試用」時呼叫，以達到不留痕跡的效果。
    """
    await db.delete(current_user)
    await db.commit()
    return {"message": f"使用者 {current_user.nickname} 及其所有資料已成功刪除"}
