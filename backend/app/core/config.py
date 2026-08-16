import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    後端應用程式全局設定類別
    """
    PROJECT_NAME: str = "信用卡權益追蹤與智能額度管理 API"
    VERSION: str = "1.0.0"
    
    # 開發環境預設採用 SQLite (Async) 本地檔案資料庫，生產環境可替換為 PostgreSQL (asyncpg)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./card_brain.db")
    GEMINI_API_KEY: str | None = None

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
