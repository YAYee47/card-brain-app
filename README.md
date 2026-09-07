# 💳 Card Brain - 信用卡權益追蹤與智能額度管理 App

這是一款為了解決「信用卡權益頻繁變動、加碼額度難以追蹤、記帳繁瑣」而設計的跨平台 (iOS/Android/Web) 智能應用程式。

---

## 🌟 專案核心功能

1. **多軌制極速記帳 (含 AI 視覺辨識)**
   - **AI 收據/載具截圖辨識**：拍照紙本發票收據，或從相簿匯入 LINE Pay/載具截圖，由 Google Gemini 3.5 Flash AI 自動辨識金額、幣別、商家與日期。
   - **多國外幣自動換算**：支援日幣 (JPY)、韓元 (KRW)、人民幣 (CNY)、美金 (USD) 等外幣消費（出國旅遊如韓國 Olive Young、淘寶掃貨皆適用），記帳時透過 ExchangeRate-API 自動抓取即時匯率換算為台幣，準確扣除加碼額度。
   - **手動補登與原生小日曆**：封裝獨立日曆組件，挑選消費日期流暢穩定。
2. **消費決策推薦引擎**
   - 結帳前輸入商家、通路或金額（如星巴克、LINE Pay），App 瞬間運算出「當下回饋最高」且「加碼未封頂」的最佳信用卡。
   - 支援動態排除「需登錄」權益，結帳最安心。
3. **獨家商業黑科技：玉山 Unicard 方案整月日曆月追溯重算**
   - 支援玉山 Unicard 的「簡單選/任意選/UP選」方案。
   - 當月期中或月底切換方案時，後端自動回溯當月所有歷史交易，收集跨越的帳單週期集合，依時序重播重算回饋金與額度累積！
4. **視覺化動態儀表板與離線快取**
   - 首頁提供所有卡片的當期消費與回饋總覽，以動態彩色進度條 (<80% 綠色、>=80% 橘色警戒、100% 紅色封頂) 顯示各加碼通道的使用率。
   - 支援 Render 雲端冷啟動 (Cold Start) 45 秒容錯與無網路時的 AsyncStorage 離線快取瀏覽。
5. **自動化爬蟲與額度警報**
   - 每季初 (1, 4, 7, 10 月) 1 號 00:05 自動爬取銀行權益更新，比對並產生變更通知。
   - 每日 09:00 自動掃描，當卡片額度使用率達 80% 或 100% (封頂) 時產生警報提醒換卡。

---

## 🛠️ 技術架構

- **後端 (Backend)**: FastAPI (Python 3.10+), SQLAlchemy 2.0 (Async), APScheduler (定時排程), Google Gemini 3.5 Flash (google-genai SDK 視覺 OCR), 原生 bcrypt 安全雜湊。
- **資料庫 (Database)**: 線上正式環境採用 Neon.tech Serverless PostgreSQL (`asyncpg`)，本地提供完整冷備份與無損遷移腳本 (`migrate_sqlite_to_pg.py`)。
- **前端 (Mobile)**: React Native (Expo SDK 57, Expo Router), TypeScript, Ionicons, AsyncStorage (離線快取), Expo EAS OTA 雲端熱更新。
- **雲端部署**: Render.com (Web Service), Neon.tech (PostgreSQL), Expo EAS (Mobile Update)。

---

## 🚀 如何啟動專案？

專案分為「後端」與「前端」兩個部分：

> 💡 **小撇步**：目前後端與資料庫皆已 24 小時託管於雲端（[`https://card-brain-app.onrender.com`](https://card-brain-app.onrender.com) 與 Neon.tech），**一般日常記帳測試時，電腦完全不需要啟動本機後端**！

### 步驟 1：啟動本機後端伺服器 (若需本機開發修改 API 才需要)

1. 打開終端機，進入後端資料夾：
   ```powershell
   cd backend
   ```
2. 啟動 Python 虛擬環境並執行伺服器：
   ```powershell
   .\venv\Scripts\activate
   $env:PYTHONPATH="."
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *啟動成功後，可開啟瀏覽器前往 `http://localhost:8000/docs` 查看 Swagger 互動文件。*

### 步驟 2：啟動前端 App (手機畫面)

1. 打開終端機，進入前端資料夾：
   ```powershell
   cd mobile
   ```
2. 啟動 Expo 開發伺服器（加 `-c` 清除快取）：
   ```powershell
   npx expo start -c
   ```
3. 選擇要在哪裡開啟 App：
   - **實體 iPhone / Android**：打開手機內建相機，對準終端機顯示的 QR Code 掃描，即可載入最新版 App。
   - **電腦瀏覽器**：在終端機按下 `w` 鍵。
   - **雲端隨身測試 (免開電腦)**：可直接於手機 Expo Go 打開透過 `eas update` 推送的最新版本！

---

## 🧪 測試與操作指南

當 App 成功啟動後，你可以透過以下 5 大 Tab 流程測試功能：

1. **初始設定 (名下卡片 - `cards.tsx`)**
   - 勾選錢包裡實際擁有的信用卡（如永豐幣倍卡、大戶卡、玉山 Unicard 等），並可自訂每張卡的個人結帳日 (1~31 號)。
2. **測試「消費決策推薦」(決策推薦 - `recommend.tsx`)**
   - 輸入商家名稱（如「星巴克」或「LINE Pay」）與預計金額，系統自動算出哪張卡回饋最高、加碼額度最充裕。
3. **測試「AI 相機與多幣別記帳」(記帳分析 - `scan.tsx`)**
   - 上傳收據或載具截圖，Gemini 3.5 Flash 瞬間辨識店家與金額。
   - 亦可手動輸入外幣消費（如 10,000 KRW 或 5,000 JPY），自動抓取即時匯率折算台幣入帳。
4. **查看「動態彩色儀表板」(額度儀表板 - `index.tsx`)**
   - 首頁動態顯示加碼額度水位：<80% 綠色安全、>=80% 橘色警報、100% 紅色封頂。
5. **瀏覽「使用教學」(使用教學 - `tutorial.tsx`)**
   - 檢視 App 秘笈與各項回饋防雷技巧。

---

## 📚 專案完整技術文檔導覽 (`docs/`)

若需深入研究架構、資料庫與踩坑歷程，請參閱 `docs/` 資料夾下的專題文件：

- 🧠 [**打造全紀錄（學習歷程・架構・全踩坑血淚寶典）**](docs/%F0%9F%A7%A0%20%E6%88%91%E7%9A%84%E4%BF%A1%E7%94%A8%E5%8D%A1%E5%A4%96%E6%8E%9B%E5%A4%A7%E8%85%A6%EF%BC%9ACard%20Brain%20%E6%89%93%E9%80%A0%E5%85%A8%E7%B4%80%E9%8C%84%EF%BC%88%E5%AD%B8%E7%BF%92%E6%AD%B7%E7%A8%8B%E3%83%BB%E6%9E%B6%E6%A7%8B%E3%83%BB%E5%85%A8%E8%B8%A9%E5%9D%91%E8%A1%80%E6%B7%9A%E5%AF%B6%E5%85%B8%EF%BC%89.md)
- 🗄️ [**資料庫手冊 (database_manual.md)**](docs/database_manual.md)
- ☁️ [**雲端架構與部署手冊 (CLOUD_DEPLOYMENT.md)**](docs/CLOUD_DEPLOYMENT.md)
- 📱 [**Expo SDK 升級與 EAS 雲端更新避坑手冊**](docs/EXPO_SDK_%E5%8D%87%E7%B4%9A%E8%88%87EAS%E6%9B%B4%E6%96%B0%E9%81%BF%E5%9D%91%E6%89%8B%E5%86%8A.md)
- 🤝 [**系統交接文件 (SYSTEM_HANDOFF.md)**](docs/SYSTEM_HANDOFF.md)
- 🗺️ [**程式碼架構導覽 (程式碼架構導覽.md)**](docs/%E7%A8%8B%E5%BC%8F%E7%A2%BC%E6%9E%B6%E6%A7%8B%E5%B0%8E%E8%A6%BD.md)
- 📖 [**環境建置手冊 (環境建置手冊.md)**](docs/%E7%92%B0%E5%A2%83%E5%BB%BA%E7%BD%AE%E6%89%8B%E5%86%8A.md)
