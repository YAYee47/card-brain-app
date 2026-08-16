from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.router import api_router
from app.db.database import init_db, AsyncSessionLocal
from app.db.seed import seed_initial_data
from app.services.scheduler import setup_scheduler, scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan 事件：啟動時初始化資料庫 Table 並寫入 Seed 資料
    """
    print("[STARTUP] Card Brain Backend API starting...")
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)
    print("[STARTUP] DB initialization complete.")
    
    # 啟動排程器
    setup_scheduler(AsyncSessionLocal)
    scheduler.start()
    print("[STARTUP] APScheduler started.")
    
    yield
    
    # 關閉排程器
    scheduler.shutdown()
    print("[SHUTDOWN] Backend service shutting down.")

app = FastAPI(
    title="信用卡權益追蹤與智能額度管理 API",
    description="提供 React Native App 信用卡權益查詢、AI 視覺記帳、消費決策推薦與額度管理 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 設定跨域資源共享 (CORS)，允許 React Native 前端 (Expo) 跨域呼叫
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊 API 路由前綴 /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/", summary="根目錄連線測試")
async def root():
    """FastAPI 根目錄連線測試資訊"""
    return {
        "message": "歡迎使用信用卡權益追蹤與智能額度管理 API 服務",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
