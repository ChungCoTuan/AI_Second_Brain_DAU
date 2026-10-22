import pymupdf as fitz
import pytest
from PIL import Image

from app.core.config import settings
from app.services import pdf_parser
from app.services.ocr_api import OCRError


def make_pdf(path, pages: int):
    doc = fitz.open()
    for _ in range(pages):
        doc.new_page()
    doc.save(path)
    doc.close()
    return str(path)


def test_scanned_pdf_requires_explicit_consent(tmp_path):
    pdf = make_pdf(tmp_path / "scan.pdf", 1)

    with pytest.raises(RuntimeError, match="xác nhận"):
        pdf_parser.extract_text_from_pdf(pdf)


def test_scanned_pdf_over_page_limit_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "OCR_MAX_PAGES", 20)
    pdf = make_pdf(tmp_path / "scan21.pdf", 21)

    with pytest.raises(RuntimeError, match="20 trang"):
        pdf_parser.extract_text_from_pdf(pdf, allow_external_ocr=True)


def test_scanned_pdf_over_size_limit_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "OCR_MAX_PDF_MB", 0.000001)
    pdf = make_pdf(tmp_path / "scan.pdf", 1)

    with pytest.raises(RuntimeError, match="vượt giới hạn OCR"):
        pdf_parser.extract_text_from_pdf(pdf, allow_external_ocr=True)


def test_page_image_over_limit_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "OCR_MAX_IMAGE_MB", 0.000001)
    monkeypatch.setattr(
        "pdf2image.convert_from_path",
        lambda *args, **kwargs: [Image.new("RGB", (50, 50), "white")],
    )
    pdf = make_pdf(tmp_path / "scan.pdf", 1)

    with pytest.raises(RuntimeError, match="vượt giới hạn"):
        pdf_parser.extract_text_from_pdf(pdf, allow_external_ocr=True)


def test_ocr_keeps_page_format(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "pdf2image.convert_from_path",
        lambda *args, **kwargs: [Image.new("RGB", (800, 1000), "white")],
    )
    monkeypatch.setattr(pdf_parser, "extract_page_text", lambda data: "Điều 1. Nội dung tiếng Việt có dấu")
    pdf = make_pdf(tmp_path / "scan.pdf", 1)

    text = pdf_parser.extract_text_from_pdf(pdf, allow_external_ocr=True)

    assert text == "--- TRANG 1 ---\nĐiều 1. Nội dung tiếng Việt có dấu"


def test_ocr_errors_are_not_swallowed(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "pdf2image.convert_from_path",
        lambda *args, **kwargs: [Image.new("RGB", (800, 1000), "white")],
    )

    def boom(data):
        raise OCRError("hết quota")

    monkeypatch.setattr(pdf_parser, "extract_page_text", boom)
    pdf = make_pdf(tmp_path / "scan.pdf", 1)

    with pytest.raises(RuntimeError, match="hết quota"):
        pdf_parser.extract_text_from_pdf(pdf, allow_external_ocr=True)
