# ☁️ 雲端架構與部署環境變數手冊 (Cloud Deployment & Environment Variables)

本手冊詳細記錄 Card Brain App 的雲端架構、資料庫連線、各平台環境變數配置與維運資訊。

---

## 🏛️ 1. 系統整體雲端架構

```mermaid
graph TD
    A["📱 iOS / Android (Expo Go / 實機 App)"] -->|HTTPS API 請求| B["☁️ Render.com (FastAPI 後端)"]
    B -->|AsyncPG (PostgreSQL)| C[("🐘 Neon.tech (雲端 PostgreSQL 資料庫)")]
    B -->|Vision OCR| D["🤖 Google Gemini 2.5 Flash API"]
    B -->|即時匯率| E["💱 Exchange Rate API"]
```

---

## 🐘 2. 雲端資料庫配置 (Neon PostgreSQL)

- **服務商**：[Neon.tech](https://neon.tech/) (Serverless Postgres)
- **方案**：Free Tier (0.5 GB 永久儲存空間，閒置時 CPU 休眠節能)
- **地區 (Region)**：`ap-southeast-1` (Singapore 新加坡)
- **連線字串 (Connection String)**：
  ```text
  postgresql://neondb_owner:npg_IW1dt5pAgyFU@ep-aged-moon-aznivm4q.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
  ```
- **資料庫遷移腳本**：`backend/migrate_sqlite_to_pg.py` (可隨時從 SQLite 備份檔 `card_brain_backup.db` 重新執行無損遷移)

---

## ☁️ 3. 後端 API 伺服器配置 (Render.com)

- **服務商**：[Render.com](https://render.com/)
- **服務類型**：Web Service (Python 3)
- **專案名稱**：`card-brain-app`
- **公開 API 網址**：[`https://card-brain-app.onrender.com`](https://card-brain-app.onrender.com)
- **API 文件位置 (Swagger UI)**：[`https://card-brain-app.onrender.com/docs`](https://card-brain-app.onrender.com/docs)
- **健康檢查端點**：[`https://card-brain-app.onrender.com/api/v1/health`](https://card-brain-app.onrender.com/api/v1/health)

### 後端環境變數清單 (Render Environment Variables)
| 變數名稱 (Key) | 說明 | 範例值 |
|:---|:---|:---|
| `DATABASE_URL` | Neon PostgreSQL 資料庫連線字串 | `postgresql://neondb_owner:npg_...` |
| `GEMINI_API_KEY` | Google Gemini Vision API Key (收據 OCR) | `AQ.Ab8RN6...` |

### Render 建置與啟動指令
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 📱 4. 前端 App API 連線配置 (React Native / Expo)

前端已配置為直接向 Render 雲端後端發送請求，無需再設定本地 IP。

### 前端環境變數 (`mobile/.env`)
```bash
EXPO_PUBLIC_API_URL=https://card-brain-app.onrender.com/api/v1
```

- **程式碼入口**：`mobile/src/api/client.ts`
  - 預設 fallback URL 已改為 `https://card-brain-app.onrender.com/api/v1`
  - 每次請求自動透過 Axios Interceptor 夾帶 `X-Device-UUID` 進行使用者辨識。

---

## 📲 5. 如何使用 Expo Go 進行真機測試

1. **手機安裝 Expo Go**：
   - 前往 App Store (iOS) 搜尋並下載 **Expo Go**。
2. **電腦端啟動 Expo 伺服器**：
   在 `mobile` 目錄下執行：
   ```bash
   cd mobile
   npx expo start
   ```
   *(若手機與電腦處於不同 Wi-Fi 或熱點，可使用 Tunnel 模式：`npx expo start --tunnel`)*
3. **手機開啟 App**：
   - 打開 iPhone 的相機，對準終端機產生的 QR Code 掃描，點擊在 Expo Go 中開啟。
   - 由於後端與資料庫皆已在雲端運作，App 啟動後即可直接讀取卡片、試算推薦與進行 AI 記帳！
