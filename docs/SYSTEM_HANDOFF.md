# 信用卡權益與額度大腦 (Card Brain) - SDD & 系統交接文件

本文件旨在作為 **Software Design Document (SDD)** 以及提供給其他 AI 助理（如 GitHub Copilot）的**系統交接手冊**。文件中詳細記錄了目前的系統架構、資料模型、核心功能、UI 設計規範以及剛完成的最新修改，以便後續無縫接軌開發。

---

## 1. 系統架構與技術棧 (Tech Stack)

本專案分為前後端分離架構，專為跨平台（Web, iOS, Android）與高效能 API 設計。

### 後端 (Backend)
- **框架**: Python FastAPI
- **資料庫 ORM**: SQLAlchemy (支援 SQLite / PostgreSQL)
- **非同步任務**: APScheduler (用於定時爬蟲任務與額度更新)
- **核心架構**: RESTful API, 依賴注入 (Dependency Injection)

### 前端 (Frontend)
- **框架**: React Native (Expo)
- **路由管理**: Expo Router (File-based routing)
- **圖示庫**: `@expo/vector-icons` (Ionicons)
- **狀態管理**: React Hooks (useState, useEffect) + Axios 進行 API 請求
- **跨平台支援**: 支援 React Native Web 與 Mobile 雙端響應式排版

---

## 2. 核心功能模組 (Core Features)

目前 App 底部導覽列 (Tab Bar) 包含以下五大模組：

1. **📊 額度儀表板 (Dashboard - `index.tsx`)**
   - 檢視所有名下信用卡的額度使用狀況。
   - 根據使用者的記帳紀錄，自動計算剩餘額度。
2. **🎯 決策推薦 (Recommend - `recommend.tsx`)**
   - **智慧試算**: 讓使用者輸入消費金額、支付通道 (如 LINE Pay, Apple Pay 等)、消費分類。
   - **需登錄過濾**: 後端實作了 `exclude_registration` 邏輯，可將帶有「(需登錄)」字眼的權益分開顯示，讓使用者自由選擇是否要看需要登錄的加碼回饋。
3. **📷 相機記帳 (Scan - `scan.tsx`)**
   - **雙軌記帳設計**: 支援手動記帳、以及 AI 收據辨識 (透過 Gemini Vision 支援拍照與相簿上傳截圖)。
   - **多幣別支援**: 支援 TWD, JPY, USD 等匯率換算。
4. **📇 名下卡片 (Cards - `cards.tsx`)**
   - 管理使用者持有的信用卡。
   - 點擊卡片可檢視該卡的詳細回饋通路與限時活動。
   - 後端已預先建立完整的卡片資料庫 (`seed.py`)。
5. **📖 使用教學 (Tutorial - `tutorial.tsx`)**
   - App 的靜態教學與提示頁面。

---

## 3. 資料庫與模型 (Data Models)

- **User**: 使用者帳號模型。
  - 近期新增欄位：`password_hash` (使用原生 `bcrypt` 進行加密)，解決了舊版無密碼直接登入的資安漏洞。
- **Card**: 系統內建的信用卡圖鑑。
  - 近期新增欄位：`benefit_url` (官方權益網址)、`last_synced_at` (最後爬蟲更新時間)。
- **UserCard**: 使用者名下的信用卡（關聯 User 與 Card），包含個人結帳日 `billing_cycle_date`。
- **CardBenefit**: 卡片權益規則（例如：LINE Pay 3.5% 上限 1000）。
- **Transaction**: 記帳交易紀錄，紀錄消費金額、分類、通路、對應的 UserCard 及其產生的回饋金。

---

## 4. UI / UX 設計規範 (Design System)

為了提供一致且高級的視覺體驗，本專案嚴格遵守以下設計規範（請 Copilot 延續此風格）：

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

以下是開發過程中確立的硬性規則，**請 Copilot 絕對遵守**，不可擅自覆寫：

1. **信用卡結帳日強制綁定**:
   - 永豐銀行: 18 號
   - 台新銀行: 7 號
   - 玉山銀行: 7 號
   - 聯邦銀行: 12 號
   - 星展銀行: 10 號
2. **Icon Emoji 欄位已廢棄**:
   - 舊版資料庫與前端曾使用 `icon_emoji`，**現已徹底移除**，請勿在任何程式碼中存取或建立此欄位。
3. **特定卡片權益規則 (記錄於 `seed.py`)**:
   - **玉山 Unicard (舊戶)**: 「簡單選/任意選」上限為 1000 點；「UP選」上限為 5000 點。
   - **台新 Richart 卡 (包含 @GoGo卡等)**: 規則為「7+1 刷」機制，移除舊版的「一律 3.5%」邏輯。導入通路分級（如 Chill刷、Pay著刷等），並且該卡的特定回饋額度設定為「無上限」。
4. **爬蟲與初始資料**:
   - 目前因伺服器與 Gemini API 額度不穩定，爬蟲暫時改為「半自動」或由 `backend/app/db/seed.py` 作為核心資料唯一來源（Source of Truth）。
   - 若要更新權益，請優先修改 `seed.py` 中的 `CARD_BENEFITS` 陣列。

---

## 6. 最新完成進度與修復紀錄 (Recent Changes)

- [x] **前端排版修復**: 修復 `scan.tsx` 中 `TextInput` 在網頁版導致的水平跑版 (Overflow) 問題。
- [x] **全域圖示升級**: 移除 `_layout.tsx` 底部 Tab 以及頂部 Header 中的 Emoji，全面改用 `Ionicons`，並修復了圖示與文字水平擠壓導致最左側 Tab 被切斷的排版異常。
- [x] **UI 改版**: 移除了卡片頁面的舊版教學 Modal，並於底部新增原生的「使用教學」Tab 頁面。
- [x] **後端推薦邏輯**: `recommend.tsx` API 已支援 `exclude_registration`，回傳資料會明確區分「預設結果」與「含需登錄活動結果」。
- [x] **儀表板排版與按鈕優化**: 移除儀表板中干擾排版的總卡片數，對齊文字；更新清空按鈕樣式。
- [x] **資料庫架構大改版 (額度分離)**: 將 `MonthlyUsage` 綁定 `card_benefit_id`，徹底解決了一般消費與特定加碼（如吉鶴卡日系名店）會互相佔用額度的嚴重 Bug，實現每條權益獨立計算額度。
- [x] **修復 iOS 日曆當機**: 修復了 iOS 點擊日期選擇器 (`DateTimePicker`) 因傳遞非法 `textColor` 導致觸發 `PushNotificationIOS` 報錯的嚴重系統閃退問題。
- [x] **帳號資安與密碼機制**: 為非訪客帳號新增 `password_hash` 機制，確保暱稱不被冒用。
- [x] **移除 passlib 相容性問題**: 發現 `passlib` 與 `bcrypt` 5.x 存在相容性問題會導致 500 錯誤，已全面改用原生 `bcrypt` 套件處理密碼雜湊。

---

## 7. Next Steps (給後續開發者的建議)

- **伺服器穩定性監控**: `uvicorn` 與 `npm run web` 作為背景任務容易因環境問題中斷，若發現連線失敗，需先檢查是否需重啟。
- **爬蟲機制優化**: 預留的爬蟲腳本需考量 API 速率限制與防呆機制，建議先在本地測試穩定後再整合至 APScheduler。
- **UI 優化**: 目前表單元件已具備基礎 RWD，未來可進一步調整 Tablet (iPad) 尺寸的 Grid 系統。
