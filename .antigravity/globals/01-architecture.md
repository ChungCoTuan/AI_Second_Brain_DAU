# Sơ đồ Kiến trúc & Pipeline

Hệ thống DAU Second Brain hoạt động dựa trên luồng xử lý (pipeline) 5 bước:

1. **Ingestion (Thu thập & Tiền xử lý)**: 
   - Tải văn bản PDF/DOCX từ chinhphu.vn hoặc tài liệu trường.
   - Parse thành các đoạn văn bản có cấu trúc: `DocumentChunk` (Chương, Mục, Điều, Khoản).

2. **Extraction & Classification (Trích xuất & Phân loại)**:
   - Dùng Rule-based / NER để lấy số hiệu, ngày ban hành.
   - LLM Zero-shot/Few-shot để bóc tách: Sự kiện hiệu lực, Nghĩa vụ, Con số chốt.
   - Classifier để gán nhãn Chủ đề (Đào tạo, Tuyển sinh, Tài chính...).

3. **Summarization & NLI (Tóm tắt & Đánh giá trung thực)**:
   - Tóm tắt từng đoạn.
   - Chạy mô hình NLI 3 nhãn (Entailment, Contradiction, Neutral) lên từng câu để chống "hallucination".

4. **Suggestion & RAG (Gợi ý & Hỏi đáp)**:
   - Cung cấp tính năng Hỏi đáp (RAG) dựa trên Vector DB (FAISS/Chroma).
   - Rà soát chéo (Cross-Auditing) để sinh các cảnh báo (Warnings).

5. **UI / Dashboard (Giao diện React)**:
   - Dashboard quản trị, Sổ tra ngưỡng, Việc phải làm, Cây văn bản.
