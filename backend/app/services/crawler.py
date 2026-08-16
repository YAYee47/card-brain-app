import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class FetchedBenefit:
    """爬蟲取得的最新權益資料"""
    card_id: int
    channel_name: str
    base_rate: float
    bonus_rate: float
    monthly_cap_ntd: Optional[float]


def simulate_crawl(existing_benefits: list) -> list[FetchedBenefit]:
    """
    模擬爬蟲從銀行官網取得最新信用卡權益資料。

    實際部署時，此函式應改為使用 httpx + BeautifulSoup / Playwright
    爬取各銀行信用卡優惠頁面，並解析出各通道回饋率與加碼上限。

    MVP 模擬策略：
    - 90% 機率：維持現有數值（無變動）
    - 7% 機率：加碼回饋率微幅調整 (±0.5%)
    - 3% 機率：月消費上限調整 (±1000 NTD)
    """
    fetched: list[FetchedBenefit] = []

    for b in existing_benefits:
        roll = random.random()
        new_bonus = float(b.bonus_rate)
        new_cap = float(b.monthly_cap_ntd) if b.monthly_cap_ntd else None

        if roll < 0.03:
            # 小機率：加碼回饋率調整
            delta = random.choice([-0.5, 0.5])
            new_bonus = max(0.0, round(new_bonus + delta, 1))
        elif roll < 0.06:
            # 小機率：月消費上限調整
            if new_cap is not None:
                delta = random.choice([-1000, 1000])
                new_cap = max(0.0, new_cap + delta)

        fetched.append(FetchedBenefit(
            card_id=b.card_id,
            channel_name=b.channel_name,
            base_rate=float(b.base_rate),
            bonus_rate=new_bonus,
            monthly_cap_ntd=new_cap,
        ))

    return fetched
