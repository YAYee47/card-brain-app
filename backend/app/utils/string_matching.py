from app.core.constants import SMART_DICTIONARY, UNICARD_MERCHANTS

def build_search_keywords(channel_name: str) -> list[str]:
    """將前端長字串映射成資料庫權益規則的關鍵字"""
    search_keywords = [channel_name]
    
    # 判斷是否為玉山百大特店
    for m in UNICARD_MERCHANTS:
        if channel_name.lower() in m.lower() or m.lower() in channel_name.lower():
            search_keywords.append("百大")
            search_keywords.append("百大指定消費")
            break

    channel_lower = channel_name.lower()

    # 智慧對應
    for category, keywords in SMART_DICTIONARY.items():
        for k in keywords:
            if k in channel_lower:
                # 特別排除：避免 "uber eats" 觸發 "uber" (交通)
                if k == "uber" and "uber eats" in channel_lower:
                    continue
                search_keywords.append(category)
                # 若為行動支付或特定關鍵字，同時也把原輸入字串保留
                search_keywords.append(k)
    
    # 保留原有的精確 Pay 判斷
    if "apple pay" in channel_lower:
        search_keywords.append("Apple Pay")
    if "line pay" in channel_lower:
        search_keywords.append("LINE Pay")
    if "街口" in channel_lower:
        search_keywords.append("街口")
        
    return search_keywords

def is_benefit_matched(b, search_keywords: list[str], channel_name: str, exclude_registration: bool) -> bool:
    """判斷某條權益是否與當次消費通路相符"""
    # 跳過 JCB 組織活動（僅供展示，不參與比價）
    if b.channel_name.startswith("[JCB活動]"):
        return False
    # 跳過「國外交易手續費減免」（這是費用減免，不是消費回饋）
    if "手續費減免" in b.channel_name:
        return False
    # 排除需登錄才能享有的權益（依參數決定）
    if exclude_registration and "(需登錄)" in b.channel_name:
        return False
        
    # --- 使用者自訂限制條件 ---
    # 1. 不是新戶 -> 排除含有「新戶」的規則
    if "新戶" in b.channel_name:
        return False
    # 3. 永豐大戶等級 -> 排除「大大等級」
    if "大大等級" in b.channel_name:
        return False
    # 4. 玉山 Unicard 用任意選與UP選 -> 排除「簡單選」
    if "簡單選" in b.channel_name:
        return False
    # 5. 永豐 DAWAY 卡 -> 排除「DAWAY VIP」或其他等級，保留「DAWAY GO」
    if "DAWAY" in b.channel_name and "VIP" in b.channel_name:
        return False
        
    # 6. LINE Pay 默認國內 -> 若查詢為 LINE Pay，排除國外/日本/韓國/海外
    if "LINE Pay" in search_keywords:
        if any(k in b.channel_name for k in ["海外", "國外", "日本", "韓國", "泰國", "境外"]):
            return False
            
    # 7. 避免 Uber 誤判為 Uber Eats
    search_keywords_lower = [k.lower() for k in search_keywords]
    if "uber" in search_keywords_lower and "uber eats" not in search_keywords_lower:
        if "uber eats" in b.channel_name.lower():
            return False

    # 8. 避免通用「交通」誤判為日本專屬交通卡
    channel_lower = channel_name.lower()
    if "交通" in search_keywords:
        if "日本三大交通卡" in b.channel_name and not any(k in channel_lower for k in ["suica", "pasmo", "icoca", "日本", "交通卡"]):
            return False

    # ------------------------
    if any(k.lower() in b.channel_name.lower() or k == b.channel_name for k in search_keywords):
        return True
        
    return False
