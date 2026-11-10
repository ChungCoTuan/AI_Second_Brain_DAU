# Phân công công việc (RACI)

**Cập nhật:** 10/11/2026

> Đây là biểu mẫu quản lý nhóm, không phải dữ liệu suy ra từ Git. Tên thành viên và mức phân công cần được nhóm xác nhận; mã nguồn chỉ cho biết khu vực chức năng, không chứng minh ai thực hiện.

## 1. Vai trò

| Vai trò | Người đảm nhận | Trách nhiệm |
|---|---|---|
| Thành viên phụ trách frontend | *(điền tên)* | React/TypeScript, điều hướng, UI và gọi API. |
| Thành viên phụ trách backend | *(điền tên)* | FastAPI, ORM/PostgreSQL, PDF/NLP, crawler và tích hợp. |
| Cả nhóm | *(điền tên)* | Review liên module, kiểm thử end-to-end, docs và báo cáo. |
| GVHD | *(điền tên)* | Xác nhận phạm vi, tiêu chí nghiệp vụ và quyền sử dụng dữ liệu. |

Có thể cùng một người phụ trách nhiều vai trò. Cập nhật bảng theo phân công thực tế thay vì coi đây là lịch sử commit.

## 2. RACI

- **R** — thực hiện.
- **A** — chịu trách nhiệm cuối cùng.
- **C** — được tham vấn.
- **I** — được thông báo.

| Hạng mục hiện có | Frontend | Backend | Cả nhóm/GVHD |
|---|---:|---:|---:|
| Trang React, auth state, API client | R/A | C | I |
| FastAPI routes, DB model, JWT | C | R/A | I |
| PDF parsing, OCR consent, chunking | C | R/A | C |
| NLP extraction, NLI, embedding, RAG | C | R/A | C |
| UI/API integration và regression tests | R | R | A |
| Dataset/metric và diễn giải pháp lý | C | C | R/A |
| Secrets, quyền dữ liệu và deployment | R | R | A |

## 3. Khu vực code

- Frontend: `frontend/src/pages`, `frontend/src/context`, `frontend/src/api`.
- Backend: `backend/app/api`, `backend/app/db`, `backend/app/services`.
- Tests hiện có tập trung vào OCR/PDF tại `backend/tests`.

## 4. Quy tắc phối hợp đề xuất

1. Chốt API/schema trước khi đổi đồng thời frontend và backend.
2. Review thay đổi liên quan quyền truy cập, dữ liệu nhạy cảm và OCR ngoài.
3. Gắn test hoặc bước kiểm chứng cho thay đổi behavior; phân biệt lỗi code với hạn chế dữ liệu/model.
4. Cập nhật tài liệu sau khi tính năng được triển khai; không mô tả kế hoạch như chức năng đã hoàn thành.
