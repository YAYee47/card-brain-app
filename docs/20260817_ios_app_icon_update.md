# 2026-08-17 iOS App 圖示更新與原生專案編譯紀錄

## 變動摘要
本次更新主要為了解決 App 在 iPhone 裝置上安裝後，桌面圖示 (App Icon) 呈現空白 (預設白底無圖案) 的問題。

## 具體修改內容
1. **新增應用程式圖示 (App Icon)**
   - 繪製了一款結合「信用卡」與「晶片大腦」的高質感粉色系圖示。
   - 檔案路徑：`mobile/assets/icon.png`

2. **更新 Expo 設定檔 (`app.json`)**
   - 於 `expo` 區塊內加入 `"icon": "./assets/icon.png"` 屬性，指定原生專案編譯時使用的圖示來源。

3. **重新編譯 iOS 原生專案 (`ios/` 資料夾)**
   - 執行 `npx expo prebuild --platform ios` 重新生成了 iOS 原生專案。
   - 該指令自動將 `icon.png` 轉換並注入至 Xcode 的 `.xcassets` 資源包中，確保手機安裝後能正確顯示圖示。
   - 此操作同時將 `mobile/package.json` 中的 `ios` 與 `android` 啟動指令自動升級為原生建置指令 (`expo run:ios`)。

## 開發者後續動作
* 這些變更已經推送到 Git 上。
* 由於涉及原生 iOS 專案目錄 (`ios/`) 的變動，**開發者需將原手機上的 App 刪除，並在 Xcode 中重新執行編譯 (按下 ▶️ 播放鍵)**，新的桌面圖示才會正式生效。
