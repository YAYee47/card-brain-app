# 2026-09-10 Mac Expo SDK 57 升級與修復紀錄

此文件為在 Mac 上拉取 Windows 環境 Expo SDK 57 (React Native 0.76) 升級代碼後的同步與修復紀錄。提供給未來在 Windows/Mac 間切換開發時參考。

## 1. 核心變更與同步
由於 Windows 環境將 Expo SDK 由 54 升級至 57，在 Mac 上拉取程式碼後，執行了以下同步動作：
- **套件安裝**：執行 `npm install` 重新下載對應新版本的 Node 套件。
- **iOS 原生專案重建**：由於跨越大版本，舊的 `ios` 資料夾與 CocoaPods 設定會失效，因此執行了 `npx expo prebuild --clean`，將 `ios` 資料夾完全移除並根據 SDK 57 的範本重新生成 `CardBrain.xcworkspace`。

## 2. 踩坑修復：CocoaPods 中文路徑編碼報錯
在重建 iOS 專案執行 `pod install` 時，發生以下嚴重的編譯錯誤：
```text
[!] Invalid `hermes-engine.podspec` file: incompatible character encodings: BINARY (ASCII-8BIT) and UTF-8.
```
**原因**：
React Native (0.74/0.76) 的 `hermes-engine.podspec` 在解析系統路徑時，若上層資料夾名稱包含中文字元（如本專案所在的 `/Users/chengyang/Desktop/芝蓉work`），Ruby 在執行 Node 腳本時會將中文字元誤判為 ASCII-8BIT 編碼，與文件預設的 UTF-8 衝突而導致崩潰。

**解決方案 (已透過 patch-package 永久修復)**：
我們直接修改了 `node_modules/react-native/sdks/hermes-engine/hermes-engine.podspec`，在執行 Node 指令的變數差值前，強制對路徑進行 UTF-8 編碼轉換 (`.force_encoding('UTF-8')`)。

為了讓這個修改能在不同電腦（包括 Windows 或未來重新安裝 `node_modules` 時）自動生效，我們引入了 `patch-package`：
1. 安裝了 `patch-package` 與 `postinstall-postinstall`。
2. 產生了補丁檔 `/mobile/patches/react-native+0.86.3.patch`。
3. 在 `package.json` 的 scripts 中加入了 `"postinstall": "patch-package"`。

**未來在 Windows 上開發時**：
當你在 Windows 執行 `npm install` 時，`patch-package` 會自動執行並修復這個底層 Bug。你不需要做任何額外設定！

## 3. iOS 實機打包憑證重置提醒
因為 `ios` 資料夾被 `--clean` 參數徹底重建，原本在 Xcode 中設定好的「Personal Team」憑證也被清除了。
這表示每次執行 `--clean` 之後，若要將 App 裝進手機，都必須**重新打開 Xcode，勾選 Automatically manage signing 並選擇 Team**。
