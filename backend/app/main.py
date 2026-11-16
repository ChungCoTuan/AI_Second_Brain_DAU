from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import endpoints

from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.ingestion.crawl_documents import crawl_chinhphu, check_new_chinhphu
from app.db.session import engine, ensure_sequences, SessionLocal
from app.db.models import Base
from app.core.fixed_account import sync_fixed_account, FIXED_ACCOUNT_EMAIL


def _sync_fixed_account() -> None:
    """Đồng bộ bảng `users` với tài khoản cố định duy nhất.

    Tự tạo nếu chưa có, đặt lại mật khẩu/vai trò nếu bị lệch, và xoá các
    tài khoản khác để hệ thống chỉ còn đúng một tài khoản đăng nhập.
    """
    db = SessionLocal()
    try:
        changed = sync_fixed_account(db)
        if changed:
            print(f"[AUTH] Đã đồng bộ tài khoản cố định: {FIXED_ACCOUNT_EMAIL}")
        else:
            print(f"[AUTH] Tài khoản cố định đã sẵn sàng: {FIXED_ACCOUNT_EMAIL}")
    except Exception as exc:  # noqa: BLE001 - không được chặn app khởi động
        print(f"[AUTH] Không đồng bộ được tài khoản cố định: {exc}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo DB
    Base.metadata.create_all(bind=engine)
    # Chuẩn hoá sequence cho các bảng có cột `id` (fix lỗi id=NULL sau pg_restore)
    ensure_sequences()

    # Tài khoản cố định duy nhất: admin@dau.edu.vn / Dau@Second2026
    _sync_fixed_account()

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

# CORS: chỉ cho phép origin frontend được cấu hình trong .env
# Ngoài danh sách tĩnh, hỗ trợ mẫu wildcard (vd `https://*.ts.net` cho Tailscale Funnel).
# Lưu ý: Starlette chỉ nhận MỘT chuỗi regex (không phải list).
_cors_regex = settings.cors_origin_regexes
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=_cors_regex[0] if _cors_regex else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
