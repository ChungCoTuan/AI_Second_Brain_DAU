"""OCR một trang ảnh qua Gemini API.

Module này thay thế Tesseract cục bộ. Không ghi log API key, ảnh hoặc nội dung
tài liệu; lỗi trả về chỉ chứa thông tin chẩn đoán an toàn.
"""

from __future__ import annotations

import base64
import logging
import random
import time
from typing import Any

import requests

from ..core.config import settings

logger = logging.getLogger(__name__)

_GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

# Chỉ các lỗi tạm thời mới được retry.
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_AUTH_STATUS = {401, 403}
_MAX_RETRY_AFTER_SECONDS = 10

_OCR_PROMPT = (
    "Bạn là công cụ OCR. Hãy chép lại NGUYÊN VĂN toàn bộ chữ trong ảnh trang "
    "tài liệu tiếng Việt, giữ đúng dấu, xuống dòng, thứ tự và số hiệu điều khoản. "
    "Không tóm tắt, không giải thích, không thêm bình luận, không bịa nội dung. "
    "Nếu trang không có chữ, trả về chuỗi rỗng."
)


class OCRError(RuntimeError):
    """Lỗi OCR chung, thông điệp an toàn để hiển thị cho người dùng."""


class OCRConfigurationError(OCRError):
    """Thiếu cấu hình OCR_API_KEY/OCR_MODEL."""


class OCRAuthError(OCRError):
    """API từ chối xác thực hoặc quyền của key."""


class OCRTemporaryError(OCRError):
    """Lỗi tạm thời: timeout, mạng, 429 hoặc 5xx."""


class OCRResponseError(OCRError):
    """Phản hồi không dùng được: request sai, model sai, bị chặn, kết quả bị cắt."""


def extract_page_text(image_bytes: bytes) -> str:
    """Gửi một ảnh JPEG của một trang tới Gemini và trả về text đã trích xuất."""
    if not settings.OCR_API_KEY or not settings.OCR_MODEL:
        raise OCRConfigurationError(
            "Chưa cấu hình OCR. Hãy đặt OCR_API_KEY và OCR_MODEL trong backend/.env."
        )
    if not image_bytes:
        raise OCRResponseError("Ảnh trang rỗng, không thể OCR.")

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": _OCR_PROMPT},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64.b64encode(image_bytes).decode("ascii"),
                        }
                    },
                ],
            }
        ],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 8192},
    }
    url = _GEMINI_ENDPOINT.format(model=settings.OCR_MODEL)
    headers = {
        "x-goog-api-key": settings.OCR_API_KEY,
        "Content-Type": "application/json",
    }

    attempts = settings.OCR_MAX_RETRIES + 1
    last_message = "không rõ nguyên nhân"

    for attempt in range(attempts):
        retry_after: float | None = None
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=(10, settings.OCR_TIMEOUT_SECONDS),
            )
        except requests.Timeout:
            last_message = "quá thời gian chờ"
        except requests.RequestException:
            last_message = "lỗi kết nối mạng"
        else:
            if response.status_code == 200:
                return _parse_response(response.json())
            if response.status_code in _AUTH_STATUS:
                raise OCRAuthError(
                    "Dịch vụ OCR từ chối xác thực hoặc quyền của OCR_API_KEY "
                    f"(HTTP {response.status_code}). Kiểm tra lại key và quyền truy cập model."
                )
            if response.status_code == 429:
                last_message = "hết quota hoặc bị giới hạn tần suất (HTTP 429)"
                retry_after = _retry_after_seconds(response)
            elif response.status_code in _RETRYABLE_STATUS:
                last_message = f"dịch vụ tạm thời lỗi (HTTP {response.status_code})"
            elif response.status_code in (400, 404):
                raise OCRResponseError(
                    "Yêu cầu OCR không hợp lệ hoặc không tìm thấy OCR_MODEL "
                    f"(HTTP {response.status_code}). Kiểm tra lại cấu hình."
                )
            else:
                raise OCRResponseError(
                    f"Dịch vụ OCR trả lỗi HTTP {response.status_code}."
                )

        if attempt < attempts - 1:
            time.sleep(_backoff_seconds(attempt, retry_after))

    raise OCRTemporaryError(
        f"OCR thất bại sau {attempts} lần thử: {last_message}. Vui lòng thử lại sau."
    )


def _parse_response(data: dict[str, Any]) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        block_reason = (data.get("promptFeedback") or {}).get("blockReason")
        suffix = f" (bị chặn: {block_reason})" if block_reason else ""
        raise OCRResponseError(f"Dịch vụ OCR không trả về kết quả{suffix}.")

    candidate = candidates[0]
    finish_reason = candidate.get("finishReason")
    if finish_reason == "MAX_TOKENS":
        raise OCRResponseError(
            "Trang quá dài nên kết quả OCR bị cắt. Hãy chia nhỏ tài liệu rồi thử lại."
        )
    if finish_reason in {"SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT"}:
        raise OCRResponseError(
            f"Dịch vụ OCR từ chối nội dung trang (finishReason={finish_reason})."
        )

    parts = (candidate.get("content") or {}).get("parts") or []
    text = "\n".join(part.get("text", "") for part in parts if part.get("text"))
    return text.strip()


def _retry_after_seconds(response: requests.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if not value:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None
    return max(0.0, min(seconds, _MAX_RETRY_AFTER_SECONDS))


def _backoff_seconds(attempt: int, retry_after: float | None) -> float:
    if retry_after is not None:
        return retry_after
    base = min(2 ** attempt, 8)
    return base * (0.5 + random.random() * 0.5)
