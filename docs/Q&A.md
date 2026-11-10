# Hỏi đáp về trạng thái hệ thống

**Cập nhật:** 10/11/2026

### Dự án có backend hay là demo HTML tĩnh?

Repository hiện tại là ứng dụng React/Vite kết nối backend FastAPI và PostgreSQL. Tài liệu cũ mô tả một demo HTML/data.js độc lập không tương ứng với cấu trúc code hiện tại.

### Cài đặt ở đâu?

Xem [`usage.md`](usage.md). Backend chạy từ thư mục `backend`, frontend từ `frontend`; cần PostgreSQL và cấu hình `.env`.

### Hệ thống có dùng Gemini không?

Có. Gemini dùng cho câu trả lời chatbot và OCR trang scan. OCR là xử lý bên ngoài và phải được cấu hình/cho phép. Tóm tắt, NLI và embedding dùng model Hugging Face theo code.

### Văn bản scan có tự động OCR không?

Chỉ khi được cho phép. Upload từ UI mặc định yêu cầu xác nhận gửi ảnh sang OCR API; giới hạn trang/dung lượng được cấu hình bằng biến `OCR_*`.

### Mọi câu trả lời chatbot có kiểm chứng NLI và chỉ dựa trên văn bản đã duyệt không?

Không. Chat truy xuất FAISS rồi gọi Gemini; route chat hiện không lọc trạng thái `published` và không gọi NLI trên câu trả lời. Không nên coi câu trả lời là kết luận pháp lý.

### NLI chặn xuất bản toàn bộ văn bản không?

Chưa theo đặc tả từng câu/toàn văn. NLI đang gắn với summary của obligation/threshold và hành động sửa trong review; review queue xử lý từng record.

### Extraction có phải NER AI đầy đủ không?

Không. Metadata, nghĩa vụ, ngưỡng và relation chủ yếu dùng regex/rule-based. Chủ đề dùng keyword scoring; chỉ một đoạn ứng viên cho mỗi loại nghĩa vụ/ngưỡng được chọn trong luồng ingest hiện tại.

### Có số liệu chính xác/benchmark đã đạt không?

Repository không chứa báo cáo đánh giá precision/recall/F1, ROUGE/BERTScore hay latency. Xem [`DAU_Second_Brain_Ke_Hoach_Danh_Gia.md`](DAU_Second_Brain_Ke_Hoach_Danh_Gia.md) để biết cách đo cần bổ sung.

### Cảnh báo hiệu lực có thay thế tư vấn pháp lý không?

Không. Cảnh báo dựa trên relation và status đã lưu trong hệ thống; cần đối chiếu văn bản gốc và nguồn pháp luật chính thức.
