# Bản đồ Chỉ dẫn Agent (Context Map)

Đây là file hướng dẫn đầu tiên (entry point) khi AI Agent tham gia vào dự án.
Dựa vào loại task được giao, hãy đọc các file tương ứng trong `.antigravity/` để lấy bối cảnh (context) cần thiết trước khi viết code.

## 1. Các Quy tắc Bắt buộc (Globals)
Phải tuân thủ trong MỌI TASK:
- `globals/01-architecture.md`: Tóm tắt luồng hoạt động 5 bước của hệ thống.
- `globals/02-data-models.md`: Các model dữ liệu quan trọng như Sự kiện hiệu lực, Nghĩa vụ, Con số chốt, DocumentChunk.
- `globals/03-security-bounds.md`: Ràng buộc an toàn cốt lõi (Không bịa đặt thông tin, Cross-Auditing).
- `globals/04-conventions.md`: Quy ước viết code (React, TS, cấu trúc thư mục).

## 2. Hướng dẫn Theo Dịch vụ (Services)
Chỉ đọc khi task có liên quan đến domain cụ thể:
- **Xử lý ngôn ngữ (NLI, Summarization)**: Đọc `services/summarization/01-nli-3-nhan.md`
- **Quy trình Duyệt bài (Publish Gate)**: Đọc `services/review-service/01-publish-gate.md`
