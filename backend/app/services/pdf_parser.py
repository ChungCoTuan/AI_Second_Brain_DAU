import fitz  # PyMuPDF
import os
import re
from typing import List, Dict

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Đọc file PDF và trích xuất toàn bộ văn bản thô.
    Sử dụng PyMuPDF (fitz) để giải quyết lỗi font (cid:xxx) của các file scan hoặc subset fonts.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Không tìm thấy file PDF tại: {pdf_path}")
        
    extracted_text = []
    
    try:
        # Mở file PDF bằng PyMuPDF
        with fitz.open(pdf_path) as pdf:
            for i in range(len(pdf)):
                page = pdf[i]
                text = page.get_text("text")
                if text.strip():
                    extracted_text.append(f"--- TRANG {i+1} ---\n{text.strip()}")
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
                
    full_text = "\n\n".join(extracted_text)
    return full_text

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
