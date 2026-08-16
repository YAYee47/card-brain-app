import os
import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, delete

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.users import User
from app.models.user_cards import UserCard
from app.models.cards import Card
from app.models.card_benefits import CardBenefit
from app.models.transactions import Transaction
from app.models.monthly_usage import MonthlyUsage
from app.schemas.transactions import OcrResultOut, TransactionCreate, TransactionOut
from app.services.ocr import analyze_image_with_gemini
from app.services.exchange_rate import convert_to_ntd
from app.services.billing_cycle import get_current_billing_cycle
from app.services.user_cards import get_active_user_card

router = APIRouter()

# ── OCR 端點 ──────────────────────────────────────────────────

@router.post("/ocr/receipt", response_model=OcrResultOut, summary="AI 辨識實體收據/外幣收據")
async def ocr_receipt(
    file: UploadFile = File(..., description="收據照片 (JPEG/PNG)")
):
    """
    上傳實體收據或外幣收據照片，由 Gemini Vision 解析金額、幣別、商家與日期。
    """
    image_bytes = await file.read()
    mime_type = file.content_type or "image/jpeg"
    result = await analyze_image_with_gemini(image_bytes, mime_type)
    return OcrResultOut(**result.model_dump())

@router.post("/ocr/screenshot", response_model=OcrResultOut, summary="AI 辨識 LINE Pay / 載具截圖")
async def ocr_screenshot(
    file: UploadFile = File(..., description="LINE Pay / 載具 / 信用卡推播截圖")
):
    image_bytes = await file.read()
    mime_type = file.content_type or "image/png"
    result = await analyze_image_with_gemini(image_bytes, mime_type)
    return OcrResultOut(**result.model_dump())


from app.services.transaction_service import calculate_txn_cashback

# ── 交易記帳端點 ──────────────────────────────────────────────

@router.post("/transactions", response_model=TransactionOut, summary="新增消費記帳（含回饋金精算）")
async def create_transaction(
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_card = await get_active_user_card(db, payload.user_card_id, current_user.id)
    if not user_card:
        raise HTTPException(status_code=404, detail="找不到指定的使用者信用卡")

    card = user_card.card

    ntd_amount, exchange_rate = await convert_to_ntd(payload.original_amount, payload.currency)
    transacted_at = datetime.now()
    if payload.transacted_at:
        try:
            transacted_at = datetime.fromisoformat(payload.transacted_at)
        except ValueError:
            pass

    # 若此卡為整月回溯型 (monthly)，檢查是否需要整月回溯重算
    scope = "daily"
    if card and card.mode_config:
        try:
            mode_cfg = json.loads(card.mode_config)
            scope = mode_cfg.get("scope", "daily")
        except:
            pass

    if scope == "monthly" and payload.card_mode:
        # 回溯更新本月所有該卡的交易 mode
        start_of_month = transacted_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if transacted_at.month == 12:
            next_month = transacted_at.replace(year=transacted_at.year + 1, month=1, day=1)
        else:
            next_month = transacted_at.replace(month=transacted_at.month + 1, day=1)
            
        # 1. 取得該日曆月內的所有交易，更新 card_mode
        all_txns_res = await db.execute(
            select(Transaction)
            .where(
                and_(
                    Transaction.user_card_id == user_card.id,
                    Transaction.transacted_at >= start_of_month,
                    Transaction.transacted_at < next_month
                )
            )
        )
        txns_in_month = all_txns_res.scalars().all()
        
        # 收集受影響的帳單週期
        affected_cycles = set()
        for t in txns_in_month:
            if t.card_mode != payload.card_mode:
                t.card_mode = payload.card_mode
            c_start, c_end = get_current_billing_cycle(user_card.billing_cycle_date, t.transacted_at.date())
            affected_cycles.add((c_start, c_end))
        
        # 也要把當前這筆新交易的週期加進去
        c_start, c_end = get_current_billing_cycle(user_card.billing_cycle_date, transacted_at.date())
        affected_cycles.add((c_start, c_end))

        # 2. 刪除所有受影響帳單週期的 MonthlyUsage
        for cycle_start, cycle_end in affected_cycles:
            await db.execute(
                delete(MonthlyUsage).where(
                    and_(
                        MonthlyUsage.user_card_id == user_card.id,
                        MonthlyUsage.cycle_start_date == cycle_start,
                        MonthlyUsage.cycle_end_date == cycle_end
                    )
                )
            )
        
        # 3. 取得所有在受影響週期內的交易，準備重算
        all_txns_to_recalc = set()
        for cycle_start, cycle_end in affected_cycles:
            # 轉換為 datetime
            start_dt = datetime(cycle_start.year, cycle_start.month, cycle_start.day)
            end_dt = datetime(cycle_end.year, cycle_end.month, cycle_end.day, 23, 59, 59)
            cycle_txns_res = await db.execute(
                select(Transaction)
                .where(
                    and_(
                        Transaction.user_card_id == user_card.id,
                        Transaction.transacted_at >= start_dt,
                        Transaction.transacted_at <= end_dt
                    )
                )
            )
            for t in cycle_txns_res.scalars().all():
                all_txns_to_recalc.add(t)

        benefits_result = await db.execute(select(CardBenefit).where(CardBenefit.card_id == user_card.card_id))
        benefits = benefits_result.scalars().all()
        
        # 依照時間排序重算，以正確累積 MonthlyUsage
        sorted_txns = sorted(list(all_txns_to_recalc), key=lambda x: x.transacted_at)
        for t in sorted_txns:
            await calculate_txn_cashback(t, user_card, benefits, db)

    # 現在處理這筆新交易
    txn = Transaction(
        user_card_id=payload.user_card_id,
        channel_name=payload.channel_name,
        category=payload.category,
        merchant_name=payload.merchant_name,
        original_amount=payload.original_amount,
        currency=payload.currency,
        ntd_amount=ntd_amount,
        exchange_rate=exchange_rate,
        earned_cashback_ntd=0.0,
        source_type=payload.source_type,
        card_mode=payload.card_mode,
        transacted_at=transacted_at,
        user_id=current_user.id,
    )
    db.add(txn)
    await db.flush()

    benefits_result = await db.execute(select(CardBenefit).where(CardBenefit.card_id == user_card.card_id))
    benefits = benefits_result.scalars().all()
    
    await calculate_txn_cashback(txn, user_card, benefits, db)

    await db.commit()
    await db.refresh(txn)

    return TransactionOut(
        id=txn.id,
        user_card_id=txn.user_card_id,
        channel_name=txn.channel_name,
        category=txn.category,
        merchant_name=txn.merchant_name,
        original_amount=float(txn.original_amount),
        currency=txn.currency,
        ntd_amount=float(txn.ntd_amount),
        exchange_rate=float(txn.exchange_rate),
        earned_cashback_ntd=float(txn.earned_cashback_ntd),
        source_type=txn.source_type,
        transacted_at=txn.transacted_at.isoformat(),
    )


@router.get("/transactions", response_model=list[TransactionOut], summary="列出最近記帳紀錄")
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """
    回傳當前使用者最近的消費記帳紀錄。
    """
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.transacted_at.desc())
        .limit(limit)
    )
    txns = result.scalars().all()

    out = []
    for t in txns:
        out.append(TransactionOut(
            id=t.id,
            user_card_id=t.user_card_id,
            channel_name=t.channel_name,
            category=t.category,
            merchant_name=t.merchant_name,
            original_amount=float(t.original_amount),
            currency=t.currency,
            ntd_amount=float(t.ntd_amount),
            exchange_rate=float(t.exchange_rate),
            earned_cashback_ntd=float(t.earned_cashback_ntd),
            source_type=t.source_type,
            transacted_at=t.transacted_at.isoformat(),
        ))
    return out
