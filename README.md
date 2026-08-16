# 💳 Card Brain - 信用卡權益追蹤與智能額度管理 App

這是一款為了解決「信用卡權益頻繁變動、加碼額度難以追蹤、記帳繁瑣」而設計的雙平台 (iOS/Android) 應用程式。

## 🌟 專案核心功能

1. **多軌制極速記帳 (含 AI 視覺辨識)**
   - **QR Code 秒解**：掃描台灣電子發票左側 QR Code，1 秒內自動帶入金額與日期。
   - **AI 收據/截圖辨識**：拍照紙本收據，或從相簿匯入 LINE Pay/載具截圖，由 Gemini AI 自動辨識金額、幣別。
   - **外幣自動換算**：支援日幣 (JPY)、美金 (USD) 等外幣消費，記帳時自動抓取即時匯率換算為台幣，準確扣除加碼額度。
2. **消費決策推薦引擎**
   - 結帳前輸入金額與支付方式（如 Apple Pay），App 瞬間運算出「當下回饋最高」且「額度未滿」的最佳信用卡。
   - 自動處理各家銀行不同的「結帳日」週期（例如 1 號、15 號結帳），確保額度計算精準。
3. **視覺化動態儀表板與離線快取**
   - 首頁提供所有卡片的當前消費與回饋總覽，以動態進度條 (Progress Bar) 顯示各加碼通道的使用率。
   - 支援無網路時的離線快取瀏覽。
4. **自動化爬蟲與額度警報**
   - 每月 1 號自動爬取銀行權益更新，比對並產生變更通知。
   - 每日自動掃描，當卡片額度使用率達 80% 或 100% (封頂) 時，推送警報提醒換卡。

---

## 🛠️ 技術架構

- **後端 (Backend)**: FastAPI (Python 3), SQLAlchemy (SQLite 非同步), APScheduler (自動排程), Google Gemini API (OCR 辨識)。
- **前端 (Mobile)**: React Native (Expo), AsyncStorage (離線快取)。

---

## 🚀 如何啟動專案？

專案分為「後端」與「前端」兩個部分，需要分別開啟兩個終端機 (Terminal) 執行。

### 先釐清：你現在看到的是「網頁」還是「手機 App」？

- 在 Expo 終端機按 `w`：是 **Web 預覽**（看起來像網站，正常）。
- 用 **Expo Go 掃 QR Code**：是 **手機實機開發模式**（你現在要的模式）。
- 目前專案是 Expo 開發流程，尚未打包成可安裝的商店版本，先用 Expo Go 最快。

### 步驟 1：啟動後端伺服器 (API)

後端負責處理資料庫、AI 辨識、爬蟲與推薦運算。

1. 打開終端機，進入後端資料夾：
   ```powershell
   cd D:\WORK\card-brain-app\backend
   ```
2. 設定 Gemini API Key (AI 辨識必備)：
   打開 `D:\WORK\card-brain-app\backend\.env` 檔案，填入你的 `GEMINI_API_KEY`（可至 Google AI Studio 申請）。
3. 啟動伺服器：
   ```powershell
   .\venv\Scripts\python.exe -m app.main
   ```
   _啟動成功後，伺服器會運行在 `http://localhost:8000`。你可以打開瀏覽器前往 `http://localhost:8000/docs` 查看 API 測試介面。_

### 步驟 2：啟動前端 App (手機畫面)

前端是你可以在手機或模擬器上操作的介面。

1. 打開**另一個新的終端機**，進入前端資料夾：
   ```powershell
   cd D:\WORK\card-brain-app\mobile
   ```
2. 啟動 Expo 開發伺服器 (若遇到 IP 跑掉的問題，請直接指定 IP，如 192.168.31.230)：
   ```powershell
   $env:REACT_NATIVE_PACKAGER_HOSTNAME="192.168.31.230"; npx expo start -c
   ```
3. 選擇要在哪裡開啟 App：
   - **在實體手機上跑**：下載「Expo Go」App，用手機相機掃描終端機顯示的 QR Code。
   - **在電腦網頁上跑**：在終端機按下 `w` 鍵。
   - **在 Android 模擬器上跑**：在終端機按下 `a` 鍵（需預先安裝 Android Studio）。

### 步驟 3：手機實機連不到後端時，先做這個（非常重要）

如果你用的是 **實體手機**，前端不能打 `localhost:8000`，因為手機上的 `localhost` 是「手機自己」，不是你的電腦。

#### 方案 A（同一個 Wi-Fi，最快）：改成電腦區網 IP

1. 在 Windows 終端機查詢電腦 IP：

   ```powershell
   ipconfig
   ```

   找到 IPv4（例如 `192.168.31.230`）。

2. 修改 `mobile/.env`（或是透過指令切換）：

   ```env
   EXPO_PUBLIC_API_URL=http://192.168.31.230:8000/api/v1
   ```

3. 為了避免 Expo 綁定到錯誤的網卡 IP（例如虛擬機或 Docker 網卡），啟動 Expo 時請強制指定 hostname。在終端機輸入：
   ```powershell
   $env:REACT_NATIVE_PACKAGER_HOSTNAME="192.168.31.230"; npx expo start -c
   ```
   *這樣終端機就會印出正確的 QR Code，讓您用手機掃描！*

#### 方案 B（不同網路或區網受限）：使用 Tunnel / ngrok

1. 在後端開 tunnel（範例）：
   ```powershell
   ngrok http 8000
   ```
2. 把公開網址填到 `mobile/.env`（記得尾端 `/api/v1`）：
   ```env
   EXPO_PUBLIC_API_URL=https://<your-ngrok-id>.ngrok-free.app/api/v1
   ```
3. 重新啟動 Expo，再用手機掃 QR 測試。

> 小提醒：iPhone 實機測試時，若區網掃碼不穩，可改用 `npx expo start --tunnel`。

### （新增）一鍵切換 LAN / Tunnel，不用手改 `.env`

在 `mobile` 目錄可以直接用：

```powershell
# 切換成 LAN（同 Wi-Fi）
npm run switch:lan -- 192.168.31.230

# 切換成 Tunnel / ngrok
npm run switch:tunnel -- https://<your-ngrok-id>.ngrok-free.app
```

執行後會自動更新 `mobile/.env` 的 `EXPO_PUBLIC_API_URL`，再重啟 Expo：

```powershell
npx expo start -c
```

---

## 🧪 測試與操作指南

當 App 成功啟動後，你可以透過以下流程測試功能：

1. **初始設定 (Onboarding)**
   - 切換到下方 Tab **「名下卡片」**，隨便勾選幾張你擁有的信用卡（例如「大戶卡」、「Richart 狗卡」），設定結帳日，然後點擊儲存。
2. **測試「消費決策推薦」**
   - 切換到 **「消費推薦」** Tab。
   - 輸入金額 `5000`，選擇 `Apple Pay`，點擊推薦。
   - 系統會告訴你現在刷哪張卡最划算。
3. **測試「相機與 AI 記帳」**
   - 切換到中間的 **「相機/掃描」** Tab。
   - 這裡有四個軌道：
     - **掃描電子發票**：如果你手邊有發票，可以直接掃描左側的 QR Code。
     - **AI 截圖辨識**：點擊選取你手機裡面的網購明細、或是 LINE Pay 結帳截圖，讓 Gemini AI 幫你辨識金額。
     - **手動記帳**：直接點最下方的筆，輸入一筆日幣消費（例如 5000 JPY），看看系統會不會自動幫你換算成台幣！
4. **查看「動態儀表板」**
   - 記帳完成後，切換回 **「總覽」** Tab。
   - 你會看到剛剛消費的金額已經累積上去，進度條往前推進，並告訴你已經賺了多少回饋金。
5. **測試「警報中心」**
   - 故意手動記一筆金額很大的消費（例如讓額度直接爆滿）。
   - 切換到 **「通知」** Tab，點擊畫面上的 **「手動觸發權益爬蟲與額度掃描」** 按鈕。
   - 幾秒後，你會看到「🔴 額度封頂」或「⚠️ 額度即將達上限」的警告通知跳出來！
