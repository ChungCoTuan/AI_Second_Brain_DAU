# Kế hoạch dữ liệu và xử lý

**Cập nhật:** 10/11/2026

## 1. Dữ liệu runtime

Backend dùng PostgreSQL cho metadata/record và thư mục `backend/data` cho PDF, FAISS index, metadata vector và trạng thái crawler. Một số PDF và file FAISS được version hóa trong repository; nội dung DB phụ thuộc môi trường runtime. Không có căn cứ trong code để công bố cố định tổng số tài liệu/điều/nghĩa vụ/ngưỡng.

Các ORM entity hiện tại: `Document`, `Obligation`, `Threshold`, `DocumentRelation`, `DocumentEmbedding`, `AuditTrail`, `ChatSession`, `ChatMessage`, `User`. Chưa có bảng chunk riêng hay annotation Gold Standard.

## 2. Nguồn và ingest

- Crawler lấy PDF từ `vanban.chinhphu.vn`, phân nhóm theo domain/category và bỏ qua một số văn bản cũ hơn 2018 hoặc không khớp nhóm từ khóa.
- Admin có thể upload PDF vào `data/uploads`; tên file trùng bị từ chối.
- PDF scan được phát hiện heuristic (trung bình dưới 20 từ/trang). Upload scan cần người dùng xác nhận `allow_external_ocr`; crawler công khai gọi extraction với quyền OCR bật.
- OCR gửi ảnh từng trang đến Gemini API. Cần kiểm tra quyền xử lý dữ liệu và tránh tài liệu nhạy cảm trước khi bật.

## 3. Tiền xử lý và trích xuất

1. PyMuPDF đọc text, giữ marker `--- TRANG N ---`.
2. Nếu cần và được phép, `pdf2image` render trang, Pillow giảm dung lượng, Gemini OCR trả text.
3. `chunk_document` chọn cấp tách phù hợp theo nội dung; chunk hiện dùng trong tiến trình, không được lưu thành bảng riêng.
4. Regex trích metadata; topic dùng keyword scoring.
5. Chọn đoạn ứng viên nghĩa vụ/ngưỡng theo từ khóa; rule-based trích các trường; ViT5 tạo summary và mDeBERTa gán NLI.
6. Trích quan hệ văn bản bằng regex; embedding các chunk rồi thêm vào FAISS.

Hệ thống hiện không tạo dataset huấn luyện, không fine-tune mô hình và không gán nhãn tự động theo JSON schema độc lập. Kết quả extraction là gợi ý cần review.

## 4. Chất lượng và quản trị

- Duy trì PDF gốc để đối chiếu với nội dung OCR/extraction.
- Ghi nguồn/ngày thu thập/quyền sử dụng và phiên bản của mỗi tài liệu trong quy trình quản lý dữ liệu ngoài DB khi cần đánh giá.
- Ẩn thông tin cá nhân không cần thiết; không đưa nội dung nội bộ lên dịch vụ ngoài nếu chưa được phép.
- Kiểm tra thủ công ngày, số hiệu, chủ thể, đơn vị đo, điều khoản chuyển tiếp và phạm vi thay thế/bãi bỏ.
- Lưu ý hiện tại chưa có provenance đầy đủ hay bản annotation gold trong repository; không suy ra độ chính xác từ trường `conf` mặc định.

Xem giới hạn OCR trong [`backend/app/services/pdf_parser.py`](../backend/app/services/pdf_parser.py), cấu hình trong [`backend/.env.example`](../backend/.env.example), và các test OCR/PDF trong `backend/tests/`.
