import os
import urllib.request
import zipfile
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
os.makedirs(BIN_DIR, exist_ok=True)

def download_file(url, dest):
    print(f"Đang tải {url}...")
    # Add headers to avoid 403 Forbidden
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    print(f"Đã tải xong: {dest}")

# 1. Poppler
poppler_zip = os.path.join(BIN_DIR, "poppler.zip")
if not os.path.exists(os.path.join(BIN_DIR, "poppler")):
    download_file("https://github.com/oschwartz10612/poppler-windows/releases/download/v24.07.0-0/Release-24.07.0-0.zip", poppler_zip)
    print("Đang giải nén Poppler...")
    with zipfile.ZipFile(poppler_zip, 'r') as zip_ref:
        zip_ref.extractall(BIN_DIR)
    os.remove(poppler_zip)
    # Đổi tên thư mục giải nén
    for folder in os.listdir(BIN_DIR):
        if folder.startswith("poppler-"):
            os.rename(os.path.join(BIN_DIR, folder), os.path.join(BIN_DIR, "poppler"))
            break

# 2. Tesseract
tess_dir = os.path.join(BIN_DIR, "Tesseract-OCR")
tess_exe = os.path.join(BIN_DIR, "tesseract-setup.exe")
if not os.path.exists(tess_dir):
    download_file("https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe", tess_exe)
    print("Đang cài đặt Tesseract vào thư mục cục bộ (không cần quyền Admin)...")
    subprocess.run([tess_exe, "/S", f"/D={tess_dir}"], check=True)
    os.remove(tess_exe)

# 3. Gói ngôn ngữ Tiếng Việt
tessdata_dir = os.path.join(tess_dir, "tessdata")
os.makedirs(tessdata_dir, exist_ok=True)
vie_traineddata = os.path.join(tessdata_dir, "vie.traineddata")
if not os.path.exists(vie_traineddata):
    download_file("https://github.com/tesseract-ocr/tessdata/raw/main/vie.traineddata", vie_traineddata)

print(f"Hoàn tất cài đặt OCR tại {BIN_DIR}")
