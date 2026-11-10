# DAU Second Brain

Hệ thống web giúp Trường Đại học Kiến trúc Đà Nẵng **nạp, bóc tách, rà soát và tra cứu văn bản PDF tiếng Việt** (quy chế, thông tư, quyết định). Đồ án môn Trí tuệ nhân tạo.

Người dùng đăng nhập, admin đưa PDF vào kho, máy đọc và trích thông tin, admin duyệt từng mục trước khi đưa lên các màn tra cứu. Giảng viên tìm văn bản hoặc hỏi chatbot kèm đoạn nguồn.

> Kết quả AI là hỗ trợ tra cứu. Nội dung pháp lý cần đối chiếu PDF gốc hoặc nguồn chính thức.

---

## Mục lục

1. [Repo này có gì](#1-repo-này-có-gì)
2. [Điểm khác biệt](#2-điểm-khác-biệt)
3. [Cấu trúc thư mục dự án](#3-cấu-trúc-thư-mục-dự-án)
4. [Cài đặt từ đầu đến khi mở được web](#4-cài-đặt-từ-đầu-đến-khi-mở-được-web)
5. [Lỗi thường gặp khi mang sang máy khác](#5-lỗi-thường-gặp-khi-mang-sang-máy-khác)
6. [Danh mục tài liệu kỹ thuật đồ án](#6-danh-mục-tài-liệu-kỹ-thuật-đồ-án)
7. [Đội ngũ và giấy phép](#7-đội-ngũ-và-giấy-phép)

---

## 1. Repo này có gì

Ba phần chạy cùng nhau:

```mermaid
flowchart LR
    U[Người dùng trình duyệt] --> FE[Frontend React + Vite<br/>localhost:5173]
    FE -->|REST /api/v1| API[Backend FastAPI<br/>localhost:8000]
    API --> DB[(PostgreSQL<br/>dau_second_brain)]
    API --> FILES[PDF và chỉ mục FAISS<br/>backend/data]
    API --> NLP[Mô hình cục bộ<br/>ViT5 · mDeBERTa · MiniLM]
    API -->|Chat và OCR trang scan| GEMINI[Gemini API]
    API -->|SSE tiến trình| FE
```

| Thành phần | Công nghệ | Việc nó làm |
|---|---|---|
| Giao diện | React 19, TypeScript, Vite | Đăng nhập, menu theo vai trò, rà soát, tra cứu, chat, đồ thị |
| API | FastAPI, SQLAlchemy, JWT | Upload, crawl, review, search, chat, báo cáo DOCX |
| Dữ liệu | PostgreSQL | Văn bản, nghĩa vụ, ngưỡng, quan hệ, audit, phiên chat |
| Vector | MiniLM + FAISS | Đoạn trích cho chatbot (384 chiều, inner product) |
| Lịch | APScheduler | 02:00 crawl tối đa 10 văn bản; mỗi 30 phút kiểm tra nguồn mới |

Hai vai trò:

| Vai trò | Thấy gì trên web |
|---|---|
| **Admin** | Ưu tiên xử lý, văn bản hết hiệu lực, hạn chót, phân tích, sự kiện luật, hàng đợi rà soát, chủ đề, tải PDF, nhật ký, văn bản loại bỏ — cộng toàn bộ mục tra cứu |
| **Giảng viên** | Tra cứu thủ công, chatbot, việc phải làm, sổ ngưỡng, đồ thị ảnh hưởng, phân tích |

```mermaid
flowchart TD
    A[Đăng nhập] --> B{Vai trò}
    B -->|Admin| C[Tải PDF hoặc chọn file crawler]
    C --> D[Pipeline đọc và trích xuất]
    D --> E[Hàng đợi: nghĩa vụ và ngưỡng chờ duyệt]
    E --> F[Sửa / công bố / từ chối]
    F --> G[Màn tra cứu và đồ thị]
    B -->|Giảng viên| G
    G --> H[Tìm theo tên, chủ đề, thẻ]
    G --> I[Hỏi chatbot kèm citation]
```

---

## 2. Điểm khác biệt

Kho văn bản hành chính tiếng Việt thường chỉ là file PDF. Repo này gắn một **pipeline đọc — trích — kiểm — duyệt — tra cứu** vào đúng kho đó.

### Mô hình nào chạy ở đâu

| Công đoạn | Cách làm trong code | Chạy ở đâu |
|---|---|---|
| Đọc PDF có lớp chữ | PyMuPDF, giữ mốc `--- TRANG N ---` | Máy local |
| PDF scan (dưới khoảng 20 từ/trang) | Render ảnh bằng Poppler/`pdf2image`, gửi Gemini OCR | API ngoài, admin phải xác nhận trên giao diện |
| Chia đoạn | Chọn một cấp cấu trúc: Điều, Chương, mục số hoặc trang | Máy local |
| Metadata và quan hệ | Regex: cơ quan, ngày ký, người ký, hiệu lực, căn cứ / thay thế / sửa đổi / bãi bỏ | Máy local |
| Chủ đề | Chấm điểm từ khóa; dưới ngưỡng thì gán `Khác` | Máy local |
| Nghĩa vụ và ngưỡng số | Luật/regex chọn đoạn ứng viên, tối đa một bản ghi mỗi loại mỗi lần nạp | Máy local |
| Tóm tắt | `VietAI/vit5-base-vietnews-summarization` | Máy local |
| Kiểm tra câu tóm tắt có bám nguồn không | `mDeBERTa-v3-base-xnli` — 3 nhãn `entailment` / `neutral` / `contradiction` | Máy local |
| Embedding cho chat | `paraphrase-MiniLM-L3-v2` + FAISS | Máy local |
| Câu trả lời hội thoại | Gemini, tối đa 5 đoạn gần nhất | API ngoài |

Gemini chỉ dùng cho **chatbot** và **OCR trang scan**. Tóm tắt, NLI và embedding không gọi Gemini.

### Luồng một file PDF

```mermaid
flowchart TD
    A[Admin upload PDF hoặc đưa file crawler vào xử lý] --> B[Lưu backend/data]
    B --> C[PyMuPDF đọc chữ]
    C --> D{Ít chữ trên trang?}
    D -->|Có và đã cho phép OCR| E[Ảnh trang → Gemini OCR]
    D -->|Có và chưa cho phép| X[Báo cần xác nhận OCR]
    D -->|PDF có chữ| F[Chia đoạn + metadata + chủ đề]
    E --> F
    F --> G[Nghĩa vụ / ngưỡng + tóm tắt ViT5]
    G --> H[NLI 3 nhãn trên bản tóm tắt]
    H --> I[Quan hệ văn bản bằng regex]
    I --> J[Embedding MiniLM ghi FAISS]
    J --> K[SSE báo tiến trình cho giao diện]
    K --> L[Mục ở trạng thái chờ rà soát]
    L --> M{Admin}
    M -->|Sửa| N[Chạy lại NLI; contradiction thì không nhận bản sửa]
    M -->|Công bố hoặc từ chối| O[Ghi audit trail]
```

Nguồn crawl tự động là [vanban.chinhphu.vn](https://vanban.chinhphu.vn): lịch trong `backend/app/main.py`, file tải về `backend/data/vanban_caotudong`. Admin cũng bấm crawl thủ công (tối đa 5 file mỗi lần).

### Những gì khách nên biết trước khi demo

- NLI gắn với **bản tóm tắt nghĩa vụ và ngưỡng**, và chạy lại khi admin sửa. Hàng đợi duyệt theo từng mục, kèm nhật ký thao tác.
- Tra cứu thủ công lọc `filename`, chủ đề và thẻ trên PostgreSQL.
- Chatbot lấy đoạn từ FAISS rồi nhờ Gemini viết câu trả lời có citation. Người xem vẫn cần mở PDF gốc.
- Bảng được tạo lúc backend khởi động (`create_all`). Repo không dùng Docker Compose.

Chi tiết từng bước: [docs/workflow.md](docs/workflow.md).

---

## 3. Cấu trúc thư mục dự án

```
AI_Second_Brain_DAU/
├── backend/                              # API FastAPI và pipeline AI
│   ├── app/
│   │   ├── main.py                       # App, CORS, tạo bảng, lịch crawl
│   │   ├── api/
│   │   │   ├── endpoints.py              # Gắn toàn bộ router vào /api/v1
│   │   │   ├── routers/
│   │   │   │   ├── auth.py               # Đăng nhập JWT, /auth/me
│   │   │   │   ├── documents.py          # Upload, crawl đã tải, chủ đề, legal-data, impact
│   │   │   │   ├── review.py             # Hàng đợi, sửa/NLI, publish, reject
│   │   │   │   ├── search.py             # Tra cứu metadata
│   │   │   │   ├── chat.py               # Phiên chat + RAG
│   │   │   │   ├── analytics.py
│   │   │   │   ├── audit.py              # Cảnh báo quan hệ + nhật ký
│   │   │   │   ├── reports.py            # Xuất DOCX
│   │   │   │   └── system.py             # Trạng thái, crawl, SSE
│   │   │   └── schemas/                  # Pydantic (user, token)
│   │   ├── core/                         # config.py, security.py (JWT, bcrypt)
│   │   ├── db/                           # models.py, session.py
│   │   ├── scripts/create_admin.py       # Tạo admin/giảng viên, hỏi mật khẩu
│   │   └── services/
│   │       ├── pdf_parser.py             # PyMuPDF, OCR fallback, chia đoạn
│   │       ├── nlp_pipeline.py           # ViT5, mDeBERTa QA + NLI, MiniLM
│   │       ├── ocr_api.py                # Gemini OCR
│   │       ├── vector_db.py              # FAISS IndexFlatIP
│   │       ├── notifier.py               # Sự kiện tiến trình
│   │       └── ingestion/crawl_documents.py
│   ├── bin/
│   │   ├── poppler/                      # pdftoppm — render trang PDF khi OCR
│   │   ├── patched_tokenizer/            # Tokenizer ViT5 đã vá, dùng nếu có
│   │   └── tessdata/                     # Dữ liệu Tesseract cũ, pipeline hiện không gọi
│   ├── data/                             # Runtime: uploads, PDF crawl, faiss_*.bin/json, cache model
│   ├── scripts/download_models.py        # Tải trước 4 model Hugging Face
│   ├── tests/                            # Giới hạn OCR và PDF
│   ├── .env.example
│   ├── requirements.txt                  # Thư viện chạy app, pin phiên bản
│   └── requirements-dev.txt              # pytest
│
├── frontend/                             # SPA React + Vite
│   ├── src/
│   │   ├── pages/                        # Login, Priority, Review, Search, Chat, Graph, Admin...
│   │   ├── components/layout/            # Layout, Sidebar, Header
│   │   ├── components/shared/            # Drawer chi tiết, modal xác nhận
│   │   ├── context/                      # Auth, Data, Detail
│   │   └── api/axiosClient.ts            # Gọi /api/v1, gắn JWT
│   ├── vite.config.ts                    # Proxy /api → http://127.0.0.1:8000
│   └── package.json
│
├── docs/                                 # Đặc tả, hướng dẫn chạy, hỏi đáp (mục 6)
├── deploy/                               # Ghi chú Cloudflare Tunnel, Tailscale, triển khai
├── requirements.txt                      # Bản thư viện ở thư mục gốc (cùng pin với backend)
├── requirements.py                       # Script chẩn đoán cũ — xem lưu ý ở mục 4
├── LICENSE                               # MIT
└── README.md
```

Bảng chính trong PostgreSQL (`backend/app/db/models.py`): `User`, `Document`, `Obligation`, `Threshold`, `DocumentRelation`, `DocumentEmbedding`, `AuditTrail`, `ChatSession`, `ChatMessage`.

---

## 4. Cài đặt từ đầu đến khi mở được web

Làm trên Windows PowerShell. Máy cần mạng ở lần cài pip và lần tải model.

### 4.1. Phần mềm cần có trước

| Phần mềm | Phiên bản | Ghi chú |
|---|---|---|
| Python | **3.11** (chấp nhận 3.10–3.12), 64-bit | 3.13 dễ thiếu wheel PyTorch / tokenizers |
| Node.js | **20 LTS** trở lên | Kèm `npm`. Frontend dùng Vite 8 |
| PostgreSQL | 14 trở lên | Tạo database trống, app tự tạo bảng |
| Poppler | `pdftoppm` trong PATH | Chỉ cần khi OCR PDF scan. Có sẵn trong `backend/bin/poppler` |
| RAM | 8 GB tối thiểu, **16 GB** dễ chịu hơn | Model load cùng lúc khá nặng; xem mục 5 nếu gặp WinError 1455 |

Git clone repo về máy, rồi mở terminal **tại thư mục gốc** `AI_Second_Brain_DAU`.

### 4.2. PostgreSQL

Trong pgAdmin hoặc `psql`:

```sql
CREATE DATABASE dau_second_brain;
```

User trong chuỗi kết nối phải có quyền trên database này. Ví dụ user `postgres` trên máy local.

### 4.3. File `backend/.env`

```powershell
Copy-Item backend\.env.example backend\.env
```

Mở `backend/.env` và điền. Không commit file này, không dán key vào chat.

```env
DATABASE_URL=postgresql://postgres:MAT_KHAU_POSTGRES@127.0.0.1:5432/dau_second_brain

# Chuỗi ngẫu nhiên dài. Tạo bằng lệnh ở dưới.
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

CORS_ORIGINS=http://localhost:5173

# Chatbot. Có thể thêm GEMINI_API_KEY_2 và _3 để xoay key khi hết quota.
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.6-flash

# OCR trang scan — key riêng, không dùng chung key chatbot.
OCR_API_KEY=
OCR_MODEL=gemini-3.6-flash
OCR_TIMEOUT_SECONDS=90
OCR_MAX_PAGES=20
OCR_MAX_PDF_MB=20
OCR_MAX_IMAGE_MB=4
OCR_MAX_RETRIES=2

# Cache model. Trên Windows dùng đường dẫn tuyệt đối, dấu gạch chéo xuôi.
HF_HOME=E:/AI_Second_Brain_DAU/backend/data/models
```

Tạo `SECRET_KEY`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Thiếu `GEMINI_API_KEY` thì chatbot không trả lời. Thiếu `OCR_API_KEY` thì PDF scan không đọc được; PDF có lớp chữ vẫn chạy.

### 4.4. Backend

```powershell
Set-Location backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1
python -m pip install -r requirements.txt
```

PowerShell chặn script kích hoạt venv thì chạy một lần:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Tải model (vài GB, cần mạng). Lệnh này đọc `HF_HOME` trong `.env`:

```powershell
python scripts/download_models.py
```

Thêm `--verify` nếu muốn load thử từng model rồi giải phóng RAM.

Tạo tài khoản. Mật khẩu gõ trên terminal (ít nhất 10 ký tự), không có tài khoản mặc định trong app:

```powershell
python -m app.scripts.create_admin --email admin@example.com --role admin
```

Giảng viên: cùng lệnh với `--role lecturer`. Đặt lại mật khẩu: thêm `--reset-password`.

Chạy API:

```powershell
uvicorn app.main:app --reload --port 8000
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

Giữ cửa sổ này mở.

### 4.5. Frontend

Terminal **mới**, tại thư mục gốc:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Mở http://localhost:5173 và đăng nhập bằng email vừa tạo.

Vite proxy `/api` sang `http://127.0.0.1:8000`, nên lúc dev không cần `VITE_API_URL`. Khi frontend và API khác origin, đặt `VITE_API_URL` (ví dụ `https://host-cua-ban/api/v1`) và khai báo origin đó trong `CORS_ORIGINS`.

### 4.6. Kiểm tra nhanh

1. Swagger mở được và `GET /` trả lời welcome.
2. Đăng nhập admin vào được màn **Ưu tiên xử lý**.
3. Vào **Tải tài liệu**, upload một PDF có lớp chữ (không phải bản scan).
4. Thanh tiến trình SSE chạy; sau đó mục nghĩa vụ/ngưỡng xuất hiện ở **Cần rà soát** nếu pipeline trích được.
5. `GET /search` hoặc ô tra cứu tìm được tên file.

OCR scan: Poppler phải gọi được `pdftoppm`. Trên Windows có thể thêm vào PATH cho phiên hiện tại:

```powershell
$env:Path = "E:\AI_Second_Brain_DAU\backend\bin\poppler\Library\bin;" + $env:Path
```

Đúng đường dẫn con thư mục bản Poppler đang có trong `backend/bin/poppler` (đôi khi là `Library\bin`, đôi khi là `bin`). Upload bản scan trên UI phải tick xác nhận gửi ảnh ra OCR.

Test backend (tùy chọn):

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests
```

### 4.7. Linux hoặc macOS

Các bước giống trên, với vài lệnh khác:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1
python -m pip install -r requirements.txt
cp .env.example .env
# sửa .env, rồi:
python scripts/download_models.py
python -m app.scripts.create_admin --email admin@example.com --role admin
uvicorn app.main:app --reload --port 8000
```

Terminal khác: `cd frontend && npm ci && npm run dev`.

Poppler trên Ubuntu: `sudo apt install poppler-utils`. Trên macOS: `brew install poppler`.

### 4.8. Script `python requirements.py` ở thư mục gốc

File này là bộ chẩn đoán đời trước. Nó vẫn tìm Tesseract, có thể tự ghi `backend/.env` với secret yếu, và in một email/mật khẩu mẫu **mà ứng dụng không tạo**. Đường cài trong mục 4.3–4.5 là đường đang khớp code. Muốn xem thêm: [docs/usage.md](docs/usage.md).

---

## 5. Lỗi thường gặp khi mang sang máy khác

### Python 3.13 hoặc thiếu wheel

`pip install` báo build C++ (`tokenizers`, `sentencepiece`). Dùng Python 3.11 64-bit và cài `torch==2.5.1` từ index CPU **trước** `requirements.txt` (mục 4.4).

### PostgreSQL từ chối kết nối

`password authentication failed` hoặc `database "dau_second_brain" does not exist`: dịch vụ Postgres đang chạy, database đã tạo, `DATABASE_URL` đúng user, mật khẩu, host `127.0.0.1`, cổng `5432`.

### WinError 1455 — paging file is too small

PyTorch không cấp được bộ nhớ ảo khi load model. Tăng paging file Windows: *System Properties → Advanced → Performance → Advanced → Virtual memory*. Custom size khoảng Initial 8192 MB, Maximum 16384 MB, rồi khởi động lại. Đóng ứng dụng khác trước lần load model đầu.

### Lần chạy đầu treo hoặc lỗi Hugging Face

Máy cần mạng để tải weight nếu chưa chạy `download_models.py`. Sau đó app đọc cache `HF_HOME`. Đặt `HF_HOME` trỏ tới thư mục thật, cùng giá trị khi tải và khi chạy uvicorn.

### PDF scan báo thiếu Poppler hoặc OCR

`PDFInfoNotInstalledError`: cài Poppler và đưa `pdftoppm` vào PATH (mục 4.6). OCR còn cần `OCR_API_KEY`, `OCR_MODEL`, và ô xác nhận trên form upload. Ảnh trang được gửi ra ngoài máy — không bật với tài liệu mật.

### Chatbot im hoặc 429

Điền ít nhất một `GEMINI_API_KEY`. Model trong `GEMINI_MODEL` phải là model key đó được phép gọi. Key phụ `_2`, `_3` dùng khi key chính hết quota.

### Frontend trắng hoặc 401 liên tục

Backend phải đang chạy cổng 8000. Dev server Vite phải là cổng 5173 để khớp `CORS_ORIGINS`. Sai mật khẩu: tạo lại bằng `create_admin --reset-password`.

### Script doctor in `admin@dau.edu.vn / admin123`

Đó là dòng chữ cũ trong `requirements.py`. Backend không seed mật khẩu đó. Dùng tài khoản đã tạo ở mục 4.4.

---

## 6. Danh mục tài liệu kỹ thuật đồ án

Thư mục `docs/` gồm hai lớp: **đặc tả đồ án** (đối chiếu với code ngày 10/11/2026) và **sổ tay vận hành** để chạy, đọc luồng, trả lời câu hỏi.

### Sổ tay — đọc trước khi cài hoặc demo

| Tài liệu | Dùng khi nào |
|---|---|
| [Hướng dẫn chạy ứng dụng](docs/usage.md) | Checklist cài backend/frontend, biến môi trường, giới hạn OCR và dữ liệu runtime |
| [Luồng xử lý thực tế](docs/workflow.md) | Sơ đồ upload, crawl, review, search, chat, đồ thị, audit, báo cáo |
| [Hỏi đáp trạng thái hệ thống](docs/Q&A.md) | Câu hay gặp: Gemini dùng ở đâu, NLI chặn những gì, chatbot có lọc văn bản đã duyệt không |
| [Tóm tắt gửi GVHD](docs/repo_gvhd_readme.md) | Một trang: sản phẩm trong repo và những gì không nên cam kết khi chưa đo |

### Đặc tả đồ án

| # | Tài liệu | Nội dung hiện có trong file |
|---|---|---|
| 1 | [Đề cương](docs/DAU_Second_Brain_De_Cuong_Chi_Tiet.md) | Mục tiêu, thành phần đã có trong code, phạm vi chưa chứng minh, luồng người dùng |
| 2 | [Nghiệp vụ và kiến trúc](docs/DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md) | Sơ đồ React–FastAPI–PostgreSQL–FAISS–Gemini, trách nhiệm từng module, lịch crawler |
| 3 | [Yêu cầu chức năng](docs/DAU_Second_Brain_Dac_Ta_Yeu_Cau_Chuc_Nang.md) | Ma trận FR: cái đã có một phần và cái chưa đạt đặc tả cũ (citation từng câu, gate toàn văn, NER huấn luyện) |
| 4 | [Giao diện](docs/DAU_Second_Brain_UIUX_Spec.md) | Bảng route thật (`/priority`, `/review`, `/search`, `/chat`, `/graph`…) và quyền admin / lecturer |
| 5 | [Kế hoạch dữ liệu](docs/DAU_Second_Brain_Ke_Hoach_Du_Lieu.md) | PDF runtime, entity ORM, crawler Chính phủ, các bước tiền xử lý |
| 6 | [Kế hoạch đánh giá](docs/DAU_Second_Brain_Ke_Hoach_Danh_Gia.md) | Test OCR/PDF đang có; chỉ số ROUGE, BERTScore, NLI là việc cần đo, chưa phải kết quả nghiệm thu |
| 7 | [Phân công RACI](docs/DAU_Second_Brain_Phan_Cong_RACI.md) | Biểu mẫu vai trò frontend, backend, nhóm, GVHD — tên thành viên để nhóm điền |
| 8 | [Thuật toán đang dùng](docs/CÁC%20THUẬT%20TOÁN%20SỬ%20DỤNG.md) | Bảng công đoạn ↔ model/regex trong repo, và kỹ thuật không có trong code |

Ghi chú triển khai ra mạng (Cloudflare Tunnel, Tailscale) nằm ở `deploy/`, tách khỏi đặc tả học thuật.

Swagger http://localhost:8000/docs là danh sách endpoint sống. Nhóm chính: `/auth`, `/documents`, `/topics`, `/legal-data`, `/review`, `/search`, `/chat`, `/analytics`, `/auditing`, `/audit`, `/system`, `/impact`, `/reports/template/{document_id}`.

---

## 7. Đội ngũ và giấy phép

- **Đơn vị:** Trường Đại học Kiến trúc Đà Nẵng (DAU).
- **Học phần:** Đồ án Trí tuệ nhân tạo.
- **Mã nguồn:** giấy phép MIT, xem [LICENSE](LICENSE).

Đồ án phục vụ học tập và thử nghiệm tra cứu văn bản nội bộ. Bản quyền dữ liệu PDF (văn bản nhà nước, tài liệu nhà trường) thuộc chủ sở hữu văn bản; repo không cấp quyền phân phối lại các file đó.
