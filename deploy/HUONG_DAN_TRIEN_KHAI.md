# Hướng dẫn Triển khai DAU Second Brain

> Tài liệu hướng dẫn chi tiết cách **cài đặt môi trường**, **cấu hình**, **khởi chạy**
> và **mở website** DAU Second Brain (chéo từ local cho tới triển khai nhóm test/VPS).
> Áp dụng cho mã nguồn phiên bản hiện tại: OCR qua Gemini API, PostgreSQL + pgvector,
> tạo tài khoản bằng CLI (không dùng mật khẩu mặc định).

---

## 1. Tổng quan kiến trúc triển khai

Hệ thống gồm hai thành phần chạy độc lập:

| Thành phần | Công nghệ | Cổng mặc định | Ghi chú |
|---|---|---|---|
| **Backend** | FastAPI + Uvicorn | `8000` | Chỉ nên nghe `127.0.0.1` |
| **Frontend** | React 19 + Vite | `5173` | Dev server / preview, proxy `/api` → backend |
| **Database** | PostgreSQL 14+ + pgvector | `5432` | Chỉ nghe `localhost` |
| **OCR / Chatbot** | Gemini API | — | Khóa riêng OCR + khóa chatbot |
| **Mô hình cục bộ** | ViT5, mDeBERTa, MiniLM (CPU) | — | Tải về `backend/data/models` |

Frontend proxy `/api` sang `http://127.0.0.1:8000`, nên trình duyệt chỉ nói chuyện
với **một origin duy nhất**: backend và PostgreSQL **không phải mở ra Internet**.
Điều này đúng cho cả chạy local lẫn khi phát ra ngoài qua Tailscale/Cloudflare Tunnel.

---

## 2. Yêu cầu hệ thống

### 2.1. Môi trường local (Windows 10/11, macOS, Linux)

- **Python** `3.10` – `3.12` (khuyến nghị **3.11**, tránh 3.13 vì PyTorch chưa có wheel).
- **Node.js** `18+` (khuyến nghị `20+`).
- **PostgreSQL** `14+` (khuyến nghị `16`).
- **RAM** tối thiểu 8 GB, khuyến nghị ≥ 12–16 GB (mô hình cục bộ chạy trên CPU).

### 2.2. Môi trường server / nhóm test (Ubuntu 24.04 / WSL2)

- Ubuntu 24.04 (hoặc WSL2 Ubuntu 24.04), Python 3.12, Node 20+.
- RAM ≥ 12 GB (khuyến nghị 16 GB, bật swap nếu ít RAM).
- Một **Gemini API key** cho chatbot và một key **riêng** cho OCR.

---

## 3. Cài đặt trên Ubuntu / VPS (khuyến nghị cho triển khai nhóm)

### Bước 1 — Cài gói hệ thống

```bash
sudo apt update
sudo apt install -y python3-venv build-essential poppler-utils \
  postgresql postgresql-contrib postgresql-16-pgvector \
  git curl
```

> Không cần cài Tesseract: ở phiên bản hiện tại OCR đã chuyển sang dùng Gemini API.

### Bước 2 — Chuẩn bị Python và cài thư viện

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel

# Torch bản CPU, không CUDA
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1

pip install -r requirements.txt
pip install -r requirements-dev.txt
pip check
```

Kiểm tra nhanh:

```bash
python -c "import torch, numpy, faiss; print(torch.__version__, numpy.__version__)"
python -m pytest -q
```

### Bước 3 — Tạo Database và extension pgvector

Mở `psql` với quyền superuser:

```bash
sudo -u postgres psql
```

Chạy các câu lệnh sau (thay mật khẩu thật, tối thiểu 10 ký tự):

```sql
CREATE ROLE dau_app LOGIN PASSWORD '<mat-khau-manh>';
CREATE DATABASE dau_second_brain OWNER dau_app;
\c dau_second_brain
CREATE EXTENSION IF NOT EXISTS vector;
\dx
```

Kiểm tra PostgreSQL chỉ nghe trên localhost:

```bash
sudo ss -ltnp | grep 5432   # phải thấy 127.0.0.1:5432
```

### Bước 4 — Cấu hình biến môi trường (`.env`)

```bash
cp backend/.env.example backend/.env
chmod 600 backend/.env
```

Mở `backend/.env` và điền các giá trị bắt buộc:

```env
# Kết nối DB (đúng với role/database vừa tạo)
DATABASE_URL=postgresql://dau_app:MAT_KHAU_MANH@127.0.0.1:5432/dau_second_brain

# Bắt buộc, chuỗi ngẫu nhiên >= 32 ký tự
SECRET_KEY=<sinh-bang-lenh-duoi>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Origin frontend (local dùng localhost:5173)
CORS_ORIGINS=http://localhost:5173

# Chatbot RAG
GEMINI_API_KEY=<key-chatbot>
GEMINI_MODEL=gemini-3.6-flash

# OCR qua Gemini (key RIÊNG, không dùng chung với chatbot)
OCR_API_KEY=<key-ocr>
OCR_MODEL=gemini-3.6-flash
OCR_TIMEOUT_SECONDS=90
OCR_MAX_PAGES=20
OCR_MAX_PDF_MB=20
OCR_MAX_IMAGE_MB=4
OCR_MAX_RETRIES=2

# Cache mô hình cục bộ (đường dẫn tuyệt đối tới backend/data/models)
HF_HOME=/home/USER/AI_Second_Brain_DAU/backend/data/models
```

Sinh `SECRET_KEY` ngẫu nhiên:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Bước 5 — Kiểm tra và tải trước mô hình cục bộ

Kiểm tra model Gemini còn khả dụng với key của bạn (Google đã đóng nhiều model cũ):

```bash
cd backend && .venv/bin/python - <<'PY'
import requests
from app.core.config import settings
r = requests.get("https://generativelanguage.googleapis.com/v1beta/models",
                 headers={"x-goog-api-key": settings.OCR_API_KEY}, timeout=25)
print("HTTP", r.status_code)
for m in r.json().get("models", []):
    if "generateContent" in m.get("supportedGenerationMethods", []):
        print("-", m["name"].replace("models/", ""))
PY
```

Tải trước 4 mô hình cục bộ (summarization, QA, NLI, embedding):

```bash
cd backend
source .venv/bin/activate
export HF_HOME="$PWD/data/models"
python scripts/download_models.py
```

Có thể bỏ qua bước này (mô hình sẽ tự tải ở lần chạy đầu, cần Internet). Tải trước giúp
lần chạy đầu nhanh hơn và kiểm tra sớm lỗi về mạng.

### Bước 6 — Tạo tài khoản quản trị

Mật khẩu được hỏi trên terminal (không hiện trên màn hình, không ghi log, không truyền
qua tham số dòng lệnh):

```bash
cd backend && source .venv/bin/activate
python -m app.scripts.create_admin --email admin@example.com --role admin
```

> Mật khẩu phải ≥ 10 ký tự. Script tự tạo bảng nếu database còn trống, nên có thể chạy
> ngay cả trước lần khởi động app đầu tiên.

---

## 4. Khởi chạy dịch vụ

Cần **2 terminal** (backend và frontend). Backend và frontend đều chỉ nghe localhost.

### Terminal 1 — Backend

```bash
cd backend && source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- API hoạt động tại: `http://127.0.0.1:8000`
- Tài liệu OpenAPI (Swagger UI): `http://127.0.0.1:8000/docs`

### Terminal 2 — Frontend

```bash
cd frontend
npm ci
VITE_API_URL=/api/v1 npm run build
npm run preview -- --host 127.0.0.1 --port 5173
```

Hoặc dùng dev server (tự động reload khi sửa code):

```bash
cd frontend
npm ci
VITE_API_URL=/api/v1 npm run dev -- --host 127.0.0.1 --port 5173
```

### Mở website

Mở trình duyệt truy cập **http://127.0.0.1:5173** rồi đăng nhập bằng email/mật khẩu
đã tạo ở Bước 6.

---

## 5. Cài đặt trên Windows (local)

Nếu chỉ chạy trên máy Windows theo cách thủ công:

1. **Cài PostgreSQL 14+** — tạo database `dau_second_brain` (xem Bước 3, hoặc dùng pgAdmin).
2. **Cài Python 3.11** và **Node 18+**.
3. **Backend:**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1
   pip install -r requirements.txt
   copy .env.example .env
   # Điền DATABASE_URL, SECRET_KEY, GEMINI_API_KEY, OCR_API_KEY...
   python -m app.scripts.create_admin --email admin@example.com --role admin
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
4. **Frontend:**
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
   Mở **http://localhost:5173**.

> Có thể dùng script chẩn đoán tự động `python requirements.py` ở thư mục gốc để kiểm tra
> môi trường (phiên bản, thư viện, DB) trước khi chạy thủ công.

---

## 6. Cho nhóm test truy cập từ xa

### Cách 1 — Cùng mạng WiFi (không cần cài gì)

Chạy frontend trên `0.0.0.0` để các máy cùng mạng truy cập được (backend vẫn nằm trong
`127.0.0.1`, được Vite proxy nên không mở ra LAN):

```bash
cd frontend
VITE_API_URL=/api/v1 npm run dev -- --host 0.0.0.0 --port 5173
```

Máy khác truy cập `http://<IP-LAN-cua-ban>:5173` (xem IP bằng `ip -4 addr show scope global`).

### Cách 2 — Tailscale (khuyến nghị khi test ở xa, không cần domain)

Tham khảo chi tiết tại [`deploy/tailscale-setup.md`](tailscale-setup.md). Tóm tắt:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
sudo tailscale set --operator=$USER
sudo tailscale serve --bg 5173
tailscale serve status
```

- Bật **MagicDNS** và **HTTPS Certificates** trong admin console Tailscale.
- Đảm bảo `frontend/vite.config.ts` có `allowedHosts: ['.ts.net']` (đã được cấu hình sẵn).
- Gửi link `https://<ten-may>.<tailnet>.ts.net` cho người test sau khi họ tham gia tailnet.

### Cách 3 — Cloudflare Tunnel + Access (khi đã có domain)

Tham khảo chi tiết tại [`deploy/README-local-test.md`](README-local-test.md). Tóm tắt:

- Tạo tunnel và cấu hình ingress theo mẫu [`deploy/cloudflared-config.yml`](cloudflared-config.yml)
  (API ở `/api/*`, `/docs`; frontend build ở cổng 5173).
- Trên Cloudflare Zero Trust → Access → tạo policy `Allow` chỉ với email của người test,
  bật one-time PIN.

```bash
cloudflared tunnel --config deploy/cloudflared-config.yml run dau-test
```

> **Không** dùng quick tunnel `trycloudflare.com` với key thật (link công khai, không có Access).

---

## 7. Kiểm tra sau khi triển khai

```bash
# DB kết nối được và có extension vector
psql "$DATABASE_URL" -c "SELECT 1;"
psql "$DATABASE_URL" -c "SELECT extname FROM pg_extension WHERE extname='vector';"

# Backend phản hồi
curl -s http://127.0.0.1:8000/
```

Kiểm tra bằng tay trên trình duyệt:

1. Mở frontend, đăng nhập bằng tài khoản đã tạo, gọi `GET /api/v1/auth/me` trả về thông tin.
2. Upload một PDF tiếng Việt (≤ 20 trang), **tick xác nhận không nhạy cảm**; kiểm tra dấu tiếng Việt hiển thị đúng.
3. Upload PDF mà **không tick** xác nhận: hệ thống phải **từ chối**.
4. Hỏi chatbot: câu trả lời phải có trích dẫn (citation); câu ngoài phạm vi phải trả lời "không tìm thấy".
5. Kiểm tra log (`journalctl` / terminal) **không chứa** API key hay nội dung tài liệu.

---

## 8. Vận hành cơ bản

Xem tiến trình đang chạy:

```bash
ss -ltnp | grep -E '8000|5173'
ps aux | grep -E 'uvicorn|vite|cloudflared' | grep -v grep
```

Dừng dịch vụ: `Ctrl+C` ở từng terminal (hoặc `kill <PID>`).

Chạy nền tạm thời (chỉ để thử, không dùng cho production):

```bash
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 > logs/backend.log 2>&1 &
tail -f logs/backend.log
```

Cập nhật code khi có bản mới:

```bash
git pull
cd backend && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
# Khởi động lại backend; frontend build lại nếu có thay đổi UI
```

Backup dữ liệu:

```bash
pg_dump "$DATABASE_URL" > backup_$(date +%F).sql
tar -czf faiss_$(date +%F).tar.gz backend/data
```

---

## 9. Danh sách lỗi phổ biến và cách xử lý

| # | Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|---|
| 1 | `FATAL: password authentication failed ... database does not exist` | DB chưa tạo / sai mật khẩu | Kiểm tra dịch vụ PostgreSQL đang chạy; tạo lại role + database theo Bước 3 |
| 2 | `psycopg2` báo lỗi kết nối `127.0.0.1:5432` | PostgreSQL không nghe localhost | `sudo ss -ltnp \| grep 5432` |
| 3 | Lỗi `403 Blocked request ... host not allowed` khi mở qua Tailscale | Vite chặn host lạ | Đảm bảo `allowedHosts: ['.ts.net']` trong `vite.config.ts` |
| 4 | Gemini trả `HTTP 404` khi gọi model | Model cũ đã bị Google đóng | Kiểm tra model khả dụng (Bước 5), đặt `GEMINI_MODEL`/`OCR_MODEL` đúng |
| 5 | Treo lâu / lỗi kết nối `huggingface.co` ở lần chạy đầu | Chưa tải weights mô hình cục bộ | Chạy `scripts/download_models.py` khi có Internet ổn định |
| 6 | `WinError 1455 paging file too small` / OOM khi nạp mô hình (Windows) | Thiếu bộ nhớ ảo | Bật paging file ≥ 8–16 GB hoặc giảm RAM mô hình |
| 7 | `pip install` lỗi biên dịch C++ (`cl.exe failed`, wheel build failed) | Python 3.13 / thiếu binary wheel | Dùng Python 3.10–3.11 (64-bit) |
| 8 | Upload PDF > 20 trang / > 20 MB bị từ chối | Giới hạn bảo vệ chi phí OCR | Cấu hình `OCR_MAX_PAGES` / `OCR_MAX_PDF_MB` nếu cần, nhưng cân nhắc chi phí |
| 9 | Chưa có bảng dữ liệu khi mới chạy | App tự `create_all` khi khởi động | Khởi động backend một lần, hoặc chạy `create_admin` để tạo bảng |

---

## 10. Lưu ý bảo mật khi triển khai

- `SECRET_KEY` phải là chuỗi ngẫu nhiên ≥ 32 ký tự, thay giá trị mặc định.
- Không commit `backend/.env` (đã có trong `.gitignore`), không dán API key vào chat/log/README.
- Phân quyền file: `chmod 600 backend/.env`.
- Chỉ mở PostgreSQL và backend trên `127.0.0.1`; truy cập từ xa đi qua Tailscale/Cloudflare Access.
- Không dùng quick tunnel công khai; luôn chặn quyền truy cập bằng danh sách email hoặc tailnet.