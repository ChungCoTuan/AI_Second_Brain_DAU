import io
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

import pymupdf as fitz  # PyMuPDF

from ..core.config import settings
from .ocr_api import extract_page_text

# Số trang OCR được gửi SONG SONG tới gateway.
# Đo thực tế: conc=1 -> ~12.0s/trang, conc=4 -> ~5.3s/trang (nhanh gấp 2.3).
# Gateway chấp nhận 4 request đồng thời; quá ngưỡng sẽ trả 429.
_OCR_CONCURRENCY = int(os.getenv("OCR_CONCURRENCY", "4"))

# Nghỉ giữa 2 đợt OCR để không vượt giới hạn request đồng thời của dịch vụ LLM.
# Với OCR song song, delay này chỉ áp dụng giữa các lô.
_OCR_PAGE_DELAY_SECONDS = float(os.getenv("OCR_PAGE_DELAY_SECONDS", "0"))


def extract_text_from_pdf(
    pdf_path: str,
    *,
    allow_external_ocr: bool = False,
    progress_callback=None,
) -> str:
    """
    Đọc file PDF và trích xuất toàn bộ văn bản thô.
    Sử dụng PyMuPDF (fitz) để giải quyết lỗi font (cid:xxx) của các file scan hoặc subset fonts.
    Hỗ trợ Fallback OCR qua API nếu phát hiện file scan.

    allow_external_ocr: phải bật rõ ràng để gửi ảnh trang ra dịch vụ OCR bên ngoài.
    Mặc định tắt để tránh vô tình gửi tài liệu nhạy cảm ra ngoài.
    progress_callback: callable(page_no, total_pages) để báo tiến trình OCR theo trang.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Không tìm thấy file PDF tại: {pdf_path}")
        
    extracted_text = []
    total_words = 0
    total_pages = 0
    # Callback chỉ dùng cho nhánh đọc text layer; nhánh OCR sẽ báo tiến trình riêng.
    text_layer_callback = progress_callback

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
        ocr_result = _extract_text_via_ocr(pdf_path, progress_callback=progress_callback)
        if ocr_result:
            extracted_text = ocr_result
    elif text_layer_callback and total_pages:
        # Bản có sẵn text layer: báo tiến trình đọc từng trang.
        for i in range(total_pages):
            try:
                text_layer_callback(i + 1, total_pages)
            except Exception:  # noqa: BLE001
                pass

    full_text = "\n\n".join(extracted_text)
    return full_text


def _extract_text_via_ocr(pdf_path: str, progress_callback=None) -> List[str]:
    """
    Render từng trang PDF thành JPEG rồi gọi OCR API.
    Giữ nguyên định dạng trả về "--- TRANG N ---\\n..." như luồng Tesseract cũ.

    Render TỪNG TRANG một (không convert cả tài liệu cùng lúc) để tránh tràn RAM
    trên máy có page file nhỏ (WinError 1455 khi nạp torch).
    """
    from pdf2image import convert_from_path

    max_image_bytes = settings.OCR_MAX_IMAGE_MB * 1024 * 1024

    total_pages = _count_pages(pdf_path)
    last_page = min(total_pages, settings.OCR_MAX_PAGES)

    def _ocr_one_page(page_no: int) -> str:
        """Render + OCR một trang. Trả về text (rỗng nếu lỗi)."""
        print(f"OCR trang {page_no}/{last_page}...")
        images = convert_from_path(
            pdf_path,
            dpi=150,
            fmt="jpeg",
            jpegopt={"quality": 75},
            thread_count=1,
            first_page=page_no,
            last_page=page_no,
        )
        if not images:
            return ""
        try:
            image_bytes = _encode_page_image(images[0], max_image_bytes)
            return extract_page_text(image_bytes)
        except Exception as exc:  # noqa: BLE001 - lỗi 1 trang không nên dừng cả tài liệu
            print(f"[OCR] Lỗi ở trang {page_no}: {type(exc).__name__}: {exc}")
            return ""
        finally:
            # Giải phóng ảnh ngay để không giữ nhiều trang trong RAM
            images.clear()

    # OCR SONG SONG: mỗi worker giữ 1 trang trong RAM tại một thời điểm.
    # Đo thực tế: tuần tự ~12.0s/trang -> song song 4 worker ~5.3s/trang.
    concurrency = max(1, min(_OCR_CONCURRENCY, last_page))
    results: Dict[int, str] = {}

    if concurrency == 1:
        for page_no in range(1, last_page + 1):
            results[page_no] = _ocr_one_page(page_no)
            if progress_callback:
                try:
                    progress_callback(page_no, last_page)
                except Exception:  # noqa: BLE001
                    pass
            if page_no < last_page and _OCR_PAGE_DELAY_SECONDS > 0:
                time.sleep(_OCR_PAGE_DELAY_SECONDS)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {
                executor.submit(_ocr_one_page, page_no): page_no
                for page_no in range(1, last_page + 1)
            }
            done_count = 0
            for future, page_no in futures.items():
                results[page_no] = future.result()
                done_count += 1
                if progress_callback:
                    try:
                        progress_callback(done_count, last_page)
                    except Exception:  # noqa: BLE001
                        pass

    extracted: List[str] = []
    for page_no in range(1, last_page + 1):
        text = clean_ocr_text(results.get(page_no) or "")
        if text:
            extracted.append(f"--- TRANG {page_no} ---\n{text}")

    return extracted


def _count_pages(pdf_path: str) -> int:
    """Đếm số trang của PDF, trả về 0 nếu không đọc được."""
    try:
        import fitz

        with fitz.open(pdf_path) as doc:
            return doc.page_count
    except Exception:  # noqa: BLE001 - fallback khi thiếu PyMuPDF
        try:
            from pdf2image import pdfinfo_from_path

            return int(pdfinfo_from_path(pdf_path).get("Pages", 0))
        except Exception:  # noqa: BLE001
            return 0


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

def clean_ocr_text(text: str) -> str:
    """Làm sạch text thô từ OCR API.

    OCR trả về bản trích của PDF scan kèm nhiều khoảng trắng thừa ở cuối dòng
    và ký tự "+" từ footer watermark (VD: "Nội dung +        ").
    Nếu không làm sạch, chunking và truy hồi vector sẽ bị nhiễu nặng.

    - Chuẩn hoá ký tự xuống dòng (gateway có thể trả "\\n" dạng 2 ký tự literal).
    - Bỏ ký tự "+" đứng riêng ở cuối dòng (footer watermark).
    - Rút gọn khoảng trắng thừa nhưng GIỮ ngắt dòng (quan trọng cho chunking).
    - Gộp các dòng trống liên tiếp.
    """
    if not text:
        return text

    # 1) Chuẩn hoá newline: một số gateway trả về "\\n" dạng HAI ký tự literal
    #    (backslash + n) thay vì newline thật. Nếu không sửa, các tiêu đề "Điều N"
    #    nằm giữa dòng sẽ không được nhận diện và bị chunking BỎ MẤT.
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")
    text = text.replace("\\t", "\t")

    lines = text.split("\n")
    cleaned: list[str] = []
    for line in lines:
        # Bỏ ký tự '+' thừa ở cuối dòng (footer watermark của cổng thông tin)
        line = re.sub(r"[ \t ]*\+[ \t]*$", "", line)
        # Rút gọn khoảng trắng thừa, giữ ngắt dòng
        line = re.sub(r"[ \t ]{2,}", " ", line).rstrip()
        cleaned.append(line)

    # Gộp dòng trống liên tiếp, bỏ dòng trống đầu/cuối
    out: list[str] = []
    blank = False
    for line in cleaned:
        if not line.strip():
            if blank:
                continue
            blank = True
        else:
            blank = False
        out.append(line)

    return "\n".join(out).strip()


def chunk_document(text: str) -> List[Dict[str, str]]:
    """
    Adaptive Chunking: Cắt văn bản theo các cấp độ ưu tiên (Thác đổ).
    Hỗ trợ: Điều -> Chương/Phần -> Số La Mã -> Số thường -> Trang.
    """
    patterns = {
        # Cho phép khoảng trắng/indent trước "Điều" vì OCR PDF scan thường
        # đặt tiêu đề điều ở đầu dòng nhưng có thụt lề (ví dụ "        Điều 1.").
        "dieu": r'\n[ \t\u00a0]*(?=Điều\s*\d+|Dieu\s*\d+)',
        "chuong_phan": r'\n[ \t\u00a0]*(?=(?:Chương|Phần|Chuong|Phan)\s+[IVX\d]+)',
        "la_ma": r'\n[ \t\u00a0]*(?=[IVX]+\.\s)',
        "so": r'\n[ \t\u00a0]*(?=\d+\.\s)',
        "trang": r'\n[ \t\u00a0]*(?=---\s*TRANG)'
    }
    
    chosen_pattern_key = "trang"
    
    # 1. Đo lường để chọn pattern phù hợp nhất
    #    Dùng bộ đếm riêng (không phụ thuộc split regex) để tránh false-positive.
    count_dieu = len(re.findall(r'(?m)^[ \t\u00a0]*(?:Điều|Dieu)\s*\d+', text, re.IGNORECASE))
    count_chuong = len(re.findall(r'(?m)^[ \t\u00a0]*(?:Chương|Phần|Chuong|Phan)\s+[IVX\d]+', text, re.IGNORECASE))
    count_lama = len(re.findall(r'(?m)^[ \t\u00a0]*[IVX]+\.\s', text))
    count_so = len(re.findall(r'(?m)^[ \t\u00a0]*\d+\.\s', text))
    
    if count_dieu >= 2:
        chosen_pattern_key = "dieu"
    elif count_chuong >= 2:
        chosen_pattern_key = "chuong_phan"
    elif count_lama >= 2:
        chosen_pattern_key = "la_ma"
    elif count_so >= 3:
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
        # (strip() đã loại indent, nên kiểm tra prefix đã chuẩn hoá)
        if chosen_pattern_key == "dieu" and not re.match(r'^(?:Điều|Dieu)\s*\d+', chunk, re.IGNORECASE): continue
        if chosen_pattern_key == "chuong_phan" and not re.match(r'^(?:Chương|Phần|Chuong|Phan)\s+[IVX\d]+', chunk, re.IGNORECASE): continue
        if chosen_pattern_key == "la_ma" and not re.match(r'^[IVX]+\.\s', chunk): continue
        if chosen_pattern_key == "so" and not re.match(r'^\d+\.\s', chunk): continue
        
        # LỌC MỤC LỤC: Bỏ qua nếu đoạn text chứa quá nhiều dấu chấm nối tiếp (Ví dụ: ..... 12)
        if len(re.findall(r'\.\.\.\.\.', chunk)) > 2:
            continue
            
        lines = chunk.split('\n', 1)
        header_line = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ""
        
        dieu_so = ""
        tieu_de = ""
        
        # Bóc tách tên Mục / Điều / Phần
        # OCR một số PDF viết không dấu ("Dieu 1.", "Chuong I") -> chấp nhận cả 2 dạng.
        if chosen_pattern_key == "dieu":
            match = re.match(r"((?:Điều|Dieu)\s*\d+)(.*)", header_line, re.IGNORECASE)
            if match:
                dieu_so = match.group(1).strip()
                if dieu_so.lower().startswith("dieu"):
                    dieu_so = "Điều" + dieu_so[4:]
                tieu_de = match.group(2).strip(" .:-") 
        elif chosen_pattern_key == "chuong_phan":
            match = re.match(r"((?:Chương|Phần|Chuong|Phan)\s+[IVX\d]+)(.*)", header_line, re.IGNORECASE)
            if match:
                dieu_so = match.group(1).strip()
                if dieu_so.lower().startswith("chuong"):
                    dieu_so = "Chương" + dieu_so[6:]
                elif dieu_so.lower().startswith("phan"):
                    dieu_so = "Phần" + dieu_so[4:]
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
