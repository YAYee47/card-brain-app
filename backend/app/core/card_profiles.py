# 信用卡爬蟲專屬設定檔
# 對應使用者實際持卡狀況與身分
# 共通前提：使用者所有卡片都已設定「帳戶自動轉帳扣繳」+「電子帳單」

CARD_PROFILES = [
    {
        "bank_name": "永豐銀行",
        "card_name": "大戸卡",  # 注意這裡使用了與 DB seed 一致的名稱
        "url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/DAWHO.html",
        "instructions": (
            "使用者為舊戶，且擁有『大戶資格』，已設定自動扣繳與電子帳單。"
            "請忽略新戶專屬加碼。"
            "國內基礎回饋 1% 與國外基礎回饋 2% 是無上限的。"
            "monthly_cap_ntd 只填加碼回饋的每期封頂金額。"
            "請列出所有適用的加碼通路與具體商家名稱。"
            "若有活動標示『已額滿』或『登錄已額滿』，請不要列出。"
        )
    },
    {
        "bank_name": "永豐銀行",
        "card_name": "現金回饋JCB卡",
        "url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/cashcardJCB.html",
        "instructions": (
            "使用者為舊戶，已設定自動扣繳與電子帳單。"
            "請忽略新戶專屬加碼。"
            "國內基礎回饋 1% 與國外基礎回饋 2% 是無上限的。"
            "monthly_cap_ntd 只填加碼回饋的每期封頂金額。"
            "請列出所有特選通路的具體商家名稱（如：蝦皮/momo/百貨公司名稱/全支付等）。"
            "不要列出 JCB APP 限定活動（如需透過 MyJapan+ APP 登錄的活動）。"
            "若有活動標示『已額滿』或『登錄已額滿』，請不要列出該活動。"
        )
    },
    {
        "bank_name": "永豐銀行",
        "card_name": "幣倍卡",
        "url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/dual-currency-card.html",
        "instructions": (
            "使用者為舊戶，持有『日圓雙幣卡』，已設定自動扣繳與電子帳單。"
            "請忽略新戶專屬加碼。"
            "國內基礎回饋 1% 與國外基礎回饋 2% 是無上限的。"
            "monthly_cap_ntd 只填加碼回饋的每期封頂金額。"
            "請列出精選通路的具體商家名稱。"
            "若有活動標示『已額滿』或『登錄已額滿』，請不要列出該活動。"
        )
    },
    {
        "bank_name": "永豐銀行",
        "card_name": "大衛卡",  # DAWAY卡
        "url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/DAWAY.html",
        "instructions": (
            "使用者為舊戶，已設定自動扣繳與電子帳單。"
            "使用者為 DAWAY GO 等級（已升級至 GO 等級）。"
            "請忽略新戶專屬加碼。"
            "國內基礎回饋與國外基礎回饋是無上限的。"
            "monthly_cap_ntd 只填加碼回饋的每期封頂金額。"
            "請列出所有適用通路的具體商家名稱（包含 LINE Pay 綁定的指定通路）。"
            "若有活動標示『已額滿』或『登錄已額滿』，請不要列出該活動。"
        )
    },
    {
        "bank_name": "玉山銀行",
        "card_name": "Uni 卡",
        "url": "https://event.esunbank.com.tw/credit/unicard/index.html",
        "instructions": (
            "使用者為舊戶，已設定自動扣繳與電子帳單。"
            "方案預設為『任意選』。但若使用條件顯示消費大於 14900 且 149 點玉山 e point 扣抵划算時，可升級為『UP 選』。"
            "請忽略新戶專屬加碼。"
            "國內基礎回饋 1% 是無上限的。"
            "monthly_cap_ntd 只填加碼回饋的每期封頂金額。"
            "百大指定消費的具體商家/通路請盡量列出（如：蝦皮/momo/全聯/家樂福/Netflix 等，越具體越好）。"
            "若有活動標示『已額滿』或『登錄已額滿』，請不要列出該活動。"
        )
    },
    {
        "bank_name": "玉山銀行",
        "card_name": "熊本熊JCB卡",
        "url": [
            "https://event.esunbank.com.tw/credit/kumamon-card/japan-discount.html",
            "https://event.esunbank.com.tw/credit/kumamon-card/japan-discount-paypay.html",
            "https://event.esunbank.com.tw/credit/kumamon-card/taiwan-discount.html",
            "https://event.esunbank.com.tw/credit/kumamon-card/campaign.html",
        ],
        "instructions": (
            "使用者為舊戶，持有『向左左版日圓雙幣卡』，已設定自動扣繳與電子帳單。"
            "請忽略新戶加碼。"
            "此卡在日本消費確實會被收取 1.5% 海外交易手續費，請不要把它當成回饋。"
            "如果有「免收海外交易手續費」或「回饋抵海外手續費」的活動，請獨立列出為『國外交易手續費減免』。"
            "國內基礎回饋 1% 是無上限的。"
            "monthly_cap_ntd 只填加碼回饋的每期封頂金額。"
            "請綜合多個網頁的資訊（日本優惠、PayPay 合作、台灣優惠、登錄活動）來完整提取權益。"
            "若有活動標示『已額滿』或『登錄已額滿』，請不要列出該活動。"
            "登錄活動頁面(campaign)中的活動如果需要每半年登錄，請在 channel_name 中加註『(需登錄)』。"
        )
    },
    {
        "bank_name": "台新銀行",
        "card_name": "Richart 卡",
        "url": "https://mkp.taishinbank.com.tw/TsCms/marketing/expose/WM_20251216135929999/index.html",
        "instructions": (
            "使用者為舊戶，已設定自動扣繳與電子帳單。"
            "持有 Visa 和 Mastercard 共兩張。"
            "這是一張可以切換『天天刷/大筆刷/Chill刷/數趣刷/好饗刷/Pay著刷/玩旅刷/假日刷』等多種方案的卡。"
            "請將所有方案的回饋通路與回饋率全部列出，每個方案一筆或多筆記錄。"
            "channel_name 格式為：『方案名稱 - 具體通路/商家名稱』，例如：『Chill刷 - 蝦皮/momo/淘寶/酷澎/Uber Eats』。"
            "請盡量列出每個方案下的具體商家名稱。"
            "請忽略新戶加碼。"
            "若有活動標示『已額滿』或『登錄已額滿』，請不要列出該活動。"
        )
    },
    {
        "bank_name": "星展銀行",
        "card_name": "傳說對決聯名卡",
        "url": "https://www.dbs.com.tw/personal-zh/cards/dbs-aov/index.html",
        "instructions": (
            "使用者為舊戶，已設定指定星展帳戶自動轉帳扣繳與電子帳單。"
            "請忽略新戶專屬加碼。"
            "國內基礎回饋 1% 是無上限的。"
            "monthly_cap_ntd 只填加碼回饋的每期封頂金額。"
            "請列出「生活玩家精選通路」和「指定國家實體消費」的具體商家/通路名稱。"
            "例如：App Store/Google Play/Steam/Netflix/Uber Eats/蝦皮/momo 等。"
            "若有活動標示『已額滿』或『登錄已額滿』，請不要列出該活動。"
        )
    },
    {
        "bank_name": "聯邦銀行",
        "card_name": "吉鶴卡",
        "url": "https://activity.ubot.com.tw/2026JiHoCard/index.htm",
        "instructions": (
            "使用者為舊戶，已設定自動扣繳與電子帳單。"
            "請忽略新戶專屬加碼。"
            "請列出國內外一般消費基礎回饋與各通路加碼。"
            "基礎回饋是無上限的。"
            "monthly_cap_ntd 只填加碼回饋的每期封頂金額。"
            "請列出具體的加碼通路與商家名稱。"
            "若有活動標示『已額滿』或『登錄已額滿』，請不要列出該活動。"
        )
    }
]

# JCB 組織專屬活動 (Global) — 僅供展示，不參與消費決策比價
JCB_SPECIAL_OFFERS = {
    "url": "https://www.specialoffers.jcb/zh-tw/",
    "instructions": (
        "請提取 JCB 組織近期的所有信用卡共通刷卡優惠活動。"
        "提取各活動的通路名稱（要具體，例如 BicCamera/大國藥妝/Agoda 等）、"
        "加碼回饋率（或等值回饋%數）與每月/每季上限。"
        "這些優惠僅供展示，不參與消費決策比價。"
        "不要列出需要透過 JCB APP（如 MyJapan+）登錄的活動。"
    ),
    "is_display_only": True  # 標記為僅展示，不參與推薦比價
}
