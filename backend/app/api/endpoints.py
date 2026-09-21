from fastapi import APIRouter
from .routers import documents, review, system, analytics, chat, audit, search

router = APIRouter()

router.include_router(documents.router, tags=["Documents"])
router.include_router(review.router, tags=["Review"])
router.include_router(system.router, tags=["System"])
router.include_router(analytics.router, tags=["Analytics"])
router.include_router(chat.router, tags=["Chat"])
router.include_router(audit.router, tags=["Audit"])
router.include_router(search.router, tags=["Search"])
