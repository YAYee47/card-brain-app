from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cards import Card
from app.models.card_benefits import CardBenefit
from app.models.user_cards import UserCard

# 5 家指定銀行信用卡初始資料
INITIAL_CARDS = [
    {"bank_name": "永豐銀行", "card_name": "DAWHO現金回饋信用卡", "benefit_url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/DAWHO.html"},
    {"bank_name": "永豐銀行", "card_name": "DAWAY卡", "benefit_url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/DAWAY.html"},
    {"bank_name": "永豐銀行", "card_name": "幣倍卡", "benefit_url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/dual-currency-card.html"},
    {"bank_name": "永豐銀行", "card_name": "現金回饋JCB卡", "benefit_url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/cashcardJCB.html"},
    {"bank_name": "台新銀行", "card_name": "Richart 卡", "benefit_url": "https://mkp.taishinbank.com.tw/TsCms/marketing/expose/WM_20251216135929999/index.html"},
    {"bank_name": "玉山銀行", "card_name": "Unicard", "benefit_url": "https://event.esunbank.com.tw/credit/unicard/index.html"},
    {"bank_name": "玉山銀行", "card_name": "熊本熊卡", "benefit_url": "https://event.esunbank.com.tw/credit/kumamon-card/japan-discount.html, https://event.esunbank.com.tw/credit/kumamon-card/japan-discount-paypay.html, https://event.esunbank.com.tw/credit/kumamon-card/taiwan-discount.html, https://event.esunbank.com.tw/credit/kumamon-card/campaign.html"},
    {"bank_name": "聯邦銀行", "card_name": "吉鶴卡", "benefit_url": "https://activity.ubot.com.tw/2026JiHoCard/japan.htm, https://activity.ubot.com.tw/2026JiHoCard/domestic.htm"},
    {"bank_name": "星展銀行", "card_name": "傳說對決聯名卡", "benefit_url": "https://www.dbs.com.tw/personal-zh/cards/dbs-aov/index.html"},
]

INITIAL_BENEFITS = [
    # 永豐 DAWHO現金回饋信用卡 (大戶卡)
    {"card_index": 0, "channel_name": "國內一般消費", "base_rate": 1.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 0, "channel_name": "國外消費", "base_rate": 2.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 0, "channel_name": "指定通路 (大戶等級)", "base_rate": 1.0, "bonus_rate": 5.0, "monthly_cap_ntd": 300.0},

    # 永豐 DAWAY卡 (DAWAY GO)
    {"card_index": 1, "channel_name": "國內一般消費", "base_rate": 1.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 1, "channel_name": "國外消費", "base_rate": 2.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 1, "channel_name": "LINE Pay 國內消費", "base_rate": 1.0, "bonus_rate": 1.0, "monthly_cap_ntd": None},
    {"card_index": 1, "channel_name": "海外實體消費", "base_rate": 2.0, "bonus_rate": 1.0, "monthly_cap_ntd": None},

    # 永豐 幣倍卡
    {"card_index": 2, "channel_name": "國內一般消費", "base_rate": 1.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 2, "channel_name": "國外消費", "base_rate": 2.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 2, "channel_name": "海外實體消費 (需登錄)", "base_rate": 2.0, "bonus_rate": 3.0, "monthly_cap_ntd": 500.0},
    {"card_index": 2, "channel_name": "精選通路", "base_rate": 1.0, "bonus_rate": 4.0, "monthly_cap_ntd": 300.0},

    # 永豐 現金回饋JCB卡
    {"card_index": 3, "channel_name": "國內一般消費", "base_rate": 1.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 3, "channel_name": "國外消費", "base_rate": 2.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 3, "channel_name": "特選通路-網購/百貨/日本 (需登錄)", "base_rate": 1.0, "bonus_rate": 4.0, "monthly_cap_ntd": 300.0},

    # 台新 Richart 卡 (可切換權益方案 7+1)
    {"card_index": 4, "channel_name": "一般消費 (未切換加碼)", "base_rate": 0.3, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 4, "channel_name": "Chill刷 (火鍋/燒肉/追星/串流/運動)", "base_rate": 0.3, "bonus_rate": 9.7, "monthly_cap_ntd": None},
    {"card_index": 4, "channel_name": "Pay 著刷 (台新Pay及台新Pay+)", "base_rate": 0.3, "bonus_rate": 3.5, "monthly_cap_ntd": None},
    {"card_index": 4, "channel_name": "Pay 著刷 (LINE Pay及全盈+Pay)", "base_rate": 0.3, "bonus_rate": 2.0, "monthly_cap_ntd": None},
    {"card_index": 4, "channel_name": "天天刷 (超商/量販/交通)", "base_rate": 0.3, "bonus_rate": 3.5, "monthly_cap_ntd": None},
    {"card_index": 4, "channel_name": "大筆刷 (百貨/Outlet/居家)", "base_rate": 0.3, "bonus_rate": 3.5, "monthly_cap_ntd": None},
    {"card_index": 4, "channel_name": "好饗刷 (餐飲/外送/訂房)", "base_rate": 0.3, "bonus_rate": 3.0, "monthly_cap_ntd": None},
    {"card_index": 4, "channel_name": "數趣刷 (網購/影音)", "base_rate": 0.3, "bonus_rate": 3.5, "monthly_cap_ntd": None},
    {"card_index": 4, "channel_name": "玩旅刷 (海外/航空/旅行社)", "base_rate": 0.3, "bonus_rate": 3.5, "monthly_cap_ntd": None},
    {"card_index": 4, "channel_name": "假日刷 (國內假日不限通路)", "base_rate": 0.3, "bonus_rate": 1.7, "monthly_cap_ntd": None},

    # 玉山 Unicard (舊戶)
    {"card_index": 5, "channel_name": "一般消費", "base_rate": 1.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 5, "channel_name": "百大特店 (簡單選)", "base_rate": 1.0, "bonus_rate": 2.0, "monthly_cap_ntd": 1000.0},
    {"card_index": 5, "channel_name": "百大特店 (任意選)", "base_rate": 1.0, "bonus_rate": 2.5, "monthly_cap_ntd": 1000.0},
    {"card_index": 5, "channel_name": "百大特店 (UP選)", "base_rate": 1.0, "bonus_rate": 3.5, "monthly_cap_ntd": 5000.0},
    
    # 玉山 熊本熊卡 (舊戶)
    {"card_index": 6, "channel_name": "國內一般消費", "base_rate": 1.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 6, "channel_name": "國外消費", "base_rate": 1.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 6, "channel_name": "日本地區消費", "base_rate": 1.0, "bonus_rate": 1.0, "monthly_cap_ntd": None},
    {"card_index": 6, "channel_name": "指定日本商店", "base_rate": 2.0, "bonus_rate": 6.5, "monthly_cap_ntd": 500.0},

    # 聯邦 吉鶴卡 (舊戶)
    {"card_index": 7, "channel_name": "國內一般消費", "base_rate": 1.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 7, "channel_name": "日本消費", "base_rate": 2.5, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 7, "channel_name": "日系名店加碼", "base_rate": 1.0, "bonus_rate": 4.0, "monthly_cap_ntd": 500.0},

    # 星展 傳說對決聯名卡
    {"card_index": 8, "channel_name": "國內一般消費", "base_rate": 1.0, "bonus_rate": 0.0, "monthly_cap_ntd": None},
    {"card_index": 8, "channel_name": "生活玩家精選通路 (App Store/蝦皮/UberEats/Netflix等)", "base_rate": 1.0, "bonus_rate": 9.0, "monthly_cap_ntd": 500.0},
    {"card_index": 8, "channel_name": "日韓泰新美歐實體商店 (含Apple Pay)", "base_rate": 1.0, "bonus_rate": 4.0, "monthly_cap_ntd": 500.0},
]

async def seed_initial_data(session: AsyncSession):
    """
    初始化 Seed 資料：寫入 5 家銀行信用卡基本資料與初始權益規則。
    若資料已存在則跳過，確保冪等性 (idempotent)。
    """
    from sqlalchemy import select

    # 確認是否已有 Seed 資料 (冪等性保護)
    result = await session.execute(select(Card).limit(1))
    if result.scalar_one_or_none() is not None:
        print("[SEED] Seed data already exists, skipping.")
        return

    print("[SEED] Writing initial credit card seed data...")

    # 寫入 Card 主表
    card_objects = []
    for c in INITIAL_CARDS:
        card = Card(bank_name=c["bank_name"], card_name=c["card_name"], benefit_url=c.get("benefit_url"))
        session.add(card)
        card_objects.append(card)

    await session.flush()  # 取得自增 ID

    # 寫入 CardBenefit 權益規則
    for b in INITIAL_BENEFITS:
        card = card_objects[b["card_index"]]
        benefit = CardBenefit(
            card_id=card.id,
            channel_name=b["channel_name"],
            base_rate=b["base_rate"],
            bonus_rate=b["bonus_rate"],
            monthly_cap_ntd=b["monthly_cap_ntd"],
            effective_date=date(2025, 1, 1),  # 初始資料生效日
        )
        session.add(benefit)

    # 寫入 UserCard 持有卡片記錄
    billing_dates = {
        0: 18, 1: 18, 2: 18, 3: 18, # 永豐
        4: 7,                       # 台新
        5: 7, 6: 7,                 # 玉山
        7: 12,                      # 聯邦
        8: 10                       # 星展
    }
    for i, card in enumerate(card_objects):
        uc = UserCard(
            card_id=card.id,
            billing_cycle_date=billing_dates.get(i, 15)
        )
        session.add(uc)

    await session.commit()
    print(f"[SEED] Inserted {len(INITIAL_CARDS)} cards, {len(INITIAL_BENEFITS)} benefit rules, and auto-assigned {len(card_objects)} user cards.")
