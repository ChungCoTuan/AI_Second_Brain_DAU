# Triển khai Phương án 3: Spaces + Neon + Pages

> Mục tiêu: Web không sập khi tắt máy cá nhân. Giữ nguyên pipeline AI nặng (ViT5 + mDeBERTa + MiniLM).
> Kiến trúc: `Frontend (Cloudflare Pages) -> Backend (Hugging Face Spaces Docker) -> DB (Neon Postgres) + Gemini API`.

```mermaid
flowchart LR
    U[Nguoi_dung] --> FE[Cloudflare_Pages_React]
    FE -->|"VITE_API_URL"| BE[HF_Spaces_Docker_7860]
    BE --> DB[(Neon_Postgres)]
    BE --> GEM[Gemini_Chat_OCR]
```

Hiện tại bạn chạy tất cả ở local (`scripts/start_all.ps1`: Postgres ở `D:/pg17`, backend `uvicorn :8000`, frontend `vite :5173`) rồi mở Cloudflare Tunnel. Tắt máy = mất origin nên sập. Phương án 3 đưa cả 3 mảnh lên cloud free.

---

## 0. Kiến thức nền cần nắm (5 phút)

| Mảnh | Đang ở đâu | Sẽ đi đâu | Vì sao |
|---|---|---|---|
| Frontend `frontend/` | `vite dev :5173`, proxy `/api -> 127.0.0.1:8000` trong `frontend/vite.config.ts` | Cloudflare Pages (static `dist/`) | React build xong là file tĩnh, host free ổn định |
| Backend `backend/app/main.py` | `FastAPI + lifespan (create_all + APScheduler crawl 2h sáng)` chạy `:8000` | Hugging Face Spaces (Docker, port `7860`) | Spaces free RAM ~16GB, đủ load model nặng. Render free chỉ ~512MB sẽ crash |
| DB `backend/app/db/models.py` + `session.py` | `postgresql://...@127.0.0.1:5432` | Neon Postgres free | Spaces/Render không có Postgres kèm theo |
| AI `backend/app/services/nlp_pipeline.py` | Lazy-load 4 model: `VietAI/vit5-base`, `timpal0l/mdeberta-v3-base-squad2`, `MoritzLaurer/mDeBERTa...xnli`, `paraphrase-MiniLM-L3-v2` | Preload lúc build Docker, cache `HF_HOME` | Tránh tải lúc runtime gây timeout/cold-start quá lâu |
| Vector/file `backend/app/services/vector_db.py` | `backend/data/faiss_index.bin + faiss_meta.json`, PDF trong `backend/data/` | Persistent storage `/data` của Space | Disk tạm của Space mất khi restart nếu không dùng `/data` |
| Chat/OCR | `google-generativeai` gọi ra ngoài | Giữ nguyên, chỉ cần Secrets | Không cần GPU |

File quan trọng cần mở khi làm:
- `backend/app/main.py` — entry, CORS, lifespan
- `backend/app/core/config.py` — `DATABASE_URL`, `CORS_ORIGINS`, `HF_HOME`, `GEMINI_API_KEY`, `OCR_API_KEY`
- `backend/app/db/session.py` — `create_engine(..., pool_pre_ping=True)`
- `backend/app/db/models.py` — dùng `JSONB`, chưa bắt buộc `pgvector` nên lên Neon không sửa model
- `backend/scripts/download_models.py` — danh sách `MODELS` cần preload
- `backend/requirements.txt` — có `torch==2.5.1`, `faiss-cpu`, `pdf2image`
- `frontend/src/api/axiosClient.ts` — đã ưu tiên `VITE_API_URL`
- `frontend/vite.config.ts` — proxy chỉ dùng lúc dev

---

## 1. Checklist đầu việc (tổng quan)

- [ ] 1. Tạo Neon Postgres, lấy `DATABASE_URL`
- [ ] 2. Chuẩn bị `Dockerfile` + `.dockerignore` cho backend
- [ ] 3. Sửa nhỏ backend để chạy cloud (`DATA_DIR`, `PORT`, pool Neon)
- [ ] 4. Tạo Space, push code, nhập Secrets, bật persistent storage
- [ ] 5. Tạo tài khoản admin trỏ vào Neon, test `/docs`
- [ ] 6. Build frontend với `VITE_API_URL`, deploy Cloudflare Pages
- [ ] 7. Nối CORS, kiểm thử end-to-end
- [ ] 8. Vận hành: cold-start, backup, cron, giới hạn free

---

## 2. Đầu việc 1 — Tạo Neon Postgres

1. Vào `neon.tech` tạo project, tạo database `dau_second_brain`.
2. Copy connection string dạng:
   `postgresql://user:pass@ep-xxx.neon.tech:5432/dau_second_brain?sslmode=require`
3. Test local trước (PowerShell tại `backend/`):
   ```powershell
   $env:DATABASE_URL="postgresql://...neon.tech:5432/dau_second_brain?sslmode=require"
   .\.venv\Scripts\Activate.ps1
   python -c "from app.db.session import engine; from app.db.models import Base; Base.metadata.create_all(bind=engine); print('OK')"
   ```
4. Đạt yêu cầu khi: lệnh in `OK`, vào dashboard Neon thấy bảng `users, documents, obligations, thresholds, document_embeddings, chat_sessions...`.

> Không commit URL này. Chỉ để trong `.env` local và Secrets của Space.

---

## 3. Đầu việc 2 — Viết Dockerfile cho Spaces

Tạo file `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/data/models \
    DATA_DIR=/data \
    PORT=7860

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.5.1 \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Preload 4 model trong download_models.py để runtime không phải tải
RUN python scripts/download_models.py

EXPOSE 7860
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
```

Tạo `backend/.dockerignore`:
```
.venv/
data/
__pycache__/
*.pyc
.env
```

Giải thích:
- `python:3.11-slim` khớp README (tránh 3.13 thiếu wheel).
- `poppler-utils` thay cho `backend/bin/poppler` trên Windows, vì `pdf_parser.py` gọi `pdf2image.convert_from_path()`.
- Cài `torch` CPU trước rồi mới `requirements.txt` (đúng ghi chú đầu file requirements).
- `HF_HOME=/data/models` + `DATA_DIR=/data` để dùng persistent storage của Space.

---

## 4. Đầu việc 3 — Sửa nhỏ backend để chạy cloud

Không refactor lớn. Chỉ 3 chỗ:

### 3.1. `backend/app/core/config.py`
Thêm:
```python
DATA_DIR: str = "/data"  # local fallback: backend/data
PORT: int = 7860
```
Logic gợi ý: nếu `os.path.exists("/data")` thì dùng `/data`, ngược lại dùng `backend/data`. Sửa `cors_origins_list` giữ nguyên, chỉ đổi giá trị env sau này.

### 3.2. `backend/app/services/vector_db.py`
Hiện tại:
```python
vector_db = VectorDBManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "..", "data"))
```
Đổi thành đọc env:
```python
data_dir = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data"))
vector_db = VectorDBManager(data_dir=data_dir)
```
Lý do: Space restart xóa disk tạm, chỉ `/data` (persistent) giữ được `faiss_index.bin`.

### 3.3. `backend/app/db/session.py`
Hiện tại chỉ có `pool_pre_ping=True`. Thêm cho Neon:
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"sslmode": "require"} if "neon.tech" in settings.DATABASE_URL else {}
)
```
Không đổi `get_db()` và `models.py`.

---

## 5. Đầu việc 4 — Tạo Hugging Face Space

1. Vào `huggingface.co/spaces` → New Space → chọn `Docker` (không chọn Gradio/Streamlit), CPU basic free.
2. Trong repo Space phải có:
   - Toàn bộ `backend/` ở root Space (hoặc chỉnh `WORKDIR` cho khớp).
   - File `README.md` đầu repo Space có metadata:
     ```yaml
     ---
     title: dau-second-brain-api
     sdk: docker
     app_port: 7860
     ---
     ```
3. Push code lên Space (git push).
4. Vào Settings → Variables and secrets, nhập:
   - `DATABASE_URL` = URL Neon ở mục 2
   - `SECRET_KEY` = chuỗi 48 ký tự (`python -c "import secrets; print(secrets.token_urlsafe(48))"`)
   - `CORS_ORIGINS` = tạm để `http://localhost:5173`, sau có domain Pages thì sửa
   - `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.6-flash`
   - `OCR_API_KEY`, `OCR_MODEL=gemini-3.6-flash`
   - `HF_HOME=/data/models`, `DATA_DIR=/data`
5. Bật Persistent storage, mount `/data`.
6. Xem Logs: phải thấy `Loaded FAISS index` hoặc `Initialized new FAISS index`, `Đã khởi động Cron Job ngầm`.

Lỗi hay gặp:
- Build quá lâu → do tải 4 model. Kệ nó chạy, đừng cancel. Lần sau dùng cache.
- `poppler not found` → thiếu `poppler-utils` trong Dockerfile.
- `password authentication failed` → sai `DATABASE_URL` hoặc thiếu `sslmode=require`.

---

## 6. Đầu việc 5 — Tạo admin + test backend

Chạy từ máy bạn nhưng trỏ vào Neon (không tạo user local):

```powershell
Set-Location backend
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql://...neon.tech...?sslmode=require"
python -m app.scripts.create_admin
```

Mở `https://<username>-<space>.hf.space/docs` kiểm tra:
- `GET /` trả `Welcome to DAU Second Brain API`
- `POST /api/v1/auth/login` đăng nhập được
- `GET /api/v1/system/...` (endpoint trạng thái) trả 200

---

## 7. Đầu việc 6 — Deploy frontend lên Cloudflare Pages

1. Sửa/đặt biến build:
   `VITE_API_URL=https://<username>-<space>.hf.space/api/v1`
2. Build thử local:
   ```powershell
   Set-Location frontend
   $env:VITE_API_URL="https://<username>-<space>.hf.space/api/v1"
   npm ci
   npm run build
   ```
   (`build` = `tsc -b && vite build` trong `frontend/package.json`)
3. Lên `dash.cloudflare.com` → Pages → Upload `frontend/dist/` hoặc connect git (root `frontend/`, build command `npm run build`, output `dist/`).
4. Được domain `https://dau-second-brain.pages.dev`.
5. Quay lại Space, sửa Secret `CORS_ORIGINS=https://dau-second-brain.pages.dev`, restart Space.

Vì `frontend/src/api/axiosClient.ts` dùng `VITE_API_URL || '/api/v1'` nên không cần sửa code, chỉ cần build đúng env.

---

## 8. Đầu việc 7 — Kiểm thử end-to-end

| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| 1 | Mở Pages, login admin | Vào được màn Ưu tiên, không 401 loop |
| 2 | Tải tài liệu → upload PDF có chữ | SSE chạy, vào Cần rà soát, có nghĩa vụ/ngưỡng |
| 3 | Upload PDF scan, tick xác nhận OCR | Gọi Gemini OCR, không báo thiếu `pdftoppm` |
| 4 | Sửa tóm tắt → chạy lại NLI | `contradiction` bị chặn, `entailment` cho qua |
| 5 | Ô search tìm theo tên file/chủ đề | Ra kết quả từ Neon, không phải local |
| 6 | Chat hỏi + citation | Trả lời từ FAISS + Gemini, hết quota thì xoay key `_2,_3` |
| 7 | Tắt máy cá nhân, mở Pages bằng 4G | Vẫn vào được (chứng minh hết phụ thuộc Tunnel) |

---

## 9. Vận hành + giới hạn free (phải biết trước)

- **Cold-start:** Space free sleep khi không ai gọi. Lần mở đầu sau idle chậm 1-2 phút vì load ViT5/mDeBERTa (`_get_sum_model`, `_get_nli_model` trong `nlp_pipeline.py`). Lần 2 nhanh. Khắc phục: dùng UptimeRobot ping `/` mỗi 5 phút.
- **Mất file:** nếu không bật `/data` persistent, PDF + `faiss_index.bin` mất sau restart. Bật rồi thì vẫn nên backup định kỳ.
- **Cron 2h sáng:** `main.py` dùng `APScheduler`. Khi Space sleep sẽ miss giờ. Chấp nhận cho đồ án, hoặc chuyển sang cron ngoài gọi endpoint crawl.
- **Neon free:** giới hạn ~3GB + giờ compute. Đồ án đủ, nhưng đừng để crawl 10 file/ngày quá lâu.
- **Bảo mật:** không commit `backend/.env`, không dán `GEMINI_API_KEY` lên chat. `SECRET_KEY` phải dài ≥32 ký tự. Sai mật khẩu dùng `create_admin`.
- **CORS:** quên đổi `CORS_ORIGINS` sang domain Pages là lỗi phổ biến nhất (frontend trắng/CORS block).

---

## 10. Thứ tự làm trong 1 buổi

1. Sáng: làm mục 2 (Neon) + mục 5 (test `/docs`).
2. Chiều: làm mục 3+4 (Docker + Space + Secrets).
3. Tối: làm mục 6+7 (Pages + test tắt máy).

Khi nào xong mục 7 dòng 7 (tắt máy vẫn vào web) là đạt.
