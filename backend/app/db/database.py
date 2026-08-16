from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# 建立非同步 SQLAlchemy 引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,      # 生產環境請設為 False
    future=True,
)

# 建立非同步 Session 工廠
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    """SQLAlchemy 2.0 宣告式基底類別"""
    pass

async def get_db() -> AsyncSession:
    """
    FastAPI 依賴注入用的資料庫 Session 生成器
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """
    初始化資料庫：建立所有 Table（若不存在）
    """
    from app.models import cards, user_cards, card_benefits, monthly_usage, transactions  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
