from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.users import User
from app.schemas.users import UserAuthRequest, UserOut
from app.api.deps import get_current_user

import bcrypt

router = APIRouter()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@router.post("/auth", response_model=UserOut, summary="註冊或登入")
async def authenticate_user(payload: UserAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    輕量級會員系統登入與註冊（加入密碼保護）。
    1. 訪客：直接依 uuid 建立。
    2. 舊帳號登入：若發現同 nickname 的帳號，檢查密碼。正確則覆寫/繼承該帳號的 device_uuid。
    3. 新帳號註冊：若 nickname 不存在，建立並設定密碼。
    4. 過渡機制：如果舊帳號密碼為空，則本次輸入的密碼直接作為永久密碼綁定。
    """
    if payload.is_guest:
        # 訪客直接尋找 device_uuid 或建立
        result = await db.execute(select(User).where(User.device_uuid == payload.device_uuid))
        user = result.scalar_one_or_none()
        if user:
            return user
        new_user = User(
            device_uuid=payload.device_uuid,
            nickname=payload.nickname,
            is_guest=True
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    # 非訪客：必須檢查密碼與暱稱
    if not payload.password:
        raise HTTPException(status_code=400, detail="非訪客帳號必須設定密碼")

    # 用暱稱尋找是否已存在該帳號 (不區分大小寫可用 ilike，此處使用精確比對)
    result = await db.execute(select(User).where(User.nickname == payload.nickname, User.is_guest == False))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        # 【帳號已存在，執行登入邏輯】
        # 1. 舊帳號首次綁定密碼過渡機制
        if not existing_user.password_hash:
            existing_user.password_hash = get_password_hash(payload.password)
            existing_user.device_uuid = payload.device_uuid
            await db.commit()
            await db.refresh(existing_user)
            return existing_user
        
        # 2. 正常密碼檢驗
        if not verify_password(payload.password, existing_user.password_hash):
            raise HTTPException(status_code=401, detail="此暱稱已被註冊，且密碼錯誤")
        
        # 3. 密碼正確，更新 device_uuid 以綁定新設備
        existing_user.device_uuid = payload.device_uuid
        await db.commit()
        await db.refresh(existing_user)
        return existing_user
        
    # 【帳號不存在，執行註冊邏輯】
    new_user = User(
        device_uuid=payload.device_uuid,
        nickname=payload.nickname,
        password_hash=get_password_hash(payload.password),
        is_guest=False
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
