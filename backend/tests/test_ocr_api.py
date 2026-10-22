import pytest

from app.core.config import settings
from app.services import ocr_api


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None, headers: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = headers or {}

    def json(self) -> dict:
        return self._payload


def gemini_payload(text: str, finish_reason: str = "STOP") -> dict:
    return {
        "candidates": [
            {
                "finishReason": finish_reason,
                "content": {"parts": [{"text": text}]},
            }
        ]
    }


@pytest.fixture(autouse=True)
def ocr_settings(monkeypatch):
    monkeypatch.setattr(settings, "OCR_API_KEY", "test-key")
    monkeypatch.setattr(settings, "OCR_MODEL", "test-model")
    monkeypatch.setattr(settings, "OCR_TIMEOUT_SECONDS", 5)
    monkeypatch.setattr(settings, "OCR_MAX_RETRIES", 2)
    monkeypatch.setattr(ocr_api.time, "sleep", lambda *_: None)


def test_extract_page_text_success(monkeypatch):
    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append((url, headers, timeout))
        return FakeResponse(200, gemini_payload("Điều 1. Nội dung có dấu"))

    monkeypatch.setattr(ocr_api.requests, "post", fake_post)

    text = ocr_api.extract_page_text(b"jpeg-bytes")

    assert text == "Điều 1. Nội dung có dấu"
    assert len(calls) == 1
    url, headers, timeout = calls[0]
    assert "test-model" in url
    assert headers["x-goog-api-key"] == "test-key"
    assert "test-key" not in url
    assert timeout == (10, 5)


def test_missing_config_does_not_call_network(monkeypatch):
    monkeypatch.setattr(settings, "OCR_API_KEY", "")

    def fail(*args, **kwargs):
        raise AssertionError("Không được gọi mạng khi thiếu cấu hình")

    monkeypatch.setattr(ocr_api.requests, "post", fail)

    with pytest.raises(ocr_api.OCRConfigurationError):
        ocr_api.extract_page_text(b"jpeg-bytes")


def test_retries_on_429_then_succeeds(monkeypatch):
    responses = iter(
        [
            FakeResponse(429, {"error": {"message": "quota"}}, {"Retry-After": "1"}),
            FakeResponse(200, gemini_payload("Trang 2")),
        ]
    )
    call_count = {"n": 0}

    def fake_post(*args, **kwargs):
        call_count["n"] += 1
        return next(responses)

    monkeypatch.setattr(ocr_api.requests, "post", fake_post)

    assert ocr_api.extract_page_text(b"jpeg") == "Trang 2"
    assert call_count["n"] == 2


def test_auth_error_is_not_retried(monkeypatch):
    call_count = {"n": 0}

    def fake_post(*args, **kwargs):
        call_count["n"] += 1
        return FakeResponse(401, {"error": {"message": "invalid key test-key"}})

    monkeypatch.setattr(ocr_api.requests, "post", fake_post)

    with pytest.raises(ocr_api.OCRAuthError) as exc_info:
        ocr_api.extract_page_text(b"jpeg")

    assert call_count["n"] == 1
    assert "test-key" not in str(exc_info.value)


def test_timeout_retries_then_raises(monkeypatch):
    call_count = {"n": 0}

    def fake_post(*args, **kwargs):
        call_count["n"] += 1
        raise ocr_api.requests.Timeout("timeout")

    monkeypatch.setattr(ocr_api.requests, "post", fake_post)

    with pytest.raises(ocr_api.OCRTemporaryError):
        ocr_api.extract_page_text(b"jpeg")

    # OCR_MAX_RETRIES = 2 => 3 lần thử
    assert call_count["n"] == 3


def test_truncated_output_is_rejected(monkeypatch):
    monkeypatch.setattr(
        ocr_api.requests,
        "post",
        lambda *a, **kw: FakeResponse(200, gemini_payload("bị cắt", "MAX_TOKENS")),
    )

    with pytest.raises(ocr_api.OCRResponseError) as exc_info:
        ocr_api.extract_page_text(b"jpeg")

    assert "bị cắt" in str(exc_info.value)
