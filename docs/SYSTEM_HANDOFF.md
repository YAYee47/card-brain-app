# 信用卡權益與額度大腦 (Card Brain) - SDD & 系統交接文件

本文件旨在作為 **Software Design Document (SDD)** 以及提供給其他 AI 助理（如 GitHub Copilot）的**系統交接手冊**。文件中詳細記錄了目前的系統架構、資料模型、核心功能、UI 設計規範以及剛完成的最新修改，以便後續無縫接軌開發。

---

## 1. 系統架構與技術棧 (Tech Stack)

本專案分為前後端分離架構，專為跨平台（Web, iOS, Android）與高效能 API 設計。

### 後端 (Backend)
- **框架**: Python FastAPI (Uvicorn)
- **資料庫 ORM**: SQLAlchemy 2.0 Async (線上環境為 Neon.tech Serverless PostgreSQL，本地保留 SQLite 備份)
- **非同步任務**: APScheduler (用於每季定期爬蟲任務與每日額度掃描更新)
- **AI 視覺辨識**: Google Gemini 3.5 Flash (使用官方 `google-genai` SDK)
- **匯率計算**: ExchangeRate-API (開放免金鑰端點 `open.er-api.com`)
- **核心架構**: RESTful API, 依賴注入 (Dependency Injection)

### 前端 (Frontend)
- **框架**: React Native (Expo SDK 57)
- **路由管理**: Expo Router (File-based routing)
- **圖示庫**: `@expo/vector-icons` (Ionicons)
- **狀態管理**: React Hooks (useState, useEffect) + Axios 進行 API 請求 (Request Interceptor 夾帶 `X-Device-UUID`)
- **跨平台支援**: 支援 React Native Web 與 Mobile 雙端響應式排版，支援 Expo EAS OTA 雲端熱更新

---

## 2. 核心功能模組 (Core Features)

目前 App 底部導覽列 (Tab Bar) 包含以下五大模組：

1. **📊 額度儀表板 (Dashboard - `index.tsx`)**
   - 檢視所有名下信用卡的額度使用狀況與進度條。
   - 根據使用者的記帳紀錄，自動計算剩餘額度與累積已賺回饋金。
2. **🎯 決策推薦 (Recommend - `recommend.tsx`)**
   - **智慧試算**: 讓使用者輸入消費金額、支付通道或特店名稱 (如 LINE Pay, 星巴克等)。
   - **需登錄過濾**: 後端實作了 `exclude_registration` 邏輯，可將帶有「(需登錄)」字眼的權益分開顯示，讓使用者自由選擇是否要看需要登錄的加碼回饋。
3. **📷 相機記帳 (Scan - `scan.tsx`)**
   - **雙軌記帳設計**: 支援手動記帳、以及 AI 收據辨識 (透過 Gemini 3.5 Flash 支援拍照與相簿上傳截圖)。
   - **多幣別支援**: 支援 TWD, JPY, KRW (韓元), CNY (人民幣), USD 等即時匯率換算，專門滿足出國（如韓國 Olive Young）與海淘記帳需求。
   - **日期選擇器**: 跨平台封裝為 `DatePickerModal.tsx`，鎖定 `themeVariant="light"` 徹底防禦 iOS 閃退。
4. **📇 名下卡片 (Cards - `cards.tsx`)**
   - 管理使用者持有的信用卡。
   - 點擊卡片可檢視該卡的詳細回饋通路與限時活動。
   - 後端已預先建立完整的卡片資料庫 (`seed.py`)。
5. **📖 使用教學 (Tutorial - `tutorial.tsx`)**
   - App 的原生教學與提示頁面。

---

## 3. 資料庫與模型 (Data Models)

資料庫包含 6 大核心業務表與 2 大系統運維快照表：

- **User**: 使用者帳號模型，包含 `device_uuid`、`is_guest` 與 `password_hash` (使用原生 `bcrypt` 進行加密)，解決舊版無密碼直接登入的資安漏洞。
- **Card**: 系統內建的信用卡圖鑑，包含 `mode_config` (方案配置)、`benefit_url` (官方權益網址)、`last_synced_at` (最後爬蟲更新時間)。
- **UserCard**: 使用者名下的信用卡（關聯 User 與 Card），包含個人結帳日 `billing_cycle_date`。
- **CardBenefit**: 卡片權益規則（例如：LINE Pay 3.5% 上限 1000），包含 `effective_date` 生效日與 `required_mode` 模式限制。
- **Transaction**: 記帳交易紀錄，紀錄消費金額、幣別、匯率、分類、通路、對應的 UserCard、方案 `card_mode` 及其產生的回饋金。
- **MonthlyUsage**: 帳單週期加碼額度累積表，**綁定 `card_benefit_id`**，實現每條加碼獨立追蹤。
- **AppAlert**: 使用者通知警報表（80% 預警、100% 封頂、權益異動通知）。
- **BenefitSnapshot**: 權益快照表，供 APScheduler 爬蟲比對歷史差異。

---

## 4. UI / UX 設計規範 (Design System)

為了提供一致且高級的視覺體驗，本專案嚴格遵守以下設計規範：

1. **主題色系 (Pink Theme)**:
   - 背景色: `#FFF0F5` (LavenderBlush)
   - 邊框與分隔線: `#FCE7F3` (Pink 100)
   - 次要提示文字: `#F9A8D4` / `#BE185D`
   - **主視覺強調色 (Primary)**: `#DB2777` (Pink 600) / `#831843` (深紫紅)
   - 亮點色 (如成功、高亮): `#059669` (Emerald)
2. **圖示系統 (Iconography)**:
   - **嚴禁使用純文字 Emoji 作為版面佈局的 Icon** (會導致 Web 版排版崩潰與對齊問題)。
   - 必須使用 `@expo/vector-icons` (主要使用 `Ionicons`)。
   - 底部 Tab Bar 設定為 `flexDirection: 'column'` (圖標在上，文字在下)。
   - 頂部 Header Title 實作了 `CustomHeaderTitle` 元件，圖文水平置中。
3. **響應式與彈性佈局 (Flexbox)**:
   - 表單與輸入框在橫向 `flexDirection: 'row'` 佈局中，必須加上 `minWidth: 0` 來防止 WebKit/Blink 引擎的 TextInput 溢出 (Overflow) 問題。

---

## 5. 商業邏輯與硬性規則 (Business Rules)

以下是開發過程中確立的硬性規則，**請後續開發者絕對遵守**，不可擅自覆寫：

1. **信用卡結帳日強制綁定**:
   - 永豐銀行: 18 號
   - 台新銀行: 7 號
   - 玉山銀行: 7 號
   - 聯邦銀行: 12 號
   - 星展銀行: 10 號
2. **玉山 Unicard 方案整月追溯重算機制**:
   - 玉山 Unicard 具備 `scope: "monthly"` 特性。當使用者切換方案時，後端會自動回溯當月所有歷史交易，收集跨越的帳單週期 (`affected_cycles`)，清空舊有 `MonthlyUsage` 並依照時序重新精算回饋金與累計水位。
3. **特定卡片權益規則 (記錄於 `seed.py`)**:
   - **玉山 Unicard (舊戶)**: 「簡單選/任意選」上限為 1000 點；「UP選」上限為 5000 點。
   - **台新 Richart 卡 (包含 @GoGo卡等)**: 規則為「7+1 刷」機制，移除舊版的「一律 3.5%」邏輯。導入通路分級（如 Chill刷、Pay著刷等），並且該卡的特定回饋額度設定為「無上限」。
4. **爬蟲與初始資料**:
   - 目前因伺服器與外部網站限制，爬蟲設定為每季排程或手動觸發，`backend/app/db/seed.py` 作為核心初始資料來源。
   - 若要更新權益，請優先修改 `seed.py` 中的資料陣列。

---

## 6. 最新完成進度與修復紀錄 (Recent Changes)

- [x] **前端排版修復**: 修復 `scan.tsx` 中 `TextInput` 在網頁版導致的水平跑版 (Overflow) 問題。
- [x] **全域圖示升級**: 移除 `_layout.tsx` 底部 Tab 以及頂部 Header 中的 Emoji，全面改用 `Ionicons`。
- [x] **UI 改版**: 新增原生的「使用教學」Tab 頁面。
- [x] **後端推薦邏輯**: `recommend.py` API 支援 `exclude_registration`，回傳資料明確區分預設與含需登錄活動結果。
- [x] **資料庫架構大改版 (額度分離)**: 將 `MonthlyUsage` 綁定 `card_benefit_id`，徹底解決一般消費與特定加碼會互相佔用額度的 Bug。
- [x] **修復 iOS 日曆當機**: 抽離 `DatePickerModal.tsx` 並鎖定 `themeVariant="light"`，解決 iOS 日曆閃退問題。
- [x] **帳號資安與密碼機制**: 為非訪客帳號新增 `password_hash` 機制，採用原生 `bcrypt` 取代有衝突的 `passlib`。
- [x] **升級 Expo SDK 57 與 Bare Workflow 修復**: 設定固定版號 `runtimeVersion: "1.0.0"`，解決 EAS Update 500 錯誤；補齊 `@expo/vector-icons` 與 `@expo/config-plugins` 依賴。
- [x] **擴充韓元與人民幣支援**: 支援 Olive Young 韓元與淘寶記帳。

---

## 7. Next Steps (給後續開發者的建議)

- **EAS 雲端發布注意**: 每次修改完前端畫面，記得在 `mobile` 目錄執行 `npx eas-cli update --branch master --environment production --non-interactive`，手機 Expo Go 才能在不開電腦的情況下直接同步最新版。
- **伺服器冷啟動應對**: Render 免費版有 45 秒休眠重啟延遲，前端已配備 45 秒 Timeout 與快取，若需常態即時反應可考慮升級為付費實例。
