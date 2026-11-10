# Đề cương dự án DAU Second Brain

**Cập nhật trạng thái theo repository:** 10/11/2026

## 1. Mục tiêu

Xây dựng ứng dụng web hỗ trợ nạp, tổ chức, tra cứu và rà soát một kho PDF văn bản của Trường Đại học Kiến trúc Đà Nẵng. Trọng tâm kỹ thuật của code hiện có là đọc PDF, trích metadata và thông tin pháp lý theo luật, đưa câu hỏi qua tìm kiếm vector và hỗ trợ admin review dữ liệu trích xuất.

Ứng dụng là công cụ hỗ trợ tra cứu, không phải nguồn xác nhận hiệu lực pháp lý. Người dùng phải kiểm tra nội dung PDF gốc.

## 2. Thành phần đã có trong code

- Frontend React 19, TypeScript, Vite và React Router.
- Backend FastAPI, SQLAlchemy, PostgreSQL, JWT role `admin`/`lecturer`.
- Upload PDF, crawler `vanban.chinhphu.vn`, xử lý PDF nền, topic keyword scoring và dữ liệu nghĩa vụ/ngưỡng.
- Tóm tắt ViT5, NLI mDeBERTa, MiniLM + FAISS, Gemini chatbot và OCR ngoài có kiểm soát.
- Review obligation/threshold, audit trail, báo cáo DOCX, cảnh báo relation và SSE tiến trình.

Xem chi tiết các luồng trong [`workflow.md`](workflow.md) và [`DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md`](DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md).

## 3. Phạm vi chưa được chứng minh/hoàn thành

Code hiện không cung cấp đầy đủ các năng lực từng nêu trong đề cương cũ: citation từng câu, bộ NER được huấn luyện, hiệu chuẩn “zero hallucination”, publish gate ở cấp toàn văn, RAG chỉ trên tài liệu đã duyệt, template library, hay semantic document graph. Các API/UI liên quan hiện có chỉ thực hiện một phần chức năng.

Không có cơ sở để khẳng định mô hình đạt một ngưỡng chính xác cụ thể. Không ghi nhận số lượng văn bản đã xử lý như một kết quả cố định; dữ liệu phụ thuộc vào PostgreSQL và các file runtime trong `backend/data`.

## 4. Luồng người dùng chính

1. Người dùng đăng nhập bằng tài khoản do quản trị viên tạo.
2. Admin tải PDF lên hoặc chọn file crawler; nếu PDF scan, xác nhận trước khi gửi ảnh cho dịch vụ OCR ngoài.
3. Backend trích xuất/chia đoạn, chạy heuristic và mô hình, rồi tạo dữ liệu cần rà soát.
4. Admin xem/duyệt/sửa/từ chối nghĩa vụ và ngưỡng trong review queue.
5. Người dùng tra cứu metadata/văn bản hoặc hỏi chatbot; kết quả chatbot có thể kèm citation từ metadata FAISS.

## 5. Hướng phát triển/đánh giá tiếp theo

- Lưu cấu trúc chunk và citation mapping bền vững.
- Tăng độ phủ extraction, đánh giá trên tập gán nhãn và báo cáo sai số.
- Bảo đảm ranh giới truy xuất giữa tài liệu `published` và trạng thái khác.
- Quản lý phiên bản/hiệu lực văn bản và relation có kiểm chứng.
- Bổ sung kiểm thử tích hợp cho auth, ingestion, review, search và chat.

Các mục trên là đề xuất; chưa được xem là tính năng đang chạy.
