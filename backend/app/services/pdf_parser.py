import io
import os
import re
from typing import Dict, List

import pymupdf as fitz  # PyMuPDF

from ..core.config import settings
from .ocr_api import extract_page_text


def extract_text_from_pdf(pdf_path: str, *, allow_external_ocr: bool = False) -> str:
    """
    Đọc file PDF và trích xuất toàn bộ văn bản thô.
    Sử dụng PyMuPDF (fitz) để giải quyết lỗi font (cid:xxx) của các file scan hoặc subset fonts.
    Hỗ trợ Fallback OCR qua API nếu phát hiện file scan.

    allow_external_ocr: phải bật rõ ràng để gửi ảnh trang ra dịch vụ OCR bên ngoài.
    Mặc định tắt để tránh vô tình gửi tài liệu nhạy cảm ra ngoài.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Không tìm thấy file PDF tại: {pdf_path}")
        
    extracted_text = []
    total_words = 0
    total_pages = 0
    
    try:
        # Mở file PDF bằng PyMuPDF
        with fitz.open(pdf_path) as pdf:
            total_pages = len(pdf)
            for i in range(total_pages):
                page = pdf[i]
                text = page.get_text("text")
                if text.strip():
                    extracted_text.append(f"--- TRANG {i+1} ---\n{text.strip()}")
                    total_words += len(text.split())
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")

    # Fallback OCR
    if total_pages > 0 and (total_words / total_pages < 20):
        if not allow_external_ocr:
            raise RuntimeError(
                "Văn bản này là bản scan. Cần xác nhận tài liệu không chứa dữ liệu "
                "nhạy cảm trước khi gửi ảnh trang tới dịch vụ OCR bên ngoài."
            )

        if total_pages > settings.OCR_MAX_PAGES:
            raise RuntimeError(
                f"Văn bản scan có {total_pages} trang, vượt giới hạn OCR "
                f"{settings.OCR_MAX_PAGES} trang. Vui lòng chia nhỏ file PDF."
            )

        size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        if size_mb > settings.OCR_MAX_PDF_MB:
            raise RuntimeError(
                f"File PDF {size_mb:.1f} MB vượt giới hạn OCR "
                f"{settings.OCR_MAX_PDF_MB} MB. Vui lòng giảm dung lượng hoặc chia nhỏ file."
            )

        print(f"Phát hiện file scan ({total_words} từ / {total_pages} trang), kích hoạt Fallback OCR qua API...")
        ocr_result = _extract_text_via_ocr(pdf_path)
        if ocr_result:
            extracted_text = ocr_result

    full_text = "\n\n".join(extracted_text)
    return full_text


def _extract_text_via_ocr(pdf_path: str) -> List[str]:
    """
    Render từng trang PDF thành JPEG rồi gọi OCR API.
    Giữ nguyên định dạng trả về "--- TRANG N ---\\n..." như luồng Tesseract cũ.
    """
    from pdf2image import convert_from_path

    print(f"Bắt đầu convert PDF sang ảnh để OCR: {pdf_path}")
    images = convert_from_path(
        pdf_path,
        dpi=150,
        fmt="jpeg",
        jpegopt={"quality": 75},
        thread_count=1,
        first_page=1,
        last_page=settings.OCR_MAX_PAGES,
    )

    max_image_bytes = settings.OCR_MAX_IMAGE_MB * 1024 * 1024
    extracted: List[str] = []

    for i, image in enumerate(images):
        print(f"OCR trang {i + 1}...")
        image_bytes = _encode_page_image(image, max_image_bytes)
        text = extract_page_text(image_bytes)
        if text.strip():
            extracted.append(f"--- TRANG {i+1} ---\n{text.strip()}")

    return extracted


def _encode_page_image(image, max_bytes: int) -> bytes:
    """Chuẩn hoá ảnh trang thành JPEG nhỏ hơn giới hạn trước khi gửi API."""
    from PIL import Image

    if image.mode != "RGB":
        image = image.convert("RGB")

    max_side = 2000
    if max(image.size) > max_side:
        image.thumbnail((max_side, max_side), Image.LANCZOS)

    for quality in (75, 60, 45):
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        data = buffer.getvalue()
        if len(data) <= max_bytes:
            return data

    raise RuntimeError(
        f"Ảnh trang sau khi nén vẫn vượt giới hạn {settings.OCR_MAX_IMAGE_MB} MB. "
        "Vui lòng giảm độ phân giải hoặc chia nhỏ tài liệu."
    )

def chunk_document(text: str) -> List[Dict[str, str]]:
    """
    Adaptive Chunking: Cắt văn bản theo các cấp độ ưu tiên (Thác đổ).
    Hỗ trợ: Điều -> Chương/Phần -> Số La Mã -> Số thường -> Trang.
    """
    patterns = {
        "dieu": r'\n(?=Điều\s+\d+)',
        "chuong_phan": r'\n(?=(?:Chương|Phần)\s+[IVX\d]+)',
        "la_ma": r'\n(?=[IVX]+\.\s)',
        "so": r'\n(?=\d+\.\s)',
        "trang": r'\n(?=---\sTRANG)'
    }
    
    chosen_pattern_key = "trang"
    
    # 1. Đo lường để chọn pattern phù hợp nhất
    if len(re.findall(patterns["dieu"], text, re.IGNORECASE)) >= 2:
        chosen_pattern_key = "dieu"
    elif len(re.findall(patterns["chuong_phan"], text, re.IGNORECASE)) >= 2:
        chosen_pattern_key = "chuong_phan"
    elif len(re.findall(patterns["la_ma"], text)) >= 2:
        chosen_pattern_key = "la_ma"
    elif len(re.findall(patterns["so"], text)) >= 3:
        chosen_pattern_key = "so"
        
    # 2. Bắt đầu chặt văn bản
    split_regex = patterns[chosen_pattern_key]
    if chosen_pattern_key in ["dieu", "chuong_phan"]:
        raw_chunks = re.split(split_regex, text, flags=re.IGNORECASE)
    else:
        raw_chunks = re.split(split_regex, text)
        
    chunks = []
    
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk: continue
        
        # Bỏ qua phần rác mào đầu nếu văn bản có cấu trúc chuẩn
        if chosen_pattern_key == "dieu" and not chunk.lower().startswith("điều"): continue
        if chosen_pattern_key == "chuong_phan" and not (chunk.lower().startswith("chương") or chunk.lower().startswith("phần")): continue
        
        # LỌC MỤC LỤC: Bỏ qua nếu đoạn text chứa quá nhiều dấu chấm nối tiếp (Ví dụ: ..... 12)
        if len(re.findall(r'\.\.\.\.\.', chunk)) > 2:
            continue
            
        lines = chunk.split('\n', 1)
        header_line = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ""
        
        dieu_so = ""
        tieu_de = ""
        
        # Bóc tách tên Mục / Điều / Phần
        if chosen_pattern_key == "dieu":
            match = re.match(r"(Điều\s+\d+)(.*)", header_line, re.IGNORECASE)
            if match:
                dieu_so = match.group(1).strip()
                tieu_de = match.group(2).strip(" .:-") 
        elif chosen_pattern_key == "chuong_phan":
            match = re.match(r"((?:Chương|Phần)\s+[IVX\d]+)(.*)", header_line, re.IGNORECASE)
            if match:
                dieu_so = match.group(1).strip()
                tieu_de = match.group(2).strip(" .:-")
        elif chosen_pattern_key == "la_ma":
            match = re.match(r"([IVX]+\.)(.*)", header_line)
            if match:
                dieu_so = "Mục " + match.group(1).strip()
                tieu_de = match.group(2).strip(" .:-")
        elif chosen_pattern_key == "so":
            match = re.match(r"(\d+\.)(.*)", header_line)
            if match:
                dieu_so = "Mục " + match.group(1).strip()
                tieu_de = match.group(2).strip(" .:-")
        elif chosen_pattern_key == "trang":
            match = re.match(r"(---\sTRANG\s\d+\s---)(.*)", header_line)
            if match:
                dieu_so = match.group(1).strip("- ")
                tieu_de = match.group(2).strip(" .:-")
                
        if not dieu_so:
            dieu_so = "Đoạn văn"
            tieu_de = header_line[:50]
            
        chunks.append({
            "dieu_so": dieu_so,
            "tieu_de": tieu_de,
            "noi_dung": content,
            "raw": chunk
        })
        
    return chunks
