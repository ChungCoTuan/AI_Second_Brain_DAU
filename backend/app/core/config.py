import os
import re

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DAU Second Brain API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dau_second_brain"

    # Bảo mật JWT - bắt buộc đặt SECRET_KEY trong .env khi chạy thật
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Danh sách origin frontend, phân tách bằng dấu phẩy
    CORS_ORIGINS: str = "http://localhost:5173"

    GEMINI_API_KEY: str | None = None
    GEMINI_API_KEY_2: str | None = None
    GEMINI_API_KEY_3: str | None = None

    # OCR qua Gemini API (khóa riêng, không dùng chung với chatbot)
    OCR_API_KEY: str = ""
    OCR_MODEL: str = ""
    OCR_TIMEOUT_SECONDS: int = 60
    OCR_MAX_PAGES: int = 20
    OCR_MAX_PDF_MB: int = 20
    OCR_MAX_IMAGE_MB: int = 4
    OCR_MAX_RETRIES: int = 3

    # Giới hạn số trang tối đa cho MỌI văn bản (kể cả bản có text layer).
    # Vượt giới hạn sẽ bị từ chối ngay lúc tải lên với thông báo rõ ràng.
    MAX_PAGES_PER_DOCUMENT: int = 100

    # Thư mục cache mô hình cục bộ; để trống thì dùng mặc định của Hugging Face.
    HF_HOME: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def cors_origin_regexes(self) -> list[str]:
        """Regex origin cho các domain động (ví dụ Tailscale Funnel `*.ts.net`).

        Chỉ dùng khi `CORS_ORIGINS` chứa mẫu `https://*.ts.net` — FastAPI/Starlette
        không hỗ trợ wildcard trong `allow_origins`, nên phải dùng regex.

        `*` được hiểu là "một hoặc nhiều tầng subdomain", ví dụ:
          https://*.ts.net  ->  https://laptop-ahuge8a3.tail-1a2b.ts.net
        """
        patterns: list[str] = []
        for origin in self.cors_origins_list:
            if "*" not in origin:
                continue
            # Tach scheme va host rieng biet de tranh escape 2 lan dau '.'.
            scheme, _, host = origin.partition("://")
            host_pattern = re.escape(host).replace(r"\*", r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*")
            patterns.append(f"^{re.escape(scheme)}://{host_pattern}$")
        return patterns

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()

# transformers/sentence-transformers đọc HF_HOME từ biến môi trường, không đọc .env.
# Gán sớm để app và scripts/download_models.py dùng chung một cache.
if settings.HF_HOME:
    os.environ.setdefault("HF_HOME", settings.HF_HOME)
