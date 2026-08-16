# Card Brain 資料庫手冊

本手冊介紹 `Card Brain` 專案使用的核心資料庫架構與各資料表設計（基於 SQLAlchemy 2.0 定義）。

---

## 核心資料表關聯架構

系統主要由 6 個資料表組成，涵蓋了「使用者」、「信用卡基本資料」、「信用卡權益規則」、「使用者持卡狀態」、「消費記帳紀錄」與「帳單週期額度消耗」等功能：

1. **`users`**：使用者主檔
2. **`cards`**：系統內建的所有信用卡基本資料庫
3. **`card_benefits`**：每張信用卡對應的各項回饋與加碼規則
4. **`user_cards`**：使用者實際綁定與追蹤的信用卡（關聯 `users` 與 `cards`）
5. **`transactions`**：使用者的消費記帳明細
6. **`monthly_usage`**：各張卡片、各項加碼權益在各帳單週期的額度消耗與累計回饋

---

## 1. 使用者主檔 (`users`)
負責管理 APP 的使用者與登入狀態。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `device_uuid` | String | 裝置唯一識別碼 (用於綁定裝置) |
| `nickname` | String | 使用者暱稱 |
| `is_guest` | Boolean | 是否為訪客模式 (預設 `False`) |
| `created_at` | DateTime | 帳號建立時間 |

---

## 2. 信用卡基本資料 (`cards`)
由系統預設建置（`seed.py`），儲存各銀行的信用卡發行資料。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `bank_name` | String | 發卡銀行名稱（如：台新銀行、富邦銀行） |
| `card_name` | String | 信用卡名稱（如：@GoGo卡、J卡） |
| `card_image_url` | String | 信用卡卡面圖片連結 |
| `card_type` | String | 信用卡組織/等級（如：VISA 御璽卡） |
| `currency` | String | 預設幣別（如：TWD） |
| `created_at` | DateTime | 資料建立時間 |

---

## 3. 信用卡權益規則 (`card_benefits`)
定義某張信用卡在特定通路或條件下，可以獲得的基礎回饋與加碼回饋上限。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `card_id` | Integer (FK) | 關聯至 `cards.id` |
| `channel_name` | String | 適用通路名稱（如：國內一般消費、LINE Pay、日系名店） |
| `base_rate` | Numeric | 基礎回饋比例（%，無上限） |
| `bonus_rate` | Numeric | 加碼回饋比例（%） |
| `monthly_cap_ntd` | Integer | 每月/每帳單週期最高加碼回饋上限金額 (NTD)。若為 `NULL` 則無上限 |
| `required_mode` | String | 權益模式限制（如玉山 Unicard 的「簡單百搭」、「任意切換」等模式） |
| `effective_date` | Date | 權益生效/發布日期 |

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

---

## 5. 消費記帳明細 (`transactions`)
記錄使用者每一筆消費的金額、通路，以及經過系統精算後獲得的預估回饋金。

| 欄位名稱 | 類型 | 說明 |
| --- | --- | --- |
| `id` | Integer (PK) | 唯一識別碼 |
| `user_id` | Integer (FK) | 關聯至 `users.id` |
| `user_card_id` | Integer (FK) | 關聯至 `user_cards.id` (記錄用哪張卡刷的) |
| `channel_name` | String | 支付通道/平台 (如：Apple Pay、實體刷卡) |
| `category` | String | 消費分類 (如：餐飲、購物、交通) |
| `merchant_name` | String | 商家名稱 (如：星巴克) |
| `original_amount`| Numeric | 原始消費金額 |
| `currency` | String | 幣別 (如：TWD, JPY, USD) |
| `ntd_amount` | Numeric | 換算後的台幣金額 |
| `exchange_rate` | Numeric | 匯率 (台幣消費固定為 1.0) |
| `earned_cashback_ntd`| Numeric | 此筆交易**實際獲得**的台幣回饋金 (基礎 + 加碼) |
| `source_type` | String | 記帳來源 (如：MANUAL, RECEIPT_AI, QRCODE) |
| `card_mode` | String | 交易當下該卡片的切換模式 (若有) |
| `transacted_at` | DateTime | 實際刷卡時間 |

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
| `used_amount_ntd`| Numeric | 該週期、該權益通道**已消耗的刷卡金額** (NTD) |
| `earned_cashback_ntd`| Numeric | 該週期、該權益通道已賺取的回饋金 (NTD) |

### 💡 額度分離架構說明
- 過去的設計是整張卡片共用一筆 `monthly_usage`，導致一般消費會錯誤佔用加碼通路的額度。
- **目前的最新設計**：加入了 `card_benefit_id`。如果一張卡片有「國內一般消費」與「日系名店加碼」兩種權益，當你刷了一筆日系名店，系統只會去更新「日系名店」那筆 `monthly_usage` 的消耗進度，兩者**完全獨立計算**，確保加碼額度不會互相排擠。
- **共用額度處理**：如果是像星展傳說對決卡將「蝦皮/App Store/UberEats」等多個通路設定為**共用 300 元回饋上限**，在 `seed.py` 中這幾個通路會被合併寫在同一筆 `card_benefits` 裡，因此自然對應到同一筆 `monthly_usage` 進行累計。
