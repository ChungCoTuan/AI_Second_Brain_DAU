# Chạy thử DAU Second Brain trên máy local + Cloudflare Tunnel

Mục đích: cho 2–3 người test chức năng trước khi thuê VPS. Không mở PostgreSQL
hay cổng backend ra Internet; mọi truy cập đi qua Cloudflare Tunnel và Cloudflare Access.

## 1. Điều kiện

- Ubuntu 24.04 / WSL2 Ubuntu 24.04
- Python 3.12, Node.js 20+
- RAM khuyến nghị ≥ 12 GB (mô hình cục bộ chạy CPU)
- Tài khoản Cloudflare quản lý domain dùng để test

Cài gói hệ thống (cần mật khẩu sudo):

```bash
sudo apt update
sudo apt install -y python3-venv build-essential poppler-utils \
  postgresql postgresql-contrib postgresql-16-pgvector
```

Không cài Tesseract: OCR đã chuyển sang Gemini API.

## 2. Chuẩn bị Python

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
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

## 3. Database

```bash
sudo -u postgres psql
```

```sql
CREATE ROLE dau_app LOGIN PASSWORD '<mật-khẩu-mạnh>';
CREATE DATABASE dau_second_brain OWNER dau_app;
\c dau_second_brain
CREATE EXTENSION IF NOT EXISTS vector;
\dx
```

Kiểm tra PostgreSQL chỉ nghe localhost:

```bash
sudo ss -ltnp | grep 5432   # phải là 127.0.0.1:5432
```

## 4. Cấu hình

```bash
cp backend/.env.example backend/.env
chmod 600 backend/.env
```

Điền `DATABASE_URL`, `SECRET_KEY` (>= 32 ký tự), `GEMINI_API_KEY`, `OCR_API_KEY`,
`OCR_MODEL`, `HF_HOME`. Tạo secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Kiểm tra model Gemini còn khả dụng

Model cũ (`gemini-2.0-flash`, `gemini-2.5-flash`) đã bị Google đóng với tài khoản mới
và trả HTTP 404. Luôn kiểm tra trước khi đặt `GEMINI_MODEL`/`OCR_MODEL`:

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

Ghi chú: model có trong danh sách vẫn có thể trả `503` khi quá tải; mã OCR sẽ tự retry.
Model đang dùng cho bản test này là `gemini-3.6-flash`.

Tải trước mô hình:

```bash
cd backend
source .venv/bin/activate
export HF_HOME="$PWD/data/models"
python scripts/download_models.py
```

Tạo tài khoản (mật khẩu được hỏi, không truyền qua dòng lệnh). CLI tự tạo bảng
nếu database còn trống, nên chạy được trước lần khởi động app đầu tiên:

```bash
python -m app.scripts.create_admin --email admin@example.com --role admin
```

## 5. Chạy dịch vụ (3 terminal)

Backend (chỉ localhost):

```bash
cd backend && source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend (build cùng origin `/api/v1`):

```bash
cd frontend
npm ci
VITE_API_URL=/api/v1 npm run build
npm run preview -- --host 127.0.0.1 --port 5173
```

Tunnel:

```bash
cloudflared tunnel --config deploy/cloudflared-config.yml run dau-test
```

## 6. Cloudflare Access

Cloudflare Zero Trust → Access → Applications → Add self-hosted:

- Domain: `dau-test.example.com`
- Policy: `Allow` chỉ với email của 2–3 người test
- Bật one-time PIN

Không tạo policy `Bypass`. Không chia sẻ link test ra ngoài danh sách.

## 6b. Chưa có domain: ba cách truy cập miễn phí

### Cách 1 — Cùng mạng WiFi (không cần cài gì)

Frontend chạy ở `0.0.0.0:5173` và Vite proxy `/api` sang backend `127.0.0.1:8000`,
nên backend không mở ra LAN và không cần CORS.

```bash
cd frontend
VITE_API_URL=/api/v1 npm run dev -- --host 0.0.0.0 --port 5173
```

Máy khác trong cùng WiFi mở `http://<IP-LAN-của-bạn>:5173`
(lấy IP bằng `ip -4 addr show scope global`).

Ưu điểm: miễn phí, không cài đặt, phù hợp 2–3 người ngồi cùng phòng.
Nhược điểm: chỉ trong cùng mạng; dev server không có rate limit nên chỉ dùng với
người tin cậy. Nếu bật UFW, chỉ mở cổng 5173 cho dải LAN:

```bash
sudo ufw allow from 192.168.1.0/24 to any port 5173 proto tcp
```

### Cách 2 — Tailscale (khuyến nghị khi người test ở xa)

Tailscale tạo mạng riêng ảo, miễn phí cho nhóm nhỏ, có HTTPS `*.ts.net`,
**không cần domain**. Người test cài Tailscale và được mời vào tailnet;
người ngoài không truy cập được.

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
sudo tailscale serve --bg 5173
tailscale serve status
```

Lấy link `https://<machine>.<tailnet>.ts.net` trong `tailscale serve status` rồi gửi
cho 2–3 người test sau khi họ đã tham gia tailnet.

### Cách 3 — Mua domain rẻ rồi dùng Cloudflare

Domain `.xyz`/`.top` thường vài chục nghìn đồng/năm. Khi đã có domain:

1. Thêm domain vào Cloudflare và đổi nameserver theo hướng dẫn.
2. `cloudflared tunnel create dau-test` rồi `cloudflared tunnel route dns ...`
3. Bật Cloudflare Access chỉ cho email người test (mục 6).

Cách này cho link công khai đẹp và bảo vệ bằng email OTP, nhưng cần mua domain
và chờ DNS.

### Không nên

Không dùng quick tunnel `trycloudflare.com` với key thật: link công khai, không có
Access, ai có link cũng gọi được OCR/chatbot và tiêu quota.

## 7. Kiểm tra sau khi chạy

```bash
psql "$DATABASE_URL" -c "SELECT 1;"
psql "$DATABASE_URL" -c "SELECT extname FROM pg_extension WHERE extname='vector';"
curl -s http://127.0.0.1:8000/
```

- `https://dau-test.example.com/docs` mở được sau khi qua Access.
- Đăng nhập bằng tài khoản CLI, gọi `/api/v1/auth/me`.
- Upload PDF scan tiếng Việt ≤ 20 trang, tick xác nhận không nhạy cảm; kiểm tra dấu tiếng Việt.
- Upload PDF scan khi không tick: phải bị từ chối.
- Chatbot trả lời có citation; câu ngoài phạm vi phải nói không tìm thấy.
- `journalctl`/terminal log không chứa API key hay nội dung tài liệu.

## 8. Vận hành

Xem tiến trình:

```bash
ss -ltnp | grep -E '8000|5173'
ps aux | grep -E 'uvicorn|vite|cloudflared' | grep -v grep
```

Dừng: `Ctrl+C` ở từng terminal (hoặc `kill <PID>`).

Chạy nền tạm thời (không dùng cho production):

```bash
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 > logs/backend.log 2>&1 &
nohup cloudflared tunnel --config deploy/cloudflared-config.yml run dau-test > logs/tunnel.log 2>&1 &
```

Xem log: `tail -f logs/backend.log` hoặc `tail -f logs/tunnel.log`.

Cập nhật code:

```bash
git pull
cd backend && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
# khởi động lại backend, frontend build lại nếu có thay đổi UI
```

Backup dữ liệu:

```bash
pg_dump "$DATABASE_URL" > backup_$(date +%F).sql
tar -czf faiss_$(date +%F).tar.gz backend/data
```

## 9. Đo tải (tùy chọn)

```bash
python -m venv /tmp/kilo/locust-venv
/tmp/kilo/locust-venv/bin/pip install locust
/tmp/kilo/locust-venv/bin/locust -f loadtest/locustfile.py --host http://127.0.0.1:8000
```

Chỉ đo endpoint nhẹ và chatbot với tần suất rất thấp; không đưa OCR vào load test
vì tốn quota/tiền. Kết quả trên máy local chỉ là mốc tham chiếu.
