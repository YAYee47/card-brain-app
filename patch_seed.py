import os
import re

fp = r'backend\app\db\seed.py'
with open(fp, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove icon_emoji from INITIAL_CARDS dicts
content = re.sub(r', "icon_emoji": "[^"]+"', '', content)

# Modify INITIAL_CARDS to include benefit_url
replacements = {
    '"card_name": "DAWHO現金回饋信用卡"': '"card_name": "DAWHO現金回饋信用卡", "benefit_url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/DAWHO.html"',
    '"card_name": "DAWAY卡"': '"card_name": "DAWAY卡", "benefit_url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/DAWAY.html"',
    '"card_name": "幣倍卡"': '"card_name": "幣倍卡", "benefit_url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/dual-currency-card.html"',
    '"card_name": "現金回饋JCB卡"': '"card_name": "現金回饋JCB卡", "benefit_url": "https://bank.sinopac.com/sinopacbt/personal/credit-card/introduction/bankcard/cashcardJCB.html"',
    '"card_name": "Richart 卡"': '"card_name": "Richart 卡", "benefit_url": "https://mkp.taishinbank.com.tw/TsCms/marketing/expose/WM_20251216135929999/index.html"',
    '"card_name": "Unicard"': '"card_name": "Unicard", "benefit_url": "https://event.esunbank.com.tw/credit/unicard/index.html"',
    '"card_name": "熊本熊卡"': '"card_name": "熊本熊卡", "benefit_url": "https://event.esunbank.com.tw/credit/kumamon-card/japan-discount.html"',
    '"card_name": "吉鶴卡"': '"card_name": "吉鶴卡", "benefit_url": "https://activity.ubot.com.tw/2026JiHoCard/index.htm"',
    '"card_name": "傳說對決聯名卡"': '"card_name": "傳說對決聯名卡", "benefit_url": "https://www.dbs.com.tw/personal-zh/cards/dbs-aov/index.html"',
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Fix instantiation: remove icon_emoji, add benefit_url
content = content.replace('card_name=c["card_name"], icon_emoji=c["icon_emoji"]', 'card_name=c["card_name"], benefit_url=c.get("benefit_url")')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(content)
