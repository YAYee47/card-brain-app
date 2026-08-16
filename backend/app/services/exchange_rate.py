import httpx
from datetime import date
from typing import Optional

# 匯率快取 (程式生命週期內有效，避免頻繁 API 呼叫)
_rate_cache: dict[str, tuple[float, date]] = {}

# 常用幣別備援匯率 (當 API 不可用時使用)
FALLBACK_RATES: dict[str, float] = {
    "TWD": 1.0,
    "USD": 32.5,
    "JPY": 0.22,
    "EUR": 35.8,
    "GBP": 41.5,
    "HKD": 4.2,
    "SGD": 24.5,
    "KRW": 0.024,
    "AUD": 21.0,
    "CNY": 4.5,
}

async def get_exchange_rate_to_twd(currency: str) -> float:
    """
    取得指定幣別對台幣 (TWD) 的匯率。
    優先使用 ExchangeRate-API 免費端點，失敗時 fallback 至內建備援匯率。
    """
    currency = currency.upper()
    if currency == "TWD":
        return 1.0

    today = date.today()
    # 使用快取
    if currency in _rate_cache:
        rate, cached_date = _rate_cache[currency]
        if cached_date == today:
            return rate

    # 嘗試呼叫免費匯率 API (無需 key)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"https://open.er-api.com/v6/latest/{currency}"
            )
            if resp.status_code == 200:
                data = resp.json()
                twd_rate = data["rates"].get("TWD")
                if twd_rate:
                    _rate_cache[currency] = (float(twd_rate), today)
                    return float(twd_rate)
    except Exception:
        pass  # 網路錯誤時使用備援值

    # Fallback 到內建備援匯率
    rate = FALLBACK_RATES.get(currency, 30.0)
    _rate_cache[currency] = (rate, today)
    return rate

async def convert_to_ntd(amount: float, currency: str) -> tuple[float, float]:
    """
    將原始金額轉換為台幣。
    回傳 (台幣金額, 採用匯率)
    """
    rate = await get_exchange_rate_to_twd(currency)
    ntd = round(amount * rate, 2)
    return ntd, rate
