# Hướng dẫn chạy ứng dụng

**Cập nhật:** 10/11/2026

## 1. Yêu cầu

- Python phù hợp với pinned packages trong `backend/requirements.txt`.
- Node.js/npm phù hợp với Vite trong `frontend/package.json`.
- PostgreSQL đang chạy và có database `dau_second_brain`.
- Internet lần đầu để tải model Hugging Face; Gemini API key cho chatbot và OCR nếu dùng các chức năng đó.

## 2. Cấu hình backend

Từ PowerShell tại repository root:

```powershell
Copy-Item backend\.env.example backend\.env
```

Điền `DATABASE_URL`, `SECRET_KEY` ngẫu nhiên đủ mạnh, `CORS_ORIGINS` và key cần thiết vào `backend/.env`. Không commit hoặc chia sẻ file này.

Backend hỗ trợ cấu hình `GEMINI_API_KEY` (có thể thêm `_2`, `_3`) cho chat và `OCR_API_KEY`/`OCR_MODEL` riêng cho OCR. Thiết lập model Gemini theo `GEMINI_MODEL` nếu cần. Không bật OCR ngoài cho tài liệu nhạy cảm nếu chưa được phép.

## 3. Cài và chạy backend

```powershell
Set-Location backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app.scripts.create_admin --email admin@example.com --role admin
uvicorn app.main:app --reload --port 8000
```

Nếu cần kiểm tra test OCR/PDF:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests
```

Khi backend khởi động, app tạo các bảng thiếu qua SQLAlchemy và bật lịch crawler. Swagger UI: `http://localhost:8000/docs`. Tạo admin bằng script; không có thông tin đăng nhập mặc định được tài liệu này công bố.

## 4. Cài và chạy frontend

Mở terminal khác:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Vite mặc định phục vụ tại `http://localhost:5173`. API client dùng `/api/v1` mặc định; cấu hình `VITE_API_URL` nếu môi trường cần base URL khác.

## 5. Tài liệu/API

- OpenAPI/Swagger: `http://localhost:8000/docs`.
- API prefix mặc định: `/api/v1`.
- Frontend route và role: [`DAU_Second_Brain_UIUX_Spec.md`](DAU_Second_Brain_UIUX_Spec.md).

Các endpoint chính gồm `/auth`, `/documents`, `/topics`, `/legal-data`, `/review`, `/search`, `/chat`, `/analytics`, `/auditing`, `/audit`, `/system`, `/impact` và `/reports/template/{document_id}`. OpenAPI là nguồn chuẩn cho schema hiện tại.

## 6. Dữ liệu và giới hạn vận hành

- PDF upload lưu trong `backend/data/uploads`; PDF crawler dưới `backend/data/vanban_caotudong`.
- FAISS index/metadata nằm trong `backend/data`; không xóa hoặc sửa tay khi ứng dụng đang chạy.
- Scheduler crawl lúc 02:00 và kiểm tra nguồn mỗi 30 phút khi app hoạt động.
- Chức năng chat cần ít nhất một `GEMINI_API_KEY`; OCR cần `OCR_API_KEY` và `OCR_MODEL`.
- PDF scan: upload UI cần xác nhận OCR ngoài. Giới hạn OCR có thể cấu hình qua `OCR_MAX_PAGES`, `OCR_MAX_PDF_MB`, `OCR_MAX_IMAGE_MB`, `OCR_TIMEOUT_SECONDS`, `OCR_MAX_RETRIES`.
- Chatbot, cảnh báo và extraction là hỗ trợ; xác minh nội dung pháp lý trên PDF/nguồn chính thức.

## 7. Tham khảo thêm

- Mô hình dữ liệu: [`backend/app/db/models.py`](../backend/app/db/models.py)
- Cấu hình môi trường: [`backend/.env.example`](../backend/.env.example)
- Hướng dẫn triển khai hiện có trong `backend/HUONG_DAN_TRIEN_KHAI.md`; cần rà soát riêng trước khi áp dụng cho môi trường production.
