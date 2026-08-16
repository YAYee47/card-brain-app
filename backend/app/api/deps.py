from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.db.database import get_db
from app.models.users import User

async def get_current_user(
    x_device_uuid: Optional[str] = Header(None, alias="X-Device-UUID"),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    依賴項：根據 HTTP Header `X-Device-UUID` 取得當前使用者。
    這是一個輕量級的身分驗證機制。
    如果前端沒有傳送 UUID，或資料庫找不到該 UUID，則回傳 401。
    """
    if not x_device_uuid:
        raise HTTPException(status_code=401, detail="缺少 X-Device-UUID 標頭")
    
    result = await db.execute(select(User).where(User.device_uuid == x_device_uuid))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="無效的裝置 UUID，請重新登入或註冊")
        
    return user
