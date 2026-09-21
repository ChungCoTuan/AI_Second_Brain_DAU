from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import endpoints

from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.ingestion.crawl_documents import crawl_chinhphu, check_new_chinhphu

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động Cron Job khi app start
    scheduler = BackgroundScheduler()
    # Hàng đêm lúc 2:00 sáng, chạy crawler tải tối đa 10 văn bản
    scheduler.add_job(crawl_chinhphu, 'cron', hour=2, minute=0, args=[10], id="nightly_crawler")
    # Cứ mỗi 30 phút, chạy ping kiểm tra văn bản mới cực nhẹ
    scheduler.add_job(check_new_chinhphu, 'interval', minutes=30, id="ping_chinhphu")
    scheduler.start()
    print("Đã khởi động Cron Job ngầm (APScheduler) cho luồng Theo dõi & Cào văn bản.")
    yield
    # Dọn dẹp khi app shutdown
    scheduler.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development. In production, change to specific origins.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
