import json
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card_benefits import CardBenefit
from app.models.user_cards import UserCard
from app.models.monthly_usage import MonthlyUsage
from app.models.alerts import AppAlert, BenefitSnapshot
from app.services.crawler import simulate_crawl, FetchedBenefit
from app.services.billing_cycle import get_current_billing_cycle
from app.schemas.alerts import AlertOut


def serialize_alerts(alerts: list) -> list[AlertOut]:
    """Map ORM alert rows to the API response schema without changing payload shape."""
    return [
        AlertOut(
            id=a.id,
            alert_type=a.alert_type,
            severity=a.severity,
            card_id=a.card_id,
            user_card_id=a.user_card_id,
            title=a.title,
            body=a.body,
            diff_detail=a.diff_detail,
            is_read=a.is_read,
            created_at=a.created_at.isoformat(),
        )
        for a in alerts
    ]


async def run_crawl_and_diff(db: AsyncSession) -> dict:
    """
    爬蟲差異比對引擎主函式：
    1. 從 DB 讀取現有權益資料
    2. 呼叫爬蟲取得最新權益（MVP 使用模擬）
    3. 比對新舊差異，對有變動的欄位產生 BENEFIT_CHANGE 警報
    4. 將新的權益資料寫回 card_benefits 表
    5. 儲存本次快照至 benefit_snapshots 表
    回傳執行摘要。
    """
    # 1. 取得現有所有權益
    result = await db.execute(select(CardBenefit))
    existing_benefits = result.scalars().all()

    if not existing_benefits:
        return {"status": "no_benefits", "alerts_created": 0}

    # 2. 模擬爬蟲抓取
    fetched_list = simulate_crawl(existing_benefits)

    alerts_created = 0
    updated_count = 0

    # 建立查找字典
    existing_map = {
        (b.card_id, b.channel_name): b for b in existing_benefits
    }

    for fetched in fetched_list:
        key = (fetched.card_id, fetched.channel_name)
        old = existing_map.get(key)
        if not old:
            continue

        diffs: list[str] = []

        # 比對加碼回饋率
        old_bonus = round(float(old.bonus_rate), 2)
        new_bonus = round(fetched.bonus_rate, 2)
        if abs(old_bonus - new_bonus) >= 0.1:
            diffs.append(f"加碼回饋率：{old_bonus}% → {new_bonus}%")

        # 比對月消費上限
        old_cap = float(old.monthly_cap_ntd) if old.monthly_cap_ntd else None
        new_cap = fetched.monthly_cap_ntd
        if old_cap != new_cap:
            old_cap_str = f"NT${old_cap:,.0f}" if old_cap else "無上限"
            new_cap_str = f"NT${new_cap:,.0f}" if new_cap else "無上限"
            diffs.append(f"加碼上限：{old_cap_str} → {new_cap_str}")

        if diffs:
            # 3. 產生差異警報
            diff_detail = json.dumps({
                "card_id": fetched.card_id,
                "channel": fetched.channel_name,
                "changes": diffs,
            }, ensure_ascii=False)

            alert = AppAlert(
                alert_type="BENEFIT_CHANGE",
                severity="WARNING",
                card_id=fetched.card_id,
                title=f"信用卡權益異動通知",
                body=f"通道「{fetched.channel_name}」權益有更新：{' / '.join(diffs)}",
                diff_detail=diff_detail,
            )
            db.add(alert)
            alerts_created += 1

            # 4. 更新 card_benefits 資料
            old.bonus_rate = fetched.bonus_rate
            old.monthly_cap_ntd = fetched.monthly_cap_ntd
            updated_count += 1

        # 5. 儲存快照
        snapshot = BenefitSnapshot(
            card_id=fetched.card_id,
            channel_name=fetched.channel_name,
            base_rate=fetched.base_rate,
            bonus_rate=fetched.bonus_rate,
            monthly_cap_ntd=fetched.monthly_cap_ntd,
            source="CRAWLER",
        )
        db.add(snapshot)

    await db.commit()
    return {
        "status": "done",
        "checked": len(fetched_list),
        "updated": updated_count,
        "alerts_created": alerts_created,
        "run_at": datetime.now().isoformat(),
    }


async def check_quota_warnings(db: AsyncSession) -> int:
    """
    掃描所有啟用中使用者卡片的當前帳單週期額度使用量，
    對 >= 80% 產生 QUOTA_WARNING 警報，對 >= 100% 產生 QUOTA_CAPPED 警報。
    避免重複：只在今日尚未產生過相同警報時才新增。
    """
    from datetime import date
    today_str = date.today().isoformat()

    result = await db.execute(select(UserCard).where(UserCard.is_active == True))
    user_cards = result.scalars().all()

    alerts_created = 0
    for uc in user_cards:
        cycle_start, cycle_end = get_current_billing_cycle(uc.billing_cycle_date)

        usage_result = await db.execute(
            select(MonthlyUsage).where(
                and_(
                    MonthlyUsage.user_card_id == uc.id,
                    MonthlyUsage.cycle_start_date == cycle_start,
                )
            )
        )
        usage = usage_result.scalar_one_or_none()
        if not usage:
            continue

        used_ntd = float(usage.used_amount_ntd)

        # 取此卡片所有有上限的通道
        benefits_result = await db.execute(
            select(CardBenefit).where(
                and_(CardBenefit.card_id == uc.card_id, CardBenefit.monthly_cap_ntd.isnot(None))
            )
        )
        benefits = benefits_result.scalars().all()

        for b in benefits:
            cap = float(b.monthly_cap_ntd)
            if cap <= 0:
                continue
            pct = used_ntd / cap * 100

            alert_type = None
            severity = None
            if pct >= 100:
                alert_type = "QUOTA_CAPPED"
                severity = "CRITICAL"
                title = "加碼額度已滿！"
                body = f"您的「{b.channel_name}」加碼額度 NT${cap:,.0f} 已全部消耗完畢，本月剩餘消費改以基礎回饋 {float(b.base_rate)}% 計算。"
            elif pct >= 80:
                alert_type = "QUOTA_WARNING"
                severity = "WARNING"
                title = "加碼額度即將達上限"
                body = f"「{b.channel_name}」加碼額度已使用 {pct:.0f}%（NT${used_ntd:,.0f} / NT${cap:,.0f}），建議改用其他卡片消費。"

            if not alert_type:
                continue

            # 防止今日重複警報
            existing_alert = await db.execute(
                select(AppAlert).where(
                    and_(
                        AppAlert.user_card_id == uc.id,
                        AppAlert.alert_type == alert_type,
                        AppAlert.created_at >= datetime.combine(date.today(), datetime.min.time()),
                    )
                )
            )
            if existing_alert.scalar_one_or_none():
                continue

            db.add(AppAlert(
                alert_type=alert_type,
                severity=severity,
                card_id=uc.card_id,
                user_card_id=uc.id,
                title=title,
                body=body,
            ))
            alerts_created += 1

    if alerts_created:
        await db.commit()
    return alerts_created
