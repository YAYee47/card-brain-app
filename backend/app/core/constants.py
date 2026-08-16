import json
import os

# 台灣常見場景字典
SMART_DICTIONARY = {
    "超商": ["全家", "7-11", "7-eleven", "萊爾富", "ok超商"],
    "超市": ["全聯", "家樂福", "大潤發", "愛買", "美廉社"],
    "加油": ["中油", "全國加油站", "台亞", "福懋", "加油"],
    "交通": ["高鐵", "台鐵", "客運", "捷運", "公車", "uber", "yoxi", "台灣大車隊", "計程車"],
    "餐飲": ["星巴克", "麥當勞", "肯德基", "摩斯", "路易莎", "餐廳", "餐飲", "飲料", "五十嵐", "可不可"],
    "外送": ["uber eats", "foodpanda", "外送"],
    "網購": ["momo", "pchome", "yahoo", "博客來", "酷澎", "coupong", "網購"],
    "蝦皮": ["蝦皮", "shopee"],
    "淘寶": ["淘寶", "taobao"],
    "行動支付": ["apple pay", "google pay", "samsung pay", "line pay", "街口", "台灣pay", "悠遊付", "icash pay", "全盈", "全支付"],
    "影音": ["netflix", "disney", "spotify", "youtube", "kkbox", "愛奇藝"],
    "遊戲": ["app store", "google play", "steam", "playstation", "nintendo", "遊戲"],
    "海外": ["日本", "韓國", "泰國", "國外", "海外", "外幣"],
    "日系名店": ["lakole", "uniqlo", "gu", "無印良品", "muji", "大創", "daiso", "宜得利", "nitori", "日系名店"]
}

UNICARD_MERCHANTS = []
try:
    merchants_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "unicard_merchants.json")
    with open(merchants_path, "r", encoding="utf-8") as f:
        UNICARD_MERCHANTS = json.load(f)
except Exception as e:
    pass
