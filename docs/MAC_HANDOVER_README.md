# 💻 Mac 環境交接與開發啟動指南 (Card Brain App)

歡迎接手 **Card Brain** 專案！這份文件是專門寫給 Mac 上的 Google Antigravity 開發大腦（你的 AI 助手）與開發者，讓你們能快速無縫接軌目前的開發進度。

---

## 🎯 1. 專案現況與移轉目標
本專案是一個具備 AI 收據辨識、權益動態推薦與追蹤的「智能信用卡大腦」。
**歷史背景**：本專案前期完全在 Windows 環境下開發，目前功能已經趨於穩定。
**移轉目標**：將專案移轉至 Mac 的**最主要目的，是為了能將這個 App 安裝到使用者的 iPhone 上實機使用**。這可能需要透過 Expo Go，或是進行 iOS 的實機編譯（透過 Xcode 與 Apple 開發者模式）。

---

## 🚀 2. iPhone 實機安裝與後台雲端化計畫 
接下來在 Mac 上的首要任務有兩個：
1. **iPhone 實機安裝教學**：請帶領開發者開啟 iPhone 的「開發者模式」，並一步步教導如何透過 Mac 將這個 React Native (Expo) App 裝進他的 iPhone 裡運作。
2. **後端雲端部署**：目前後端 FastAPI 還是跑在 `localhost`。為了讓手機 App 能在日常生活中真實使用，必須協助將後端部署到雲端服務（例如 Render, Fly.io 或 Zeabur），並將前端的 API 連線網址替換為雲端網址。

---

## 🛠️ 3. Mac 環境啟動指令 (給開發者)

由於你已經切換到 macOS，指令與 Windows 會有一點點不同。請打開終端機並依序執行：

### 啟動後端 (FastAPI)
```bash
# 1. 進入後端資料夾
cd backend

# 2. 建立並啟動虛擬環境 (Mac 專用指令)
python3 -m venv venv
source venv/bin/activate

# 3. 安裝依賴套件
pip install -r requirements.txt

# 4. 啟動伺服器 (預設跑在 8000 port)
uvicorn app.main:app --reload
```
*(注意：若要測試 AI 辨識，請確保 Mac 環境變數中有設定 `GEMINI_API_KEY`)*

### 啟動前端 (Expo)
另開一個終端機視窗：
```bash
# 1. 進入前端資料夾
cd mobile

# 2. 安裝 Node 模組 (注意：請務必先刪除 Windows 拷貝過來的 node_modules，再重新執行安裝)
npm install

# 3. 啟動網頁開發伺服器
npm run web
```

---

## 🧠 4. 給 Google Antigravity 的系統交接指令 (System Prompt)

當你在 Mac 上啟動 Google Antigravity 時，請直接把這段指令貼給它：

> **「你好！我剛把在 Windows 上開發好的 Card Brain 專案移轉到這台 Mac 上。我會換到 Mac 開發的最主要目的，是為了『把這個 App 安裝到我的 iPhone 上』，並實際帶在身上使用。請你先閱讀 `docs/PROJECT_SUMMARY.md` 以及 `docs/MAC_HANDOVER_README.md`。讀完後，請一步步教我如何開啟 iPhone 的開發者模式，並把這個專案編譯/載入到我的手機上。同時，請協助規劃將後端 FastAPI 部署到 Render/Zeabur 等雲端環境，讓我的手機在外也能連線！」**
