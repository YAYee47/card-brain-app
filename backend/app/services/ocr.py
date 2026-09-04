import os
import base64
from typing import Optional
from pydantic import BaseModel

class OcrResult(BaseModel):
    """AI 視覺辨識結果"""
    amount: Optional[float] = None
    currency: str = "TWD"
    merchant_name: Optional[str] = None
    transaction_date: Optional[str] = None  # YYYY-MM-DD
    channel_name: Optional[str] = None
    category: Optional[str] = None
    confidence: str = "low"  # low / medium / high
    raw_text: Optional[str] = None

GEMINI_SYSTEM_PROMPT = """
你是一個專業的消費收據 OCR 辨識助手。請分析圖片內容，提取以下欄位並以 JSON 格式回傳，不要加任何額外說明文字：

{
  "amount": <數字，原始幣別金額>,
  "currency": <幣別代碼，如 TWD/JPY/KRW/CNY/USD，預設 TWD>,
  "merchant_name": <商家名稱，若無法辨識填 null>,
  "transaction_date": <交易日期 YYYY-MM-DD 格式，若無法辨識填 null>,
  "channel_name": <支付通道，如：Apple Pay/LINE Pay/信用卡/現金，若無法辨識填 null>,
  "category": <消費分類，從以下選一個：餐飲/購物/交通/數位網購/娛樂/固定支出/其他>,
  "confidence": <辨識信心度：low/medium/high>
}

注意：
- 速度非常重要，若截圖中無法明顯看出商家(如蝦皮)或支付通道，請直接果斷填 null，不要憑空捏造或猜測！讓使用者自己手動填寫。
- 若是台灣電子收據，currency 填 TWD
- 若是 LINE Pay 截圖，channel_name 填 LINE Pay
- 若是 Apple Pay 截圖，channel_name 填 Apple Pay
- 金額請取最終消費總額（含稅）
"""

from app.core.config import settings

async def analyze_image_with_gemini(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    api_key: Optional[str] = None,
) -> OcrResult:
    """
    呼叫 Gemini Vision API 辨識收據/截圖圖片，提取消費資訊。
    若無 API Key 或呼叫失敗，回傳空結果供使用者手動補填。
    """
    key = api_key or settings.GEMINI_API_KEY
    if not key:
        return OcrResult(
            confidence="low",
            raw_text="[GEMINI_API_KEY 未設定，請在 .env 檔案中設定 GEMINI_API_KEY]"
        )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                types.Content(parts=[
                    types.Part(text=GEMINI_SYSTEM_PROMPT),
                    types.Part(inline_data=types.Blob(
                        mime_type=mime_type,
                        data=image_b64,
                    )),
                ])
            ],
            config=types.GenerateContentConfig(temperature=0.0),
        )

        import json, re
        raw = response.text.strip()
        # 清除 markdown 程式碼區塊包裹（```json ... ```）
        raw = re.sub(r"^```[a-z]*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        parsed = json.loads(raw)
        return OcrResult(**{k: v for k, v in parsed.items() if k in OcrResult.model_fields})

    except Exception as e:
        return OcrResult(
            confidence="low",
            raw_text=f"[辨識失敗: {str(e)[:100]}]"
        )
