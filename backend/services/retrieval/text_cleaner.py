"""Vietnamese Text Cleaning & Encoding Normalizer — DAU Second Brain.

Khắc phục lỗi phông chữ, lỗi gõ/lỗi OCR tiếng Việt và loại bỏ rác tiêu đề hành chính.
"""

import re
import unicodedata

# 1. Từ điển sửa lỗi OCR/Mã hóa ký tự PDF bị lỗi dấu & bị đè chữ
OCR_CORRECTIONS = [
    # Lỗi ký tự OCR đặc biệt (chữ hoa/thường)
    (r"\bBỘ GIÁO DỤC VÀ ĐÀO TẠO CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\b", ""),
    (r"\bBO GIAO DUC VA DAO TAO CQNG HOA xA HQI CHU NGHIA VIVT NAM\b", ""),
    (r"\bBO GIAO DUC VA DAO TAO\b", "BỘ GIÁO DỤC VÀ ĐÀO TẠO"),
    (r"\bCQNG HOA xA HQI CHU NGHIA VIVT NAM\b", "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"),
    (r"\bDoc lap - Tu do - Hanh phuc\b", "Độc lập - Tự do - Hạnh phúc"),
    (r"\bquy định Vi Than Thuong Xuyen\b", "Quy chế Đào tạo Thạc sĩ (Thông tư 23/2021/TT-BGDĐT)"),
    (r"\bVi Than Thuong Xuyen\b", "Quy chế Đào tạo Thạc sĩ (Thông tư 23/2021/TT-BGDĐT)"),
    (r"\bViThanThuongXuyen\b", "QuyCheDaoTaoThacSi"),
    
    # Sửa số thay thế chữ cái trong OCR
    (r"\bh9c\b", "học"),
    (r"\bh9p\b", "hợp"),
    (r"\bmgc\b", "mực"),
    (r"\bdirc\b", "đức"),
    (r"\bngued\b", "người"),
    (r"\btri8n\b", "triển"),
    (r"\bmad\b", "mới"),
    (r"\byeti\b", "với"),
    (r"\bV\*\b", "Việt"),
    (r"\bv\*\b", "Việt"),

    # Phục hồi dấu tiếng Việt từ từ điển không dấu OCR
    (r"\bLuan van\b", "Luận văn"),
    (r"\bluan van\b", "luận văn"),
    (r"\bla mot\b", "là một"),
    (r"\bbao cao\b", "báo cáo"),
    (r"\bkhoa hoc\b", "khoa học"),
    (r"\btong hop\b", "tổng hợp"),
    (r"\btong\b", "tổng"),
    (r"\bcac\b", "các"),
    (r"\bket qua\b", "kết quả"),
    (r"\bke't qua\b", "kết quả"),
    (r"\bke't\b", "kết"),
    (r"\bnghien cuu\b", "nghiên cứu"),
    (r"\bnghien cdu\b", "nghiên cứu"),
    (r"\bnghien ciru\b", "nghiên cứu"),
    (r"\bchinhcua\b", "chính của"),
    (r"\bchinh cua\b", "chính của"),
    (r"\bchinh\b", "chính"),
    (r"\bcua\b", "của"),
    (r"\bhoc vien\b", "học viên"),
    (r"\bhọc vien\b", "học viên"),
    (r"\bvien\b", "viên"),
    (r"\bdap Ung\b", "đáp ứng"),
    (r"\bdap ung\b", "đáp ứng"),
    (r"\byeu cau sau\b", "yêu cầu sau"),
    (r"\byeu cau\b", "yêu cầu"),
    (r"\bCo &mg gop\b", "Có đóng góp"),
    (r"\bCo &mg\b", "Có đóng"),
    (r"\b&mg gop\b", "đóng góp"),
    (r"\b&mg\b", "đóng"),
    (r"\bve ly luan\b", "về lý luận"),
    (r"\bly luan\b", "lý luận"),
    (r"\bhoc thuat\b", "học thuật"),
    (r"\bhọc thuat\b", "học thuật"),
    (r"\bthuat\b", "thuật"),
    (r"\bhoac\b", "hoặc"),
    (r"\bphat trien\b", "phát triển"),
    (r"\bphat tri8n\b", "phát triển"),
    (r"\bphat\b", "phát"),
    (r"\bcong nghe\b", "công nghệ"),
    (r"\bdoi moi\b", "đổi mới"),
    (r"\bdoi mad\b", "đổi mới"),
    (r"\bdoi\b", "đổi"),
    (r"\bsang tao\b", "sáng tạo"),
    (r"\bsang\b", "sáng"),
    (r"\btao\b", "tạo"),
    (r"\bthe hien\b", "thể hiện"),
    (r"\bthe hi'n\b", "thể hiện"),
    (r"\b'fang lgc\b", "năng lực"),
    (r"\bfang lgc\b", "năng lực"),
    (r"\bna'ng lg c\b", "năng lực"),
    (r"\bPhu hop\b", "Phù hợp"),
    (r"\bPhu h9p\b", "Phù hợp"),
    (r"\bPhu\b", "Phù"),
    (r"\bphu hop\b", "phù hợp"),
    (r"\bchuan muc\b", "chuẩn mực"),
    (r"\bchuan mgc\b", "chuẩn mực"),
    (r"\bchuan\b", "chuẩn"),
    (r"\bve van hoa\b", "về văn hóa"),
    (r"\bye van Ma\b", "về văn hóa"),
    (r"\bve van Ma\b", "về văn hóa"),
    (r"\bvan Ma\b", "văn hóa"),
    (r"\bdao duc\b", "đạo đức"),
    (r"\bdao dirc\b", "đạo đức"),
    (r"\bdao\b", "đạo"),
    (r"\bva thuan phong my tuc\b", "và thuần phong mỹ tục"),
    (r"\bva\b", "và"),
    (r"\bnguoi Viet Nam\b", "người Việt Nam"),
    (r"\bngued Viet Nam\b", "người Việt Nam"),
    (r"\bViet Nam\b", "Việt Nam"),
    
    # Các thuật ngữ giáo dục đại học không dấu phổ biến
    (r"\bthac si\b", "thạc sĩ"),
    (r"\bthac sl\b", "thạc sĩ"),
    (r"\btien si\b", "tiến sĩ"),
    (r"\bcu nhan\b", "cử nhân"),
    (r"\bky su\b", "kỹ sư"),
    (r"\bki su\b", "kỹ sư"),
    (r"\bkien truc su\b", "kiến trúc sư"),
    (r"\bdao tao\b", "đào tạo"),
    (r"\bhoc phan\b", "học phần"),
    (r"\btin chi\b", "tín chỉ"),
    (r"\bquy che\b", "quy chế"),
    (r"\bquy dinh\b", "quy định"),
    (r"\btruong\b", "trường"),
    (r"\bdai hoc\b", "đại học"),
    (r"\bsinh vien\b", "sinh viên"),
    (r"\bgiang vien\b", "giảng viên"),
    (r"\bcan bo\b", "cán bộ"),
    (r"\bkhuyen khich\b", "khuyến khích"),
    (r"\bnghien cuu khoa hoc\b", "nghiên cứu khoa học"),
    (r"\bphong dao tao\b", "phòng Đào tạo"),
    (r"\bkhao thi\b", "khảo thí"),
    (r"\bxet tuyen\b", "xét tuyển"),
    (r"\btuyen sinh\b", "tuyển sinh"),
    (r"\bnhap hoc\b", "nhập học"),
    (r"\bchuyen nganh\b", "chuyên ngành"),
    (r"\bchuong trinh\b", "chương trình"),
    (r"\bluan van\b", "luận văn"),
    (r"\bluan an\b", "luận án"),
    (r"\bchong bi'a\b", "chống bịa"),
    (r"\btrich dan\b", "trích dẫn"),
    (r"\bphap ly\b", "pháp lý"),
    (r"\bchinh quy\b", "chính quy"),
]

# 2. Tiêu đề biểu ngữ thừa cần lọc bỏ
BOILERPLATE_HEADERS = [
    r"BỘ GIÁO DỤC VÀ ĐÀO TẠO CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
    r"BO GIAO DUC VA DAO TAO CQNG HOA xA HQI CHU NGHIA VIVT NAM",
    r"BỘ GIÁO DỤC VÀ ĐÀO TẠO",
    r"CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
    r"Độc lập - Tự do - Hạnh phúc",
    r"TRƯỜNG ĐẠI HỌC KIẾN TRÚC ĐÀ NẴNG",
]


def clean_vietnamese_text(text: str) -> str:
    """Chuẩn hóa Unicode NFC và tự động phục hồi dấu tiếng Việt cho các từ bị lỗi OCR."""
    if not text:
        return ""

    # 1. Normalize Unicode sang NFC
    cleaned = unicodedata.normalize("NFC", text)

    # 2. Sửa lỗi OCR và phục hồi dấu tiếng Việt theo từ điển
    for pattern, replacement in OCR_CORRECTIONS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # 3. Sửa dính chữ do OCR ngắt dòng sai (vd: "chinhcua" -> "chính của")
    cleaned = re.sub(r"([a-zàáảãạăắằẳẵặâấầẩẫậeéèẻẽẹêếềểễệiíìỉĩịoóòỏõọôốồổỗộơớờởỡợuúùủũụưứừửữựyýỳỷỹỵ])([A-ZĐĐÁÀẢÃẠẮẰẲẴẶẤẦẨẪẬẾỀỂỄỆÍÌỈĨỊỐỒỔỖỘỚỜỞỠỢỨỪỬỮỰÝỲỶỸỴ])", r"\1 \2", cleaned)

    # 4. Loại bỏ ký tự lạ rác điều khiển PDF
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)

    # 5. Chuẩn hóa khoảng trắng dư thừa
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)

    return cleaned.strip()


def remove_boilerplate_headers(text: str) -> str:
    """Loại bỏ tiêu đề biểu ngữ hành chính thừa khỏi câu trả lời RAG."""
    cleaned = text
    for header in BOILERPLATE_HEADERS:
        cleaned = re.sub(header, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^\s*[-–—:\s]+", "", cleaned)
    return clean_vietnamese_text(cleaned)


def clean_title_string(title: str) -> str:
    """Làm sạch tiêu đề văn bản, loại bỏ các đuôi dính biểu ngữ hành chính thừa và chuẩn hóa tên văn bản."""
    if not title:
        return ""
    cleaned = remove_boilerplate_headers(title)
    # Lọc bỏ phần đuôi dính biểu ngữ & rác tiêu đề
    cleaned = re.sub(r":\s*BỘ GIÁO DỤC.*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r":\s*BO GIAO DUC.*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r":\s*CỘNG HÒA XÃ HỘI.*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^Quy định BGD/TT/232021/.*$", "Thông tư 23/2021/TT-BGDĐT (Quy chế Đào tạo Thạc sĩ)", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^QuyDinhViThanThuongXuyen$", "Thông tư 23/2021/TT-BGDĐT (Quy chế Đào tạo Thạc sĩ)", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()
