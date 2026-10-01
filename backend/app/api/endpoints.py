from fastapi import APIRouter
from .routers import documents, review, system, analytics, chat, audit, search, auth, reports

router = APIRouter()

router.include_router(documents.router, tags=["Documents"])
router.include_router(review.router, tags=["Review"])
router.include_router(system.router, tags=["System"])
router.include_router(analytics.router, tags=["Analytics"])
router.include_router(chat.router, tags=["Chat"])
router.include_router(audit.router, tags=["Audit"])
router.include_router(search.router, tags=["Search"])
router.include_router(auth.router, tags=["Auth"])
router.include_router(reports.router, prefix="/reports", tags=["Reports"])
