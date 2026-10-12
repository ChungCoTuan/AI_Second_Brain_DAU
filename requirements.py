#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
DAU SECOND BRAIN - BỘ CÔNG CỤ CHẨN ĐOÁN & CÀI ĐẶT MÔI TRƯỜNG (ENVIRONMENT DOCTOR)
================================================================================
Script tự động kiểm tra, cài đặt thư viện và chẩn đoán toàn bộ các thành phần 
cần thiết để khởi chạy dự án trên bất kỳ máy tính nào.

Sử dụng:
    python requirements.py
    (hoặc trong virtualenv: .\\venv\\Scripts\\python requirements.py)
================================================================================
"""

import sys
import os
import subprocess
import platform
import shutil

# Thiết lập encoding UTF-8 cho console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ANSI Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(title):
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}")

def print_ok(msg):
    print(f"  {GREEN}[✓] ĐẠT:{RESET} {msg}")

def print_warn(msg):
    print(f"  {YELLOW}[!] CẢNH BÁO:{RESET} {msg}")

def print_err(msg):
    print(f"  {RED}[✗] LỖI:{RESET} {msg}")

def print_info(msg):
    print(f"  {BLUE}[i] THÔNG TIN:{RESET} {msg}")

def check_python_version():
    print_header("1. KIỂM TRA PHIÊN BẢN PYTHON")
    ver = sys.version_info
    ver_str = f"{ver.major}.{ver.minor}.{ver.micro}"
    print_info(f"Phiên bản Python hiện tại: {ver_str} ({platform.architecture()[0]})")
    
    if ver.major != 3:
        print_err("Dự án yêu cầu Python 3.x!")
        return False
        
    if ver.minor < 10:
        print_err(f"Python {ver_str} quá cũ! Dự án yêu cầu Python 3.10 trở lên.")
        return False
    elif ver.minor >= 13:
        print_warn(f"Bạn đang dùng Python {ver_str}. Một số thư viện học sâu (PyTorch, Tokenizers) "
                   f"chưa có bản build C wheels ổn định trên Python 3.13+.\n"
                   f"      Khuyến nghị sử dụng Python 3.10 hoặc 3.11 nếu gặp lỗi cài đặt.")
        return True
    else:
        print_ok(f"Phiên bản Python {ver_str} hoàn toàn tương thích (3.10 - 3.12).")
        return True

def install_python_requirements():
    print_header("2. CÀI ĐẶT THƯ VIỆN PYTHON (PIP DEPENDENCIES)")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    req_path = os.path.join(base_dir, "requirements.txt")
    if not os.path.exists(req_path):
        req_path = os.path.join(base_dir, "backend", "requirements.txt")
        
    if not os.path.exists(req_path):
        print_err(f"Không tìm thấy file requirements.txt!")
        return False
        
    print_info(f"Đang kiểm tra và cài đặt từ: {req_path}")
    try:
        cmd = [sys.executable, "-m", "pip", "install", "-r", req_path]
        ret = subprocess.run(cmd, check=True)
        if ret.returncode == 0:
            print_ok("Cài đặt toàn bộ thư viện Python thành công.")
            return True
    except subprocess.CalledProcessError as e:
        print_err(f"Quá trình cài đặt pip gặp lỗi: {e}")
        return False

def check_tesseract_ocr():
    print_header("3. KIỂM TRA TESSERACT OCR (CÔNG CỤ QUANG HỌC ĐỌC PDF SCAN)")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Quét tesseract trong PATH hoặc thư mục cố định
    tess_local = os.path.join(base_dir, "backend", "bin", "Tesseract-OCR", "tesseract.exe")
    tess_global = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    tess_in_path = shutil.which("tesseract")
    
    found_tess = None
    if tess_in_path:
        found_tess = tess_in_path
    elif os.path.exists(tess_local):
        found_tess = tess_local
    elif os.path.exists(tess_global):
        found_tess = tess_global
        
    if found_tess:
        print_ok(f"Tìm thấy Tesseract OCR: {found_tess}")
    else:
        print_err("Không tìm thấy Tesseract OCR binary trên máy!")
        print_info("Hướng dẫn khắc phục:")
        print("      - Tải bộ cài Tesseract Windows tại: https://github.com/UB-Mannheim/tesseract/wiki")
        print("      - Cài đặt vào đường dẫn mặc định: C:\\Program Files\\Tesseract-OCR\\")
        print("      - Hoặc copy thư mục cài đặt vào: backend/bin/Tesseract-OCR/")

    # 2. Quét gói tiếng Việt vie.traineddata
    tessdata_local = os.path.join(base_dir, "backend", "bin", "tessdata", "vie.traineddata")
    tessdata_global = r"C:\Program Files\Tesseract-OCR\tessdata\vie.traineddata"
    
    if os.path.exists(tessdata_local):
        print_ok(f"Tìm thấy dữ liệu tiếng Việt OCR: {tessdata_local}")
    elif os.path.exists(tessdata_global):
        print_ok(f"Tìm thấy dữ liệu tiếng Việt OCR: {tessdata_global}")
    else:
        print_warn("Chưa có file vie.traineddata (cần thiết để OCR tiếng Việt chính xác)!")
        print_info("Hướng dẫn: Tải file 'vie.traineddata' từ https://github.com/tesseract-ocr/tessdata")
        print("      và đặt vào thư mục 'backend/bin/tessdata/vie.traineddata'.")

def check_poppler():
    print_header("4. KIỂM TRA POPPLER (BỘ RENDER TRANG PDF THÀNH ẢNH)")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    poppler_local = os.path.join(base_dir, "backend", "bin", "poppler", "Library", "bin", "pdftoppm.exe")
    poppler_in_path = shutil.which("pdftoppm")
    
    if poppler_in_path:
        print_ok(f"Tìm thấy Poppler trong PATH: {poppler_in_path}")
    elif os.path.exists(poppler_local):
        print_ok(f"Tìm thấy Poppler cục bộ: {poppler_local}")
    else:
        print_warn("Không tìm thấy Poppler binary (pdftoppm)!")
        print_info("Nếu không có Poppler, tính năng OCR PDF scan (pdf2image) sẽ không hoạt động.")
        print_info("Hướng dẫn khắc phục:")
        print("      - Windows: Chạy lệnh 'winget install -e --id oschwartz10612.poppler'")
        print("      - Hoặc tải ZIP từ: https://github.com/oschwartz10612/poppler-windows/releases")
        print("      - Giải nén vào thư mục: backend/bin/poppler/")

def check_virtual_memory():
    print_header("5. KIỂM TRA BỘ NHỚ RAM & BỘ NHỚ ẢO (PAGING FILE / VIRTUAL MEMORY)")
    try:
        import psutil
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        ram_gb = mem.total / (1024**3)
        swap_gb = swap.total / (1024**3)
        total_virtual_gb = (mem.total + swap.total) / (1024**3)
        
        print_info(f"RAM vật lý: {ram_gb:.1f} GB")
        print_info(f"Bộ nhớ ảo (Paging File / Swap): {swap_gb:.1f} GB")
        print_info(f"Tổng dung lượng bộ nhớ khả dụng: {total_virtual_gb:.1f} GB")
        
        if total_virtual_gb < 12.0:
            print_warn("Tổng bộ nhớ (RAM + Paging File) nhỏ hơn 12GB!")
            print_warn("Nguy cơ gặp lỗi [WinError 1455] 'The paging file is too small' khi tải các mô hình ViT5 / XLM-RoBERTa.")
            print_info("Hướng dẫn khắc phục trên Windows:")
            print("      1. Nhấn phím Windows, tìm 'Advanced system settings' (Xem cài đặt hệ thống nâng cao)")
            print("      2. Trong tab 'Advanced', mục 'Performance' bấm 'Settings...'")
            print("      3. Chọn tab 'Advanced' -> mục 'Virtual memory' bấm 'Change...'")
            print("      4. Tích chọn 'Custom size': Đặt Initial: 8192 MB, Maximum: 16384 MB -> Bấm 'Set' -> OK và Khởi động lại máy.")
        else:
            print_ok("Dung lượng bộ nhớ đáp ứng tốt yêu cầu chạy mô hình AI cục bộ.")
    except Exception as e:
        print_info(f"Không thể kiểm tra bộ nhớ chi tiết (cần psutil): {e}")

def check_env_and_database():
    print_header("6. KIỂM TRA CẤU HÌNH BIẾN MÔI TRƯỜNG (.ENV) & CƠ SỞ DỮ LIỆU POSTGRESQL")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, "backend", ".env")
    
    if not os.path.exists(env_path):
        print_warn(f"Chưa có file backend/.env!")
        # Tạo file .env mẫu
        default_env = """# Database PostgreSQL
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/dau_second_brain"

# Secret Key cho JWT Authentication
SECRET_KEY="dau-second-brain-super-secret-key-for-jwt-token"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Gemini API Key (DUY NHẤT dành riêng cho Tab Tra cứu AI / Chatbot RAG)
GEMINI_API_KEY=""
GEMINI_API_KEY_2=""
GEMINI_API_KEY_3=""
"""
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(default_env)
        print_ok(f"Đã tự động tạo file mẫu tại: {env_path}")
        print_info("Vui lòng mở file backend/.env để kiểm tra mật khẩu PostgreSQL và GEMINI_API_KEY.")
    else:
        print_ok(f"Đã tìm thấy file cấu hình: {env_path}")
        
    # Thử kết nối CSDL
    try:
        db_url = None
        # Ưu tiên load bằng python-dotenv nếu có
        try:
            from dotenv import load_dotenv  # type: ignore
            load_dotenv(env_path)
            db_url = os.getenv("DATABASE_URL")
        except ImportError:
            # Fallback đọc thủ công file .env bằng Python thuần
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            os.environ[key] = val
                db_url = os.getenv("DATABASE_URL")

        if db_url:
            try:
                import psycopg2
                # Parse connection URL cơ bản
                from urllib.parse import urlparse
                p = urlparse(db_url)
                conn = psycopg2.connect(
                    dbname=p.path.lstrip('/'),
                    user=p.username,
                    password=p.password,
                    host=p.hostname or 'localhost',
                    port=p.port or 5432,
                    connect_timeout=3
                )
                conn.close()
                print_ok("Kết nối thành công đến PostgreSQL Database!")
            except ImportError:
                print_warn("Chưa cài đặt thư viện 'psycopg2-binary' để test kết nối PostgreSQL trực tiếp.")
            except Exception as conn_err:
                print_err(f"Chưa kết nối được đến cơ sở dữ liệu PostgreSQL: {conn_err}")
                print_info("Hướng dẫn khắc phục:")
                print("      1. Đảm bảo dịch vụ PostgreSQL đang chạy (Service: postgresql-x64-xx).")
                print("      2. Mở pgAdmin hoặc psql, tạo Database mới tên: 'dau_second_brain'.")
                print("      3. Cập nhật chuỗi DATABASE_URL trong backend/.env đúng user/password của bạn.")
    except Exception as e:
        print_warn(f"Không thể đọc thông tin cấu hình cơ sở dữ liệu: {e}")

def print_summary():
    print_header("TỔNG KẾT & CÂU LỆNH KHỞI CHẠY HỆ THỐNG")
    print(f"""
{BOLD}Để khởi động hệ thống sau khi kiểm tra xong, bạn mở 2 cửa sổ Terminal:{RESET}

{BOLD}1. Terminal 1 - Backend (FastAPI):{RESET}
   cd backend
   .\\venv\\Scripts\\activate
   uvicorn app.main:app --reload --port 8000

{BOLD}2. Terminal 2 - Frontend (React / Vite):{RESET}
   cd frontend
   npm install
   npm run dev

{BOLD}Truy cập Web:{RESET}
   - Giao diện người dùng: {CYAN}http://localhost:5173{RESET}
   - Tài liệu API (Swagger UI): {CYAN}http://localhost:8000/docs{RESET}
   - Tài khoản đăng nhập: {GREEN}admin@dau.edu.vn / admin123{RESET}
""")

def main():
    print(f"{BOLD}{GREEN}")
    print("=" * 70)
    print("       DAU SECOND BRAIN - BỘ CÔNG CỤ CHẨN ĐOÁN MÔI TRƯỜNG DỰ ÁN")
    print("=" * 70)
    print(f"{RESET}")
    
    check_python_version()
    install_python_requirements()
    check_tesseract_ocr()
    check_poppler()
    check_virtual_memory()
    check_env_and_database()
    print_summary()

if __name__ == "__main__":
    main()
