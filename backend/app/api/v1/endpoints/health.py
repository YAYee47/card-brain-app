from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="健康檢查端點")
async def health_check():
    """
    提供 App 前端與外部系統檢測後端 API 連線狀態之健康檢查端點。
    """
    return {
        "status": "ok",
        "service": "card-brain-backend",
        "version": "1.0.0"
    }
