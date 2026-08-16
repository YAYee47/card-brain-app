from fastapi import APIRouter
from app.api.v1.endpoints import health, cards, recommend, transactions, dashboard, alerts, users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users & Auth"])
api_router.include_router(health.router, tags=["Health Check"])
api_router.include_router(cards.router, tags=["Cards"])
api_router.include_router(recommend.router, tags=["Recommendation"])
api_router.include_router(transactions.router, tags=["Transactions & OCR"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(alerts.router, tags=["Alerts & Crawler"])
