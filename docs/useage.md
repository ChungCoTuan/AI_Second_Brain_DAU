# USEAGE — Tài liệu deploy Phương án 3 cho Agent (Spaces + Neon + Cloudflare Pages)

> File này dành cho **agent/AI** tự triển khai. Người đọc là agent, không phải GVHD.
> Nguồn tổng hợp: `implement.md` + `docs/usage.md` + `docs/workflow.md` + `docs/Q&A.md` + `docs/repo_gvhd_readme.md` + `docs/DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md` + `docs/CÁC THUẬT TOÁN SỬ DỤNG.md` + `docs/DAU_Second_Brain_Ke_Hoach_Du_Lieu.md` + `docs/DAU_Second_Brain_UIUX_Spec.md` + `docs/DAU_Second_Brain_Dac_Ta_Yeu_Cau_Chuc_Nang.md` + `docs/DAU_Second_Brain_Ke_Hoach_Danh_Gia.md` + code `backend/` + `frontend/`.
> Quy ước: mọi đường dẫn trong file này tính từ root repo `AI_Second_Brain_DAU/`.

---

## 1. Mục tiêu và phạm vi

### 1.1. Mục tiêu duy nhất

Deploy sao cho **tắt máy cá nhân web vẫn online**, free, không thuê VPS. Giữ nguyên pipeline AI nặng.

Kiến trúc đích:

```mermaid
flowchart LR
  User --> FE[Cloudflare_Pages_React]
  FE -->|"VITE_API_URL"| BE[HF_Spaces_Docker_7860]
  BE --> DB[(Neon_Postgres)]
  BE --> GEM[Gemini_Chat_OCR]
```

Kiến trúc hiện tại (local, tắt máy là sập):

```mermaid
flowchart LR
  User --> Tunnel[Cloudflare_Tunnel]
  Tunnel --> PC[May_ca_nhan]
  PC --> FE2[Vite_5173]
  PC --> BE2[Uvicorn_8000]
  PC --> DB2[Postgres_D_pg17]
```

Nguyên nhân sập đã xác minh: Tunnel chỉ forward `localhost:5173/8000` từ máy user (`scripts/start_all.ps1`). Phương án 3 đưa cả 3 mảnh lên cloud free.

### 1.2. Agent được làm / không được làm

Được làm:

- Tạo `backend/Dockerfile`, `backend/.dockerignore`, sửa tối thiểu `backend/app/core/config.py`, `backend/app/services/vector_db.py`, `backend/app/db/session.py` để chạy cloud.
- Build frontend với `VITE_API_URL`, deploy `frontend/dist` lên Cloudflare Pages.
- Tạo Space Docker, nhập Secrets, bật persistent storage `/data`.
- Tạo DB Neon, chạy `Base.metadata.create_all`, tạo admin bằng `python -m app.scripts.create_admin`.
- Kiểm thử end-to-end theo checklist mục 8.

Không được làm:

- Không commit `backend/.env`, không hardcode `GEMINI_API_KEY / OCR_API_KEY / SECRET_KEY / DATABASE_URL` vào code, log, chat.
- Không tuyên bố sai hiện trạng đã ghi trong docs ngày 10/11/2026 (xem mục 9).
- Không đổi logic nghiệp vụ (regex metadata, keyword scoring topic, NLI chỉ cho obligation/threshold, chat top-5 FAISS threshold 0.2, crawl `vanban.chinhphu.vn`) nếu không có yêu cầu riêng.
- Không xóa `backend/data` local khi chưa backup `faiss_index.bin / faiss_meta.json`.

---

## 2. Bản đồ codebase agent phải đọc trước khi deploy

| File | Đọc để làm gì |
|---|---|
| `backend/app/main.py` | Entry FastAPI, `lifespan` tạo bảng + chạy APScheduler (`crawl_chinhphu` 02:00, `check_new_chinhphu` mỗi 30 phút), CORS, prefix `/api/v1`, port local `8000` |
| `backend/app/core/config.py` | `DATABASE_URL`, `CORS_ORIGINS`, `HF_HOME`, `GEMINI_API_KEY(_2,_3)`, `OCR_API_KEY/MODEL/TIMEOUT/MAX_*`, `SECRET_KEY` bắt buộc |
| `backend/app/db/session.py` | `create_engine(pool_pre_ping=True)`, `SessionLocal`, `get_db` |
| `backend/app/db/models.py` | `User, Document, Obligation, Threshold, DocumentEmbedding(JSONB), DocumentRelation, AuditTrail, ChatSession, ChatMessage`. Chưa có `DocumentChunk/Topic/ReviewItem`. Chưa dùng `pgvector` dù `requirements.txt` có `pgvector==0.3.6` |
| `backend/app/services/vector_db.py` | `VectorDBManager(data_dir=.../backend/data)`, lưu `faiss_index.bin + faiss_meta.json`, `IndexFlatIP` dim 384, `search(top_k, threshold)` |
| `backend/app/services/nlp_pipeline.py` | Lazy-load 4 model: `VietAI/vit5-base-vietnews-summarization`, `timpal0l/mdeberta-v3-base-squad2`, `MoritzLaurer/mDeBERTa-v3-base-xnli`, `paraphrase-MiniLM-L3-v2`. `_manage_memory` chỉ giữ 1 model lớn trong RAM. Chat `generate_rag_answer` xoay key khi 429/503/504 |
| `backend/scripts/download_models.py` | Danh sách `MODELS` cần preload lúc build Docker, hỗ trợ `--verify` |
| `backend/requirements.txt` | Pin `torch==2.5.1 CPU`, `transformers==4.47.1`, `faiss-cpu`, `pymupdf`, `pdf2image`, `google-generativeai==0.8.3`, `apscheduler` |
| `backend/app/services/pdf_parser.py` | `extract_text_from_pdf(allow_external_ocr=False)`, PyMuPDF, ngưỡng scan `<20 từ/trang`, giới hạn `OCR_MAX_PAGES/MB`, `chunk_document` adaptive (Điều/Chương/La Mã/số/trang) |
| `backend/app/services/ocr_api.py` | Gọi `generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`, retry 429/5xx, lỗi `OCRConfigurationError/OCRAuthError/OCRTemporaryError/OCRResponseError` |
| `backend/app/services/ingestion/crawl_documents.py` | `BASE_OUTPUT_DIR=data/vanban_caotudong`, `DOMAIN_KEYWORDS`, lọc năm `>=2018`, `crawl_chinhphu(max_files)`, `check_new_chinhphu()`, `sync_status.json` |
| `backend/app/api/routers/documents.py` | `POST /documents/upload` (chỉ `.pdf`, trùng filename từ chối, `BackgroundTasks _run_extraction`), `POST /documents/process_crawled`, `GET /documents/{id}/pdf`, `GET /legal-data` (chỉ `published`), `GET /impact`, `_run_extraction` tạo tối đa 1 Obligation + 1 Threshold/lần ingest, SSE `progress:...`, NLI lại khi sửa |
| `backend/app/api/routers/chat.py` | `POST /chat`: `create_embedding` MiniLM → `vector_db.search(top_k=5, threshold=0.2)` → `generate_rag_answer` → lưu `ChatSession/ChatMessage` + citations |
| `backend/app/api/routers/system.py` | `GET /system/status`, `POST /system/crawl` (tối đa 5 file), `POST /system/ping`, `GET /system/crawled_files`, `GET /system/stream` SSE |
| `backend/app/api/routers/review.py` | `pending/revalidate/publish/reject`, sửa thì chạy lại NLI, `contradiction` bị từ chối |
| `backend/app/api/endpoints.py` | Gộp routers: documents, review, system, analytics, chat, audit, search, auth, reports |
| `backend/app/core/security.py` | JWT `SECRET_KEY` bắt buộc `>=32 ký tự`, `OAuth2PasswordBearer(tokenUrl=/api/v1/auth/login)`, `get_current_user/get_current_admin` |
| `backend/app/core/fixed_account.py` | Tài khoản cố định duy nhất `admin@dau.edu.vn / Dau@Second2026`, `sync_fixed_account(db)` dùng lúc app start |
| `backend/app/scripts/create_admin.py` | Đồng bộ tài khoản cố định duy nhất `admin@dau.edu.vn / Dau@Second2026` (role `admin`), xoá tài khoản khác |
| `frontend/src/api/axiosClient.ts` | `API_BASE_URL = VITE_API_URL || /api/v1`, gắn `Authorization: Bearer`, 401 thì logout về `/login` |
| `frontend/vite.config.ts` | Proxy `/api -> http://127.0.0.1:8000` chỉ dùng dev, `allowedHosts: .ts.net` |
| `frontend/package.json` | `build = tsc -b && vite build`, output `dist/` |
| `frontend/src/App.tsx` | `/login` public, `/` → `/priority`. Admin: priority/dead-docs/deadlines/events/review/topics/admin/audit/rejected. Chung: analytics/search/chat/obligations/thresholds/graph |
| `scripts/start_all.ps1` | Bằng chứng local: `D:/pg17`, `HF_HOME=D:/.../backend/data/models`, `uvicorn :8000`, `vite :5173` |
| `docs/usage.md` | Chuẩn chạy local: copy `.env.example`, `pip install -r requirements.txt`, `create_admin`, `uvicorn`, `npm ci && npm run dev`, `VITE_API_URL` khi khác origin |
| `docs/workflow.md` | Luồng thật: upload → PyMuPDF/OCR → chunk → metadata/topic/summary → obligation/threshold+NLI → relation → FAISS → SSE → `pending_review` → publish/reject |
| `docs/Q&A.md` | Giới hạn bắt buộc: chat không lọc `published`, không NLI câu trả lời; NLI chỉ cho obligation/threshold; extraction rule-based |

---

## 3. Biến môi trường chuẩn (dùng cho cả 3 môi trường)

| Biến | Local | Spaces Secrets | Pages Build | Ghi chú từ code |
|---|---|---|---|---|
| `DATABASE_URL` | `postgresql://...@127.0.0.1:5432/dau_second_brain` | URL Neon có `?sslmode=require` | — | `session.py` + `config.py`. Neon bắt buộc SSL |
| `SECRET_KEY` | random 48 ký tự | random 48 ký tự, nhập tay | — | `security.py` crash nếu rỗng |
| `CORS_ORIGINS` | `http://localhost:5173` | domain Pages `https://*.pages.dev` | — | `main.py` đọc `cors_origins_list` |
| `GEMINI_API_KEY(_2,_3)` | key chat (chỉ dùng khi `LLM_PROVIDER=gemini`) | Secrets Space | — | `nlp_pipeline.py` xoay key khi 429/504/503 |
| `GEMINI_MODEL` | `gemini-3.6-flash` | cùng giá trị, kiểm tra `/v1beta/models` | — | fallback trong code: env → `gemini-3.8-flash` → `gemini-flash-latest` → `gemini-3.5-flash` |
| `LLM_PROVIDER` | `gemini` hoặc `openai` | `openai` | — | `llm_client.py`. `openai` = endpoint tương thích OpenAI (chat + vision) |
| `LLM_BASE_URL` | rỗng nếu dùng Gemini | ví dụ `https://xai247.xyz/v1` | — | `llm_client.py` gọi `{base}/chat/completions` |
| `LLM_API_KEY` | rỗng nếu dùng Gemini | key của gateway | — | `llm_client.py` ưu tiên key này cho chat |
| `LLM_MODEL` | rỗng nếu dùng Gemini | ví dụ `claude-fable-5` | — | model vision dùng cho cả OCR |
| `OCR_API_KEY` | key riêng, không chung chat | Secrets Space | — | `ocr_api.py` tách riêng |
| `OCR_MODEL` | `gemini-3.6-flash` | model có vision | — | lỗi 400/404 = sai model. Với `LLM_PROVIDER=openai` dùng model có vision của gateway |
| `OCR_TIMEOUT_SECONDS/MAX_PAGES/MAX_PDF_MB/MAX_IMAGE_MB/MAX_RETRIES` | mặc định `.env.example` | giữ nguyên | — | `pdf_parser.py` enforce |
| `HF_HOME` | `E:/.../backend/data/models` hoặc `backend/data/models` | `/data/models` | — | `config.py` set `os.environ.setdefault` |
| `DATA_DIR` (mới thêm) | `backend/data` | `/data` | — | `vector_db.py` sẽ đọc env này |
| `PORT` (mới thêm) | `8000` | `7860` | — | Spaces yêu cầu `7860` |
| `VITE_API_URL` | không đặt (dùng `/api/v1`) | — | `https://<space>.hf.space/api/v1` | `axiosClient.ts` |

Tạo `SECRET_KEY`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## 4. Phase 0 — Chuẩn bị tài khoản và kiểm tra local

Đầu vào: repo sạch, `backend/.env` đã có, `frontend/` cài được.

1. Kiểm tra Python 3.11 64-bit, Node 20+, Postgres local chạy, `pdftoppm` dùng được nếu test OCR.
2. Chạy local theo `docs/usage.md`:
```powershell
Copy-Item backend\.env.example backend\.env
Set-Location backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1
python -m pip install -r requirements.txt
python scripts/download_models.py
python -m app.scripts.create_admin
uvicorn app.main:app --reload --port 8000
```
3. Terminal mới:
```powershell
Set-Location frontend
npm ci
npm run dev
```
4. Kiểm tra: Swagger `http://127.0.0.1:8000/docs` mở được, login vào `/priority`, upload 1 PDF có chữ thấy SSE chạy và có mục `pending_review`.

Điều kiện qua phase: `GET /` trả welcome, `POST /api/v1/auth/login` 200, `GET /api/v1/search` 200.

---

## 5. Phase 1 — Tạo Neon Postgres

Mục đích: thay `127.0.0.1:5432` trong `config.py` bằng DB cloud.

1. Tạo project Neon, database `dau_second_brain`.
2. Copy pooled connection string, bảo đảm có `?sslmode=require`.
3. Test từ máy agent (PowerShell, tại `backend/`):
```powershell
$env:DATABASE_URL="postgresql://USER:PASS@ep-xxx.neon.tech:5432/dau_second_brain?sslmode=require"
.\.venv\Scripts\Activate.ps1
python -c "from app.db.session import engine; from app.db.models import Base; Base.metadata.create_all(bind=engine); print('NEON_OK')"
```
4. Vào dashboard Neon kiểm tra bảng: `users, documents, obligations, thresholds, document_embeddings, document_relations, audit_trails, chat_sessions, chat_messages`.

Xử lý lỗi:

- `password authentication failed` → sai user/pass, copy lại full URL, không thừa khoảng trắng.
- `SSL required` → thiếu `sslmode=require`.
- Timeout → kiểm tra firewall, thử lại, Neon free đôi khi cold-start.

---

## 6. Phase 2 — Thêm Dockerfile cho Spaces

Tạo `backend/Dockerfile`:

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
logs/
```

Lý do từng dòng (agent phải hiểu):

- `python:3.11-slim` khớp `docs/usage.md` và README (3.13 thiếu wheel `tokenizers/sentencepiece`).
- `poppler-utils` thay `backend/bin/poppler/Library/bin` Windows vì `pdf_parser.py:_extract_text_via_ocr` gọi `pdf2image.convert_from_path`.
- Cài `torch` CPU trước rồi mới `requirements.txt` theo đúng comment đầu `requirements.txt`.
- `RUN python scripts/download_models.py` preload 4 repo trong `MODELS`, tránh tải runtime. Nếu build OOM thì tách preload MiniLM trước, 3 model lớn sau.
- `CMD` dùng `${PORT:-7860}` để Spaces inject port.

---

## 7. Phase 3 — Sửa tối thiểu backend để chạy cloud

Chỉ sửa 3 file. Không sửa logic regex/NLI/chat/crawl.

### 7.1. `backend/app/core/config.py`

Thêm sau `HF_HOME`:

```python
DATA_DIR: str = "/data"
PORT: int = 7860
```

Giữ nguyên `cors_origins_list`, `SECRET_KEY`, `DATABASE_URL`. Logic `HF_HOME` hiện tại (`os.environ.setdefault`) giữ nguyên để Secrets Space override được.

Quy ước runtime:

- Nếu `os.path.exists("/data")` thì dùng `/data`, ngược lại fallback `backend/data` local.
- Implement fallback ở nơi dùng, không đổi default thành đường dẫn Windows.

### 7.2. `backend/app/services/vector_db.py`

Thay dòng singleton cuối file:

```python
# cũ
vector_db = VectorDBManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "..", "data"))
# mới
data_dir = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data"))
vector_db = VectorDBManager(data_dir=data_dir)
```

Lý do: `docs/DAU_Second_Brain_Ke_Hoach_Du_Lieu.md` ghi FAISS nằm ở `backend/data`. Disk Space (trừ `/data` persistent) bị xóa khi restart. Không chuyển sang `pgvector` ở phase này dù `requirements.txt` đã có `pgvector==0.3.6`, vì `models.py` đang dùng `JSONB`.

### 7.3. `backend/app/db/session.py`

Thay `engine`:

```python
connect_args = {"sslmode": "require"} if "neon.tech" in settings.DATABASE_URL else {}
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args,
)
```

Giữ nguyên `SessionLocal` và `get_db`. Không thêm migration framework vì `main.py` đang `create_all`.

Kiểm tra sau sửa:

```powershell
python -m py_compile app/core/config.py app/services/vector_db.py app/db/session.py
python -m pytest tests -q
```

Test hiện có theo `docs/DAU_Second_Brain_Ke_Hoach_Danh_Gia.md`: `test_ocr_api.py`, `test_pdf_parser_limits.py`. Chưa có benchmark F1/ROUGE, agent không được bịa số.

---

## 8. Phase 4 — Tạo và deploy Hugging Face Space

1. Tạo Space mới: chọn `Docker`, CPU basic free, `app_port: 7860`.
2. Cấu trúc repo Space: đặt toàn bộ nội dung `backend/` ở root Space (gồm `app/`, `requirements.txt`, `Dockerfile`, `scripts/download_models.py`).
3. File `README.md` ở root Space phải có front-matter:
```yaml
---
title: dau-second-brain-api
sdk: docker
app_port: 7860
---
```
4. Push code, xem Build logs đến khi xong `RUN python scripts/download_models.py`.
5. Settings → Variables and secrets, nhập đúng tên:
   - `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `GEMINI_API_KEY`, `GEMINI_API_KEY_2`, `GEMINI_API_KEY_3`, `GEMINI_MODEL`, `OCR_API_KEY`, `OCR_MODEL`, `HF_HOME=/data/models`, `DATA_DIR=/data`, `PORT=7860`
   - `CORS_ORIGINS` tạm để `http://localhost:5173`, sau có domain Pages mới đổi.
6. Bật Persistent storage, mount `/data`.
7. Xem Runtime logs phải có:
   - `Initialized new FAISS index.` hoặc `Loaded FAISS index with ...`
   - `Đã khởi động Cron Job ngầm (APScheduler)`
8. Mở `https://<user>-<space>.hf.space/docs`, gọi `GET /` phải trả `{"message": "Welcome to DAU Second Brain API"}`.

Lỗi build/runtime và cách xử lý:

| Log | Nguyên nhân từ code | Xử lý |
|---|---|---|
| `poppler ... not found / PDFInfoNotInstalled` | thiếu `poppler-utils`, `pdf_parser.py` gọi `convert_from_path` | kiểm tra Dockerfile có `poppler-utils` |
| `SECRET_KEY chưa được cấu hình` | `security.py` raise khi rỗng | nhập `SECRET_KEY` Secrets, restart |
| `password authentication / SSL` | sai Neon URL | copy lại URL có `sslmode=require` |
| Build timeout ở `download_models.py` | 4 model vài GB | để chạy tiếp, không cancel; lần sau cache |
| `WinError 1455 / OOM / allocate` | load ViT5+mDeBERTa cùng lúc, `nlp_pipeline.py` đã có `_manage_memory` | Space free vẫn chịu được, Render free thì không; không load đồng thời khi verify |
| `404 OCR_MODEL / 401 OCR` | sai `OCR_MODEL` hoặc key | kiểm tra `/v1beta/models`, tách key OCR riêng khỏi chat |

---

## 9. Phase 5 — Tạo admin và kiểm tra backend trên cloud

Chạy từ máy agent nhưng trỏ vào Neon, không tạo user local:

```powershell
Set-Location backend
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql://USER:PASS@ep-xxx.neon.tech:5432/dau_second_brain?sslmode=require"
python -m app.scripts.create_admin
```

Sau đó test trên `*.hf.space`:

- `POST /api/v1/auth/login` với email trên → nhận `access_token`.
- `GET /api/v1/auth/me` với header `Authorization: Bearer <token>` → 200.
- `GET /api/v1/system/status` → `{"has_new_docs":..., "unprocessed_crawled_count":...}`.
- `GET /api/v1/search?query=...` → 200 (lọc SQL theo filename/chủ đề/tags, không phải semantic theo `workflow.md`).
- `GET /api/v1/legal-data` → ban đầu rỗng vì chưa có `published`.

---

## 10. Phase 6 — Deploy frontend lên Cloudflare Pages

1. Build local thử với env trỏ Space:
```powershell
Set-Location frontend
$env:VITE_API_URL="https://<user>-<space>.hf.space/api/v1"
npm ci
npm run build
```
2. Lên Cloudflare Pages: connect git hoặc upload `frontend/dist`. Cấu hình:
   - Root: `frontend/`
   - Build: `npm run build`
   - Output: `dist/`
   - Env: `VITE_API_URL=https://<user>-<space>.hf.space/api/v1`
3. Được domain `https://<project>.pages.dev`.
4. Quay lại Space, sửa `CORS_ORIGINS=https://<project>.pages.dev`, restart Space.
5. Mở Pages, login admin. Nếu trắng trang hoặc CORS block → 99% sai `CORS_ORIGINS` hoặc sai `VITE_API_URL` lúc build. Build lại sau khi sửa env.

Không sửa `vite.config.ts` proxy và `axiosClient.ts` baseURL ở phase này vì đã đúng (`axiosClient.ts` ưu tiên `VITE_API_URL`, proxy chỉ dùng dev).

---

## 11. Phase 7 — Kiểm thử end-to-end (bắt buộc)

Thực hiện đúng thứ tự, ghi pass/fail:

| # | Thao tác (role) | Endpoint/UI | Pass khi |
|---|---|---|---|
| 1 | Login admin trên Pages | `POST /api/v1/auth/login`, `/priority` | vào Ưu tiên, không loop 401 (`axiosClient.ts` chỉ logout khi 401) |
| 2 | Upload PDF có chữ | `POST /api/v1/documents/upload`, SSE `/api/v1/system/stream` | trả `đã đưa vào hàng đợi`, SSE `progress:<file>:...`, có `pending_review` ở `/review` |
| 3 | Upload PDF scan + tick OCR | cùng endpoint với `allow_external_ocr=true` | không báo `thiếu pdftoppm`, OCR chạy qua Gemini, tuân thủ `OCR_MAX_PAGES/MB` |
| 4 | Review sửa tóm tắt | `POST /api/v1/review/revalidate`, `PUT /review/.../publish` | `contradiction` bị từ chối, `entailment` cho qua, có `audit_trails` |
| 5 | Search | `GET /api/v1/search` + `/search` | lọc đúng filename/chủ đề/tags, phân trang `page/limit` |
| 6 | Chat RAG | `POST /api/v1/chat` + `/chat` | top-5 FAISS threshold 0.2, citations có `vb/dieu/nguon`, hết quota xoay `_2,_3`, lưu `chat_sessions/messages` |
| 7 | Legal/graph/audit/report | `GET /legal-data`, `/impact`, `/auditing/warnings`, `/reports/template/{id}`, các trang `/obligations /thresholds /graph /topics /admin /audit` | `legal-data` chỉ `published`, graph từ `DocumentRelation` regex, DOCX tải được |
| 8 | Crawl thủ công | `POST /api/v1/system/crawl`, `GET /system/crawled_files` | tối đa 5 file/lần, file vào `vanban_caotudong`, xử lý tiếp bằng `process_crawled` |
| 9 | Tắt máy cá nhân, mở Pages bằng 4G | Pages + Space + Neon | vẫn login/upload/search/chat được — đây là tiêu chí đạt Phương án 3 |

Nếu fail ở 9 mà pass ở local → chưa thoát Tunnel, kiểm tra lại `VITE_API_URL` có trỏ Space hay vẫn `localhost:8000`.

---

## 12. Vận hành, giới hạn free và sự thật agent phải giữ

- Cold-start: Space free sleep khi idle. Lần mở đầu chậm 1-2 phút vì `_get_sum_model/_get_nli_model` load ViT5/mDeBERTa. Dùng UptimeRobot ping `GET /` mỗi 5 phút để đỡ sleep.
- Mất file: chỉ `/data` persistent giữ `faiss_index.bin/meta.json` và PDF. Không bật là mất sau restart. Backup định kỳ.
- Cron: `main.py` chạy `APScheduler` trong cùng process API. Khi Space sleep sẽ miss `crawl 02:00` và `ping 30 phút`. Chấp nhận cho đồ án (`workflow.md` mục 6 đã cảnh báo trùng lịch khi nhiều worker).
- Neon free: giới hạn dung lượng/giờ compute. Đừng crawl 10 file/ngày liên tục.
- OCR là gửi ảnh ra ngoài (`ocr_api.py` + `pdf_parser.py`), cần consent UI. Không bật với tài liệu mật (`Q&A.md`).
- Sự thật không được nói sai khi demo:
  - Search là SQL, không phải semantic.
  - Chat không lọc `published`, không NLI câu trả lời.
  - NLI chỉ cho summary obligation/threshold và khi sửa.
  - Extraction 1 obligation + 1 threshold/lần ingest, rule-based + regex, topic keyword scoring cần `>=3 điểm` else `Khác`.
  - Không có benchmark F1/ROUGE/BERTScore trong repo. Muốn đo phải làm dataset nhãn vàng theo `docs/DAU_Second_Brain_Ke_Hoach_Danh_Gia.md`.
  - Frontend route admin/lecturer trong `App.tsx` không thay thế check backend `get_current_admin`.

---

## 13. Checklist bàn giao

- [ ] URL Space `*.hf.space/docs` mở được, `GET /` 200
- [ ] URL Pages mở được, login admin thành công
- [ ] Neon có đủ bảng, có ít nhất 1 `User admin`
- [ ] Upload PDF chữ + scan OK, SSE chạy, review publish OK
- [ ] Search/chat/legal-data/impact/audit/report OK
- [ ] Tắt máy cá nhân vẫn truy cập Pages được
- [ ] Không có secret nào trong git, `backend/.env` đã ignore
- [ ] Ghi lại 3 URL + phiên bản model + commit đã deploy để tái lập đánh giá

Khi xong mục “tắt máy vẫn vào web” là đạt.
