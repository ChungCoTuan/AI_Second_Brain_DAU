# Thuật toán và mô hình đang dùng

Tài liệu này mô tả implementation hiện có trong repository, không phải danh sách dự kiến. Cập nhật: 10/11/2026.

## Luồng xử lý hiện tại

| Công đoạn | Cách triển khai trong code |
|---|---|
| Đọc PDF | PyMuPDF (`fitz`) trích xuất text và giữ dấu trang. |
| OCR | Nếu trung bình dưới 20 từ/trang, yêu cầu cho phép OCR ngoài; render PDF qua `pdf2image`, nén ảnh bằng Pillow và gửi từng trang đến Gemini OCR API. |
| Chia đoạn | Regex chọn một cấp cấu trúc phù hợp: Điều, Chương/Phần, số La Mã, mục số hoặc trang. Đây là adaptive chunking, không phải cấu trúc `DocumentChunk` được lưu trong cơ sở dữ liệu. |
| Metadata | Regex trích cơ quan, ngày ký, người ký, ngày hiệu lực và danh sách từ khóa. |
| Chủ đề | Keyword scoring; cần tối thiểu 3 điểm cho một nhãn, nếu không thì `Khác`. Không dùng mô hình phân loại đã huấn luyện. |
| Nghĩa vụ và con số | Rule-based/regex trích một đoạn được chọn theo từ khóa; không phải bộ NER hay pipeline trích xuất toàn bộ nghĩa vụ. |
| Tóm tắt | Mô hình seq2seq `VietAI/vit5-base-vietnews-summarization` chạy bằng Transformers; có thể dùng tokenizer đã vá trong `backend/app/bin/patched_tokenizer`. |
| Kiểm tra NLI | `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`, nhãn `entailment`, `neutral`, `contradiction`. |
| Embedding và tìm kiếm chatbot | `paraphrase-MiniLM-L3-v2` (384 chiều), normalize vector và lưu/tìm bằng FAISS `IndexFlatIP`. |
| Sinh câu trả lời chatbot | Google Gemini API; các key cấu hình được luân phiên khi gặp quota/lỗi tạm thời. |
| Quan hệ văn bản | Regex phát hiện căn cứ, thay thế, bãi bỏ và sửa đổi; dữ liệu lưu ở `DocumentRelation`. |
| Sinh mẫu báo cáo | `python-docx` tạo DOCX; loại khung được chọn bằng nhận diện từ khóa trên tên file. |

## Những kỹ thuật không được dùng trong implementation hiện tại

- Không có TextRank, PhoBERT+CRF, SVM hoặc fine-tuning.
- Không có tính ROUGE/BERTScore hay bộ test Gold Standard trong pipeline.
- Không có embedding cho “Cây văn bản” theo độ tương đồng; endpoint đồ thị dựa trên quan hệ trong cơ sở dữ liệu.
- Gemini được dùng cho chatbot và OCR; extraction metadata/nghĩa vụ/con số và topic classification là xử lý cục bộ theo luật.
- NLI được gọi trong luồng trích xuất/review; câu trả lời RAG không được NLI kiểm tra ở endpoint chat.

## Mã nguồn liên quan

- PDF/OCR/chunking: [`backend/app/services/pdf_parser.py`](../backend/app/services/pdf_parser.py), [`backend/app/services/ocr_api.py`](../backend/app/services/ocr_api.py)
- NLP, model IDs, phân loại và RAG: [`backend/app/services/nlp_pipeline.py`](../backend/app/services/nlp_pipeline.py)
- FAISS: [`backend/app/services/vector_db.py`](../backend/app/services/vector_db.py)
- Orchestration ingestion: [`backend/app/api/routers/documents.py`](../backend/app/api/routers/documents.py)

Điểm số NLI, keyword score hay confidence không phải chứng nhận tính đúng pháp lý. Người dùng cần kiểm tra bản gốc trước khi dựa vào kết quả.
