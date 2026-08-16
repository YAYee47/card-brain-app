const fs = require("fs");
const path = require("path");

const mode = process.argv[2];
const value = process.argv[3];

const envPath = path.join(__dirname, "..", ".env");

function fail(message) {
  console.error(`\n[switch-api-url] ${message}\n`);
  process.exit(1);
}

if (!mode || !["lan", "tunnel"].includes(mode)) {
  fail(
    "請指定模式: lan 或 tunnel。\n範例: npm run switch:lan -- 192.168.31.230",
  );
}

if (!value) {
  if (mode === "lan") {
    fail("LAN 模式需要提供 IP。\n範例: npm run switch:lan -- 192.168.31.230");
  }
  fail(
    "Tunnel 模式需要提供網址。\n範例: npm run switch:tunnel -- https://xxxx.ngrok-free.app",
  );
}

const apiBase =
  mode === "lan"
    ? `http://${value}:8000/api/v1`
    : `${value.replace(/\/$/, "")}/api/v1`;

let content = "";
if (fs.existsSync(envPath)) {
  content = fs.readFileSync(envPath, "utf8");
}

const line = `EXPO_PUBLIC_API_URL=${apiBase}`;
if (/^EXPO_PUBLIC_API_URL=.*$/m.test(content)) {
  content = content.replace(/^EXPO_PUBLIC_API_URL=.*$/m, line);
} else {
  content = content.trimEnd();
  content += `${content ? "\n\n" : ""}${line}\n`;
}

fs.writeFileSync(envPath, content, "utf8");

console.log("\n[switch-api-url] 已更新 mobile/.env");
console.log(`[switch-api-url] 模式: ${mode}`);
console.log(`[switch-api-url] EXPO_PUBLIC_API_URL=${apiBase}`);
console.log("[switch-api-url] 請重新啟動 Expo：npx expo start -c\n");
