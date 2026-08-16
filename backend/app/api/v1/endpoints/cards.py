from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
from datetime import date, datetime

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.users import User
from app.models.cards import Card
from app.models.card_benefits import CardBenefit
from app.models.user_cards import UserCard
from app.schemas.cards import CardOut, UserCardCreate, UserCardUpdate, UserCardOut, CustomCardCreate
from app.core.card_profiles import CARD_PROFILES, JCB_SPECIAL_OFFERS
from app.services.ai_crawler import scrape_card_benefits
from app.services.billing_cycle import validate_billing_cycle_date, apply_billing_cycle_to_cards
from app.services.user_cards import (
    get_card_list_query,
    get_card_by_id_query,
    get_active_user_cards_query,
    get_user_card_detail_query,
    get_same_bank_user_cards_query,
    get_user_card_with_card_only_query,
    get_card_by_id,
    get_user_card_by_id,
)

router = APIRouter()

@router.get("/cards", response_model=List[CardOut], summary="取得所有支援的信用卡與權益列表")
async def list_all_cards(db: AsyncSession = Depends(get_db)):
    """
    取得系統內所有信用卡與其對應的各通道權益規則，供前端 Onboarding 選卡流程使用
    """
    result = await db.execute(get_card_list_query())
    cards = result.scalars().all()
    return cards

@router.get("/cards/{card_id}", response_model=CardOut, summary="取得單一信用卡詳細權益")
async def get_card(card_id: int, db: AsyncSession = Depends(get_db)):
    """
    根據 card_id 取得指定信用卡的詳細權益資料
    """
    result = await db.execute(get_card_by_id_query(card_id))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="找不到指定的信用卡資料")
    return card

@router.get("/user-cards", response_model=List[UserCardOut], summary="取得使用者持有的信用卡清單")
async def list_user_cards(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    取得使用者已設定持有的所有信用卡（含帳單結帳日設定與完整權益資料）
    """
    result = await db.execute(get_active_user_cards_query(current_user.id))
    user_cards = result.scalars().all()
    return user_cards

@router.post("/user-cards/custom", response_model=UserCardOut, summary="手動新增全新自訂卡片")
async def add_custom_card(payload: CustomCardCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    手動新增一張自訂卡片至系統，並自動將其加入使用者的錢包中。
    若有提供權益網址，則同步觸發 AI 爬蟲進行抓取。
    """
    try:
        validate_billing_cycle_date(payload.billing_cycle_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # 1. 建立 Card (全域)
    new_card = Card(
        bank_name=payload.bank_name,
        card_name=payload.card_name,
        benefit_url=payload.benefit_url
    )
    
    # 嘗試抓取權益資料
    if payload.benefit_url:
        try:
            url_param = payload.benefit_url
            if "," in url_param:
                url_param = [u.strip() for u in url_param.split(",") if u.strip()]
                
            # 由於自訂卡片沒有額外的指示，使用預設的通用指示
            benefits_data = await scrape_card_benefits(
                card_name=payload.card_name,
                url=url_param,
                instructions="請盡可能擷取該網頁上所有提到的回饋權益。"
            )
            if benefits_data:
                new_card.last_synced_at = datetime.now()
                db.add(new_card)
                await db.commit()
                await db.refresh(new_card)
                
                # 新增權益
                for b in benefits_data:
                    new_benefit = CardBenefit(
                        card_id=new_card.id,
                        channel_name=b.channel_name,
                        base_rate=b.base_rate,
                        bonus_rate=b.bonus_rate,
                        monthly_cap_ntd=b.monthly_cap_ntd,
                        effective_date=date.today()
                    )
                    db.add(new_benefit)
                await db.commit()
        except Exception as e:
            # 抓取失敗不應中斷卡片建立
            print(f"[SYNC] 自訂卡片爬蟲抓取失敗: {e}")
            
    if not new_card.id:
        db.add(new_card)
        await db.commit()
        await db.refresh(new_card)

    # 2. 加入 UserCard (綁定當前使用者)
    user_card = UserCard(
        card_id=new_card.id,
        user_id=current_user.id,
        billing_cycle_date=payload.billing_cycle_date
    )
    db.add(user_card)
    await db.commit()
    await db.refresh(user_card)

    reloaded = await get_user_card_by_id(db, user_card.id, current_user.id)
    return reloaded

@router.post("/user-cards", response_model=UserCardOut, summary="新增使用者持有信用卡 (Onboarding)")
async def add_user_card(payload: UserCardCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Onboarding 流程：使用者選擇持有的信用卡並設定帳單結帳日 (1~31)
    """
    try:
        validate_billing_cycle_date(payload.billing_cycle_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # 確認卡片存在
    card = await get_card_by_id(db, payload.card_id)
    if not card:
        raise HTTPException(status_code=404, detail="指定的信用卡不存在")

    # 同步更新相同銀行的所有卡片結帳日
    bank_name = card.bank_name
    same_bank_cards_result = await db.execute(get_same_bank_user_cards_query(bank_name, current_user.id))
    apply_billing_cycle_to_cards(same_bank_cards_result.scalars().all(), payload.billing_cycle_date)

    user_card = UserCard(card_id=payload.card_id, billing_cycle_date=payload.billing_cycle_date, user_id=current_user.id)
    db.add(user_card)
    await db.commit()
    await db.refresh(user_card)

    # 重新載入關聯資料以回傳完整結果
    reloaded_user_card = await get_user_card_by_id(db, user_card.id, current_user.id)
    if not reloaded_user_card:
        raise HTTPException(status_code=404, detail="找不到指定的使用者信用卡設定")
    return reloaded_user_card

@router.patch("/user-cards/{user_card_id}", response_model=UserCardOut, summary="更新使用者卡片設定")
async def update_user_card(user_card_id: int, payload: UserCardUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    更新使用者信用卡設定（帳單結帳日或啟用狀態）
    """
    result = await db.execute(get_user_card_with_card_only_query(user_card_id, current_user.id))
    user_card = result.scalar_one_or_none()
    if not user_card:
        raise HTTPException(status_code=404, detail="找不到指定的使用者信用卡設定")

    if payload.billing_cycle_date is not None:
        try:
            validate_billing_cycle_date(payload.billing_cycle_date)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        # 同步更新相同銀行的所有卡片結帳日
        bank_name = user_card.card.bank_name
        same_bank_cards_result = await db.execute(get_same_bank_user_cards_query(bank_name, current_user.id))
        apply_billing_cycle_to_cards(same_bank_cards_result.scalars().all(), payload.billing_cycle_date)

    if payload.is_active is not None:
        user_card.is_active = payload.is_active

    await db.commit()

    # 重新載入關聯資料
    fresh = await db.execute(get_user_card_detail_query(user_card_id, current_user.id))
    return fresh.scalar_one()

@router.delete("/user-cards/{user_card_id}", summary="停用使用者信用卡追蹤")
async def deactivate_user_card(user_card_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    停用（軟刪除）指定的使用者信用卡追蹤，保留歷史交易紀錄
    """
    result = await db.execute(select(UserCard).where(UserCard.id == user_card_id, UserCard.user_id == current_user.id))
    user_card = result.scalar_one_or_none()
    if not user_card:
        raise HTTPException(status_code=404, detail="找不到指定的使用者信用卡設定")

    user_card.is_active = False
    await db.commit()
    return {"message": f"已停用卡片追蹤 (user_card_id={user_card_id})"}

@router.post("/sync-benefits", summary="觸發 AI 爬蟲更新信用卡權益")
async def sync_benefits(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """
    非同步觸發 AI 爬蟲，根據 card_profiles 更新權益資料。
    """
    async def run_sync():
        async with db.bind.begin() as conn: # Or we can just use another session but this is a background task... Wait, injecting db into background task in fastapi might be problematic if session is closed.
            pass

    # A better approach for background task with session is to create a new session
    # Let's write the sync logic directly or in a helper.
    background_tasks.add_task(run_sync_task)
    return {"message": "AI 爬蟲同步任務已啟動，將於背景執行"}

async def run_sync_task():
    from app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        print("[SYNC] 啟動信用卡權益同步...")
        
        # 1. 處理個別卡片
        for profile in CARD_PROFILES:
            print(f"[SYNC] 正在處理: {profile['bank_name']} - {profile['card_name']}")
            result_benefits = await scrape_card_benefits(
                card_name=profile["card_name"],
                url=profile["url"],
                instructions=profile["instructions"]
            )
            if not result_benefits:
                print(f"[SYNC] {profile['card_name']} 未取得任何權益或解析失敗")
                continue
                
            # 找到對應的卡片 ID
            stmt = select(Card).where(
                Card.bank_name == profile['bank_name'],
                Card.card_name == profile['card_name']
            )
            card_res = await session.execute(stmt)
            card = card_res.scalar_one_or_none()
            
            if not card:
                print(f"[SYNC] 資料庫找不到對應卡片: {profile['card_name']}，跳過更新")
                continue
                
            # 刪除舊有權益
            await session.execute(delete(CardBenefit).where(CardBenefit.card_id == card.id))
            
            # 更新卡片的來源網址與同步時間
            url = profile["url"]
            card.benefit_url = url if isinstance(url, str) else url[0]
            card.last_synced_at = datetime.now()
            
            # 新增最新權益
            for b in result_benefits:
                new_benefit = CardBenefit(
                    card_id=card.id,
                    channel_name=b.channel_name,
                    base_rate=b.base_rate,
                    bonus_rate=b.bonus_rate,
                    monthly_cap_ntd=b.monthly_cap_ntd,
                    effective_date=date.today()
                )
                session.add(new_benefit)
                
        # 2. 處理 JCB 通用優惠
        print("[SYNC] 正在處理 JCB 組織通用優惠...")
        jcb_benefits = await scrape_card_benefits(
            card_name="JCB 通用優惠",
            url=JCB_SPECIAL_OFFERS["url"],
            instructions=JCB_SPECIAL_OFFERS["instructions"]
        )
        
        if jcb_benefits:
            # 找出所有包含 "JCB" 名稱的卡片
            stmt = select(Card).where(Card.card_name.like("%JCB%"))
            jcb_cards_res = await session.execute(stmt)
            jcb_cards = jcb_cards_res.scalars().all()
            
            for card in jcb_cards:
                for b in jcb_benefits:
                    # 避免重複，可以加個 prefix
                    channel_name = f"[JCB活動] {b.channel_name}"
                    new_benefit = CardBenefit(
                        card_id=card.id,
                        channel_name=channel_name,
                        base_rate=b.base_rate,
                        bonus_rate=b.bonus_rate,
                        monthly_cap_ntd=b.monthly_cap_ntd,
                        effective_date=date.today()
                    )
                    session.add(new_benefit)

        await session.commit()
        print("[SYNC] 信用卡權益同步完成！")
