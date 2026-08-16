import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# 全域排程器實例（在 main.py lifespan 中啟動與關閉）
scheduler = AsyncIOScheduler(timezone="Asia/Taipei")


def setup_scheduler(db_session_factory):
    """
    設定定時排程任務：
    - 每月 1 日 00:05 執行爬蟲與差異比對
    - 每日 09:00 掃描額度使用量並產生警報
    """
    from app.services.diff_engine import run_crawl_and_diff, check_quota_warnings

    async def monthly_crawl_job():
        """月初爬蟲任務"""
        logger.info("[Scheduler] 月初爬蟲任務啟動...")
        async with db_session_factory() as db:
            result = await run_crawl_and_diff(db)
            logger.info(f"[Scheduler] 爬蟲完成：{result}")

    async def daily_quota_check():
        """每日額度警告掃描"""
        logger.info("[Scheduler] 每日額度警告掃描中...")
        async with db_session_factory() as db:
            count = await check_quota_warnings(db)
            logger.info(f"[Scheduler] 額度警報產生：{count} 條")

    # 每季 (1,4,7,10月) 1 日 00:05 爬蟲
    scheduler.add_job(
        monthly_crawl_job,
        CronTrigger(month='1,4,7,10', day=1, hour=0, minute=5),
        id="monthly_crawl",
        replace_existing=True,
        name="每季信用卡權益爬蟲",
    )

    # 每日 09:00 額度掃描
    scheduler.add_job(
        daily_quota_check,
        CronTrigger(hour=9, minute=0),
        id="daily_quota_check",
        replace_existing=True,
        name="每日額度警告掃描",
    )

    logger.info("[Scheduler] 排程任務已設定：月初爬蟲 + 每日額度掃描")
