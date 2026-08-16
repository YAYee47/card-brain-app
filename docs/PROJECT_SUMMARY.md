# 💳 信用卡權益追蹤與智能額度管理 App (Card Brain)
## 專案開發成果總結報告

---

## 🎯 1. 專案簡介與目標

本專案旨在解決台灣信用卡使用者常見的三大痛點：
1. **權益頻繁變動難追蹤**：各家銀行權益每季/半年更動，加碼條件複雜。
2. **加碼回饋上限易爆額**：各通路加碼設有月上限（如 2000元/3000元），超額即降回基礎回饋。
3. **記帳繁瑣與外幣換算**：紙本收據、LINE Pay 截圖、海外消費匯率換算費時費力。

本系統透過 **FastAPI 後端 + React Native (Expo) 前端 + Gemini Vision AI + APScheduler 自動排程**，打造雙平台智能信用卡大腦。

---

## 🛠️ 2. 技術棧與系統架構

```mermaid
graph TD
    A["React Native / Expo 前端 App (iOS/Android/Web)"] -->|HTTPS / REST API| B["Render.com 雲端後端伺服器 (FastAPI)"]
    B -->|非同步 AsyncPG ORM| C[("Neon.tech 雲端 PostgreSQL 資料庫")]
    B -->|Vision OCR| D["Google Gemini 2.5 Flash API"]
    B -->|即時匯率抓取| E["Exchange Rate API"]
    B -->|排程觸發 (月/日)| F["APScheduler 定時器"]
    F -->|比對異動與掃描額度| C
```

| 層級 | 技術選型 | 說明 |
|:---|:---|:---|
| **前端 (Mobile)** | React Native, Expo, TypeScript, AsyncStorage | 跨平台 iOS/Android/Web，支援離線快取 |
| **後端 (Backend)** | Python 3, FastAPI, SQLAlchemy 2.0 (Async) | 部署於 Render.com 雲端平台 |
| **資料庫 (Database)**| PostgreSQL (`Neon.tech`) | 永久免費 Serverless 關聯資料庫 |
| **AI 視覺辨識** | Google `gemini-2.5-flash` (google-genai) | 收據照片、LINE Pay / 載具截圖 OCR 提取 |
| **自動化排程** | APScheduler (AsyncIO) | 月初自動爬蟲、每日額度掃描警報 |
| **匯率服務** | Open Exchange Rates API + 備援機制 | 支援 JPY, USD, EUR 等外幣即時折算台幣 |

---

## 🚀 3. 已完成的 6 大核心任務細節

### 任務 1：基礎骨架與健康檢查
- 建立前後端目錄結構（後端在 `D:\WORK\card-brain-app\backend`，前端在 `D:\WORK\card-brain-app\mobile`）。
- 完成 CORS 跨域設定與 `/api/v1/health` 健康檢查端點。

### 任務 2：資料庫 Schema 與 Onboarding 選卡流程
- 設計並建立 6 張核心 ORM 資料表：
  `Card`, `CardBenefit`, `UserCard`, `Transaction`, `MonthlyUsage`, `AppAlert`, `BenefitSnapshot`。
- **額度分離架構**：`MonthlyUsage` 現已加入 `card_benefit_id`，確保同一張卡的不同加碼通路（如國內一般消費 vs 日系名店）額度能完全獨立精算與消耗。
- 初始化 Seed 資料：寫入永豐大戶卡、台新 Richart 卡、玉山 Unicard、星展傳說對決卡、聯邦吉鶴卡等 5 家指定銀行卡片與加碼規則。
- 完成 Onboarding API，讓使用者選擇持有卡片並設定帳單結帳日 (1~31 號)。

### 任務 3：消費決策推薦引擎 (Recommendation Engine)
- 實作 `/api/v1/recommend` 端點：輸入「消費金額 + 支付通道 (如 Apple Pay)」。
- 自動結合 `billing_cycle.py` 判斷當前帳單週期，計算各卡片剩餘加碼額度。
- 推薦「當下預估回饋金最高」且「額度未滿」的最佳卡片，並回饋完整比較清單。

### 任務 4：雙軌制相機記帳 (AI 辨識 + 手動)與權益引擎
- **軌道 1 (AI 收據辨識)**：後端呼叫 Gemini 2.5 Flash 精準解析實體收據或相簿內截圖的金額、幣別、日期與商家。
- **軌道 2 (手動記帳)**：提供方便的手動記帳介面與日期選單。
- **自動匯率與回饋精算**：外幣消費自動換算台幣，精算基礎+加碼回饋金，並寫入 `Transaction` 與更新 `MonthlyUsage` 當期對應權益的累計。
- **共用額度上限機制 (Shared Cap)**：支援將多個通路綁定至同一個加碼規則下，例如永豐 JCB 特選網購與星展傳說對決，確保多通路能正確共用同一個月回饋上限額度，儀表板顯示合併後進度條。
- **玉山 Unicard 月度權益追溯引擎**：支援選擇「簡單選/任意選/UP選」，當月期中切換方案時，系統會自動往前回溯同日曆月所有交易，並自動重建跨帳單週期的 `MonthlyUsage`，確保留存歷史與額度 100% 精準。

### 任務 5：視覺化動態儀表板與離線快取同步
- **後端彙整 API** (`/api/v1/dashboard`)：回饋全卡本期總消費、總預估回饋、各通道使用率百分比。
- **動態進度條**：使用率 <80% 顯示綠色；>=80% 顯示橘色警示；100% 顯示紅色封頂。
- **離線快取模組** (`src/services/cache.ts`)：支援 AsyncStorage 快取，無網路時顯示離線 Banner 並展示最後一次同步資料。

### 任務 6：權益異動爬蟲排程與自動化警報
- **爬蟲差異比對引擎** (`services/crawler.py` & `diff_engine.py`)：抓取最新權益並與現有資料比對，產生 `BENEFIT_CHANGE` 異動通知。
- **額度警告掃描**：對額度達 80% 產生 `QUOTA_WARNING`，對 100% 產生 `QUOTA_CAPPED` 警報。
- **APScheduler 自動化排程**：每月 1 號 00:05 自動跑爬蟲，每日 09:00 自動掃描額度。
- **前端通知中心** (`alerts.tsx`)：獨立的通知頁面，支援單筆/全部標記已讀，並提供手動測試觸發按鈕。

---

## 📊 4. API 端點清單

| 分類 | HTTP 方法 | API 路徑 | 功能說明 |
|:---|:---|:---|:---|
| **系統** | `GET` | `/api/v1/health` | 系統健康檢查 |
| **卡片權益** | `GET` | `/api/v1/cards` | 查詢所有支援的信用卡與權益 |
| **使用者選卡**| `GET` / `POST` | `/api/v1/user-cards` | 查詢/新增使用者持有的卡片與結帳日 |
| **推薦引擎** | `POST` | `/api/v1/recommend` | 消費決策推薦最佳卡片 |
| **AI 辨識** | `POST` | `/api/v1/ocr/receipt` | 上傳收據/截圖照片由 Gemini 解析 |
| **交易記帳** | `POST` / `GET` | `/api/v1/transactions` | 新增消費記帳（精算回饋）/ 查詢明細 |
| **交易重置** | `DELETE` | `/api/v1/transactions/reset` | 一鍵清空測試記帳與累計額度 |
| **儀表板** | `GET` | `/api/v1/dashboard` | 取得儀表板彙整資料 (含通道進度條) |
| **警報通知** | `GET` / `POST` | `/api/v1/alerts` | 查詢警報清單 / 標記已讀 |
| **爬蟲觸發** | `POST` | `/api/v1/crawl` | 手動觸發權益爬蟲與額度掃描 |

---

## ✅ 5. 測試驗證紀錄總結

1. **後端 E2E 測試**：執行 `test_task4.py`、`test_dashboard.py` 與 `test_task6.py` 全部通過。
   - NT$1,500 Apple Pay 消費：精算回饋 **NT$37.5** (0.5%基礎 + 2%加碼)。
   - 5,000 JPY 消費：成功依即時匯率 0.203 換算為 **NT$1,014.94**。
   - 大戶卡消費 NT$8,000 達上限：正確觸發 **100% 封頂警報** (`is_capped=True`)。
   - 消費 NT$2,514.94 達 83.8%：正確觸發 **80% 額度警示** (`is_warning=True`)。
2. **前端 UI 呈現**：
   - Web 介面完美呈現暗色模式 (Dark Mode) 儀表板、動態進度條與警告徽章。
   - `_layout.tsx` 已加入 `maxWidth: 480` 置中響應式限制，搭配 Chrome DevTools (`F12` -> `Ctrl+Shift+M`) 可完全模擬智慧型手機操作體驗。

---

## 📌 6. 檔案目錄結構導覽

```
D:\WORK\card-brain-app\
├── backend/                  # FastAPI 後端專案
│   ├── app/
│   │   ├── api/v1/           # API 端點 (cards, recommend, transactions, dashboard, alerts)
│   │   ├── db/               # 資料庫初始化與 Seed 資料
│   │   ├── models/           # SQLAlchemy 6 大 ORM 模型
│   │   ├── schemas/          # Pydantic 驗證 Schema
│   │   └── services/         # 推薦引擎, OCR, 匯率, 比對引擎, APScheduler
│   ├── card_brain.db         # SQLite 資料庫主檔
│   └── reset_data.py         # 一鍵清空測試資料腳本
└── mobile/                   # React Native (Expo) 前端專案
    ├── app/
    │   ├── (tabs)/           # 5 大 Tab 頁面 (index, recommend, scan, cards, alerts)
    │   └── _layout.tsx       # Web 手機容器置中佈局
    └── src/
        ├── api/              # axios API 連線模組
        └── services/         # AsyncStorage 離線快取模組
```
