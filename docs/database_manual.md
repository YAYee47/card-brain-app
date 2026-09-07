# Card Brain 資料庫手冊

本手冊介紹 `Card Brain` 專案使用的核心資料庫架構與各資料表設計（基於 SQLAlchemy 2.0 定義，支援 Neon.tech Serverless PostgreSQL 與本地 SQLite 備份）。

---

## 核心資料表關聯架構

系統由 **6 大核心業務資料表** 搭配 **2 大系統運維與快照表** 組成，涵蓋了「使用者會員系統」、「信用卡基本圖鑑」、「信用卡權益規則」、「使用者持卡狀態」、「消費記帳紀錄」、「帳單週期額度消耗」、「系統通知警報」與「爬蟲快照比對」：

### 核心業務表 (Core Business Tables)
1. **`users`**：使用者帳號主檔（支援訪客模式與會員密碼驗證）
2. **`cards`**：系統內建的所有信用卡基本資料庫（含動態方案配置）
3. **`card_benefits`**：每張信用卡對應的各項回饋與加碼規則
4. **`user_cards`**：使用者實際綁定與追蹤的信用卡（關聯 `users` 與 `cards`，記錄個人結帳日）
5. **`transactions`**：使用者的消費記帳明細（記錄當下幣別、匯率、適用的卡片方案）
6. **`monthly_usage`**：各張卡片、各項加碼權益在各帳單週期的額度消耗與累計回饋

### 系統運維與快照表 (Operational & Snapshot Tables)
7. **`app_alerts`**：使用者警報與通知紀錄（額度 80% 預警、100% 封頂、權益異動通知）
8. **`benefit_snapshots`**：權益快照歷史紀錄（供 APScheduler 爬蟲執行差異比對）

---

## 1. 使用者主檔 (`users`)
負責管理 APP 的使用者身分識別與登入狀態。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `device_uuid` | String (255) | 裝置唯一識別碼 (唯一索引，用於綁定設備或訪客記帳) |
| `nickname` | String (100) | 使用者暱稱 |
| `password_hash` | String (255) | 密碼雜湊值（採用原生 `bcrypt` 進行 Hash 保護，可為空） |
| `is_guest` | Boolean | 是否為訪客模式 (預設 `False`) |
| `created_at` | DateTime | 帳號建立時間 (預設當前時間) |

---

## 2. 信用卡基本資料 (`cards`)
由系統預設建置（`seed.py`），儲存各銀行的信用卡發行資料與動態模式設定。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `bank_name` | String (50) | 發卡銀行名稱（如：永豐銀行、玉山銀行） |
| `card_name` | String (100) | 信用卡名稱（如：幣倍卡、Unicard） |
| `mode_config` | Text | 動態方案 JSON 配置（如玉山 Unicard 的 `scope: "monthly"` 方案切換定義） |
| `benefit_url` | Text | 官方權益介紹網址 (供爬蟲與使用者查閱) |
| `last_synced_at` | DateTime | 最近爬蟲更新時間 |
| `created_at` | DateTime | 資料建立時間 |

---

## 3. 信用卡權益規則 (`card_benefits`)
定義某張信用卡在特定通路或條件下，可以獲得的基礎回饋與加碼回饋上限。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `card_id` | Integer (FK) | 關聯至 `cards.id` |
| `channel_name` | Text | 適用通路名稱（如：國內一般消費、LINE Pay、日系名店） |
| `base_rate` | Numeric (5, 2) | 基礎回饋比例（%，無上限） |
| `bonus_rate` | Numeric (5, 2) | 加碼回饋比例（%） |
| `monthly_cap_ntd` | Integer | 每月/每帳單週期最高加碼回饋上限金額 (NTD)。若為 `NULL` 則無上限 |
| `required_mode` | Text | 權益模式限制（如玉山 Unicard 的「簡單選」、「任意選」、「UP選」） |
| `effective_date` | Date | 權益生效/發布日期 |
| `created_at` | DateTime | 資料建立時間 |

---

## 4. 使用者持卡狀態 (`user_cards`)
當使用者決定追蹤某張信用卡時，會建立一筆 `user_cards`，並設定其個人化的結帳日。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `user_id` | Integer (FK) | 關聯至 `users.id` |
| `card_id` | Integer (FK) | 關聯至 `cards.id` |
| `billing_cycle_date` | Integer | 每月帳單結帳日 (1~31) |
| `is_active` | Boolean | 是否啟用此卡片的額度追蹤 |
| `created_at` | DateTime | 資料建立時間 |

---

## 5. 消費記帳明細 (`transactions`)
記錄使用者每一筆消費的金額、通路，以及經過系統精算後獲得的預估回饋金。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `user_id` | Integer (FK) | 關聯至 `users.id` |
| `user_card_id` | Integer (FK) | 關聯至 `user_cards.id` (記錄用哪張卡刷的) |
| `channel_name` | Text | 支付通道/平台 (如：Apple Pay、LINE Pay、實體刷卡) |
| `category` | String (50) | 消費分類 (如：餐飲、購物、交通、娛樂) |
| `merchant_name` | Text | 商家名稱 (由 AI 辨識或使用者手動輸入) |
| `original_amount`| Numeric (12, 2) | 原始消費金額 |
| `currency` | String (5) | 幣別 (如：TWD, JPY, KRW, CNY, USD) |
| `ntd_amount` | Numeric (12, 2) | 換算後的台幣金額 |
| `exchange_rate` | Numeric (10, 4) | 匯率 (台幣消費固定為 1.0) |
| `earned_cashback_ntd`| Numeric (10, 2) | 此筆交易**實際獲得**的台幣回饋金 (基礎 + 加碼) |
| `source_type` | String (50) | 記帳來源 (如：MANUAL, RECEIPT_AI, QRCODE) |
| `card_mode` | String (50) | 交易當下該卡片的切換模式（如：簡單選、任意選、UP選） |
| `transacted_at` | DateTime | 實際刷卡時間 (用於判定所屬帳單週期與日曆月) |
| `created_at` | DateTime | 資料建立時間 |

---

## 6. 帳單週期額度消耗 (`monthly_usage`)
**核心額度管理機制**。為了精確計算各通路加碼上限是否封頂，系統會針對**每一個帳單週期**與**每一個權益通道 (`card_benefit_id`)** 建立一筆使用紀錄。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `user_id` | Integer (FK) | 關聯至 `users.id` |
| `user_card_id` | Integer (FK) | 關聯至 `user_cards.id` |
| `card_benefit_id`| Integer (FK) | **關聯至 `card_benefits.id`** (精確追蹤是哪個權益通道的消耗) |
| `cycle_start_date`| Date | 本帳單週期的起始日 |
| `cycle_end_date` | Date | 本帳單週期的結束日 |
| `used_amount_ntd`| Numeric (12, 2) | 該週期、該權益通道**已消耗的刷卡金額** (NTD) |
| `earned_cashback_ntd`| Numeric (10, 2) | 該週期、該權益通道已賺取的回饋金 (NTD) |
| `updated_at` | DateTime | 最後累計更新時間 |

### 💡 額度分離架構與防重機制說明
- **額度分離**：加入了 `card_benefit_id` 外鍵。若一張卡片有「國內一般消費」與「日系名店加碼」兩種權益，刷日系名店只會累計「日系名店」那筆 `monthly_usage` 的進度條，兩者**完全獨立計算**，確保加碼額度不會互相排擠。
- **防重與 UPSERT**：目前在 `transaction_service.py` 應用層中透過 `(user_card_id, card_benefit_id, cycle_start_date, cycle_end_date)` 查詢判定，存在則累加，不存在則動態開立新週期紀錄。
- **共用額度處理**：像星展傳說對決卡將「蝦皮/App Store/UberEats」等多個通路設定為**共用 300 元回饋上限**，在 `seed.py` 中這幾個通路合併寫在同一筆 `card_benefits` 裡，因此自然對應到同一筆 `monthly_usage` 進行合併累計。

---

## 7. 使用者通知警報表 (`app_alerts`)
記錄權益異動爬蟲比對結果與個人化額度水位警告通知。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `user_id` | Integer (FK) | 關聯至 `users.id` |
| `alert_type` | String (50) | 警報類型：`BENEFIT_CHANGE` / `QUOTA_WARNING` / `QUOTA_CAPPED` / `CRAWL_DONE` |
| `severity` | String (20) | 嚴重等級：`INFO` / `WARNING` / `CRITICAL` |
| `card_id` | Integer (FK) | 關聯至 `cards.id` (可為空，代表系統級通知) |
| `user_card_id` | Integer (FK) | 關聯至 `user_cards.id` |
| `title` | String (200) | 警報標題 |
| `body` | Text | 警報詳細內容 |
| `diff_detail` | Text | 差異比對 JSON 詳細資訊 (可為空) |
| `is_read` | Boolean | 是否已讀 (預設 `False`) |
| `created_at` | DateTime | 警報產生時間 |

---

## 8. 權益快照歷史表 (`benefit_snapshots`)
每次定時爬蟲執行完畢後儲存一份權益快照，供後續執行 Diff 差異比對。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `card_id` | Integer (FK) | 關聯至 `cards.id` |
| `channel_name` | String (100) | 適用通路名稱 |
| `base_rate` | Float | 基礎回饋率 (%) |
| `bonus_rate` | Float | 加碼回饋率 (%) |
| `monthly_cap_ntd` | Float | 每月加碼封頂金額 (可為空) |
| `source` | String (20) | 快照來源：`SEED` / `CRAWLER` / `MANUAL` |
| `snapshotted_at` | DateTime | 快照時間 |
