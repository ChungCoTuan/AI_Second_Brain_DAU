# Kế hoạch đánh giá

**Cập nhật:** 10/11/2026
Đây là kế hoạch đo lường; các ngưỡng bên dưới không phải kết quả đã đạt.

## 1. Hiện trạng kiểm thử trong repository

Các test hiện có tập trung vào giới hạn và lỗi OCR/PDF:

- `backend/tests/test_ocr_api.py`: phản hồi thành công, thiếu cấu hình, retry 429/timeout, lỗi xác thực và kết quả bị cắt.
- `backend/tests/test_pdf_parser_limits.py`: scan cần consent, giới hạn trang/dung lượng/ảnh và lỗi OCR.

Chưa có test benchmark precision/recall cho extraction, NLI, topic classifier, audit warning, chất lượng RAG, UI performance hay ROUGE/BERTScore. Không nên đưa các con số trong tài liệu cũ thành kết quả nghiệm thu.

## 2. Bộ đánh giá cần chuẩn bị

Tạo tập PDF có quyền sử dụng và nhãn vàng do người rà soát xác nhận. Mỗi record nhãn cần giữ:

- file và checksum nguồn;
- đoạn nguyên văn/page;
- metadata hoặc relation kỳ vọng;
- nghĩa vụ/con số và trường tương ứng;
- label NLI nếu đánh giá NLI;
- kết quả mong đợi cho cảnh báo audit.

Tách dữ liệu phát triển và kiểm thử theo văn bản, tránh đưa các đoạn từ cùng một văn bản vào cả hai tập. Lưu phiên bản dataset, hướng dẫn gán nhãn và cách xử lý bất đồng.

## 3. Chỉ số đề xuất

| Thành phần | Chỉ số phù hợp |
|---|---|
| Metadata, nghĩa vụ, ngưỡng, relation | Precision, recall, F1; exact match cho số hiệu/ngày/giá trị. |
| Topic keyword classifier | Macro-F1 và confusion matrix; báo cáo riêng nhãn `Khác`. |
| NLI | Macro-F1 per label, confusion matrix, tỷ lệ false-negative của `contradiction`. |
| Audit cảnh báo | Precision/recall theo relation, kèm đánh giá thủ công trên mẫu. |
| RAG | Độ đúng câu trả lời, tính liên quan citation, tỷ lệ từ chối phù hợp; đo độc lập với NLI extraction. |
| OCR | Character error rate/word error rate trên trang gán nhãn; theo dõi lỗi số hiệu/ngày. |
| Hiệu năng | Thời gian ingest/PDF, latency API và truy vấn UI trên môi trường được ghi rõ. |

Ngưỡng chấp nhận cần được thống nhất trước khi chạy test. Cần công bố kích thước/nguồn tập test, cách tính metric và khoảng tin cậy; không suy ra ngưỡng từ số lượng ví dụ nhỏ.

## 4. Quy trình tái lập

1. Chốt commit code, cấu hình model, phiên bản dependency và dataset.
2. Chạy unit test OCR/PDF: từ thư mục repository, `python -m pytest backend/tests`.
3. Chạy script đánh giá mới trên tập giữ kín; lưu raw output và summary metric.
4. Kiểm tra lỗi nghiêm trọng bằng người có chuyên môn, đặc biệt ngày, số hiệu, phạm vi bãi bỏ và citation.
5. Báo cáo riêng kết quả benchmark và giới hạn; không gọi kết quả NLI là chứng nhận đúng pháp luật.

## 5. Trạng thái tiêu chí

Các mục dưới đây đang **chưa đo** trong repository: F1 extraction, accuracy NLI, detection rate cảnh báo, ROUGE/BERTScore, độ trễ UI. Chỉ đánh dấu đạt sau khi có test dataset, script/biên bản chạy và kết quả có thể tái lập.
