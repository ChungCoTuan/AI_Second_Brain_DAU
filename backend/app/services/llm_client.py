"""Client LLM thống nhất cho hệ thống DAU Second Brain.

Hỗ trợ hai chế độ:
1. ``gemini`` — Gemini native (google.generativeai / generativelanguage.googleapis.com).
2. ``openai`` — endpoint tương thích OpenAI (OpenAI-compatible gateway),
   dùng cho cả chat (RAG) và OCR (vision) qua ``/v1/chat/completions``.

Chế độ được chọn bằng biến môi trường ``LLM_PROVIDER`` (mặc định ``gemini``).
"""

from __future__ import annotations

import base64
import os
import threading
import time
from pathlib import Path
from typing import Any

import requests

# Nạp .env của backend (thư mục cha của app/) để cấu hình luôn có hiệu lực,
# bất kể tiến trình được khởi chạy từ thư mục nào.
try:
    from dotenv import load_dotenv

    _env_file = Path(__file__).resolve().parents[2] / ".env"
    if _env_file.is_file():
        load_dotenv(_env_file, override=False)
except Exception:  # noqa: BLE001 - thiếu dotenv không nên làm sập app
    pass

# Một số gateway phía sau Cloudflare chặn user-agent mặc định của python-requests
# (HTTP 403 / error code 1010), nên ta luôn gửi kèm UA trình duyệt.
_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def get_provider() -> str:
    """``gemini`` hoặc ``openai``."""
    return (os.getenv("LLM_PROVIDER") or "gemini").strip().lower()


def get_base_url() -> str:
    """Base URL của endpoint OpenAI-compatible (không có dấu / ở cuối)."""
    base = (
        os.getenv("LLM_BASE_URL")
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("OPENAI_API_BASE")
        or ""
    ).strip()
    if base and not base.endswith("/"):
        base += "/"
    return base


def get_api_keys() -> list[str]:
    """Danh sách key theo thứ tự ưu tiên, đã loại bỏ giá trị rỗng."""
    names = [
        "LLM_API_KEY",
        "GEMINI_API_KEY",
        "GEMINI_API_KEY_2",
        "GEMINI_API_KEY_3",
        "OPENAI_API_KEY",
    ]
    keys: list[str] = []
    for name in names:
        value = (os.getenv(name) or "").strip()
        if value and value not in keys:
            keys.append(value)
    return keys


def get_model(default: str = "") -> str:
    model = (os.getenv("LLM_MODEL") or os.getenv("GEMINI_MODEL") or "").strip()
    return model or default


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": _BROWSER_UA,
    }


# Một số gateway giới hạn số request đồng thời (lỗi 429 "too many concurrent").
# Ta dùng semaphore toàn cục để giới hạn số request chạy song song.
# Mặc định 4: đo thực tế cho thấy 4 request đồng thời giúp OCR nhanh gấp ~2.3 lần
# so với tuần tự, và gateway vẫn trả 200 (429 chỉ xảy ra khi vượt ngưỡng).
_MAX_CONCURRENT = int(os.getenv("LLM_MAX_CONCURRENT", "4"))
_semaphore = threading.Semaphore(max(1, _MAX_CONCURRENT))


def _acquire() -> None:
    _semaphore.acquire()


def _release() -> None:
    _semaphore.release()


def chat_completion(
    messages: list[dict[str, Any]],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.0,
    timeout: int = 120,
    max_retries: int = 4,
) -> str:
    """Gọi ``POST {base}/chat/completions`` và trả về nội dung text.

    ``messages`` theo chuẩn OpenAI: ``{"role": ..., "content": str | [parts]}``.
    Tự retry khi gateway trả 429 (quá nhiều request đồng thời) hoặc 5xx.
    """
    key = api_key or (get_api_keys() or [""])[0]
    root = (base_url or get_base_url()).rstrip("/")
    if not root:
        raise RuntimeError("Chưa cấu hình LLM_BASE_URL cho endpoint OpenAI-compatible.")
    if not key:
        raise RuntimeError("Chưa cấu hình API key cho LLM.")

    url = f"{root}/chat/completions"
    payload: dict[str, Any] = {
        "model": model or get_model("claude-fable-5"),
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    last_error = ""
    for attempt in range(max(1, max_retries)):
        response = None
        _acquire()
        try:
            response = requests.post(
                url,
                json=payload,
                headers=_headers(key),
                timeout=(10, timeout),
            )
        except requests.Timeout as exc:
            last_error = f"timeout: {exc}"
        except requests.RequestException as exc:
            last_error = f"network error: {exc}"
        finally:
            _release()

        if response is not None:
            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices") or []
                if not choices:
                    raise RuntimeError("LLM không trả về lựa chọn nào.")
                message = choices[0].get("message") or {}
                content = message.get("content")
                if isinstance(content, list):  # một số gateway trả content dạng mảng parts
                    content = "".join(
                        part.get("text", "")
                        for part in content
                        if isinstance(part, dict) and part.get("text")
                    )
                return (content or "").strip()

            last_error = f"LLM HTTP {response.status_code}: {response.text[:300]}"
            if response.status_code not in (429, 500, 502, 503, 504):
                raise RuntimeError(last_error)

        if attempt < max_retries - 1:
            # Backoff tăng dần: 2s, 4s, 8s, 16s
            time.sleep(min(2 ** (attempt + 1), 16))

    raise RuntimeError(last_error or "LLM không phản hồi.")


def image_message(prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> list[dict[str, Any]]:
    """Dựng message OpenAI-compatible chứa ảnh inline (data URI)."""
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
                },
            ],
        }
    ]
