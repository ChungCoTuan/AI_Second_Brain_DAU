# KẾ HOẠCH ĐÁNH GIÁ & TIÊU CHÍ NGHIỆM THU CHI TIẾT
## Hệ Sinh Thái "DAU Second Brain"

| | |
|---|---|
| **Phiên bản** | 1.0 |
| **Tài liệu liên quan** | SRS (Use Case & Yêu cầu chức năng), Kế hoạch Dữ liệu, Tài liệu Kiến trúc (mục CI/CD) |
| **Mục đích** | Cụ thể hóa các chỉ số đánh giá thành quy trình đo được, có ngưỡng Pass/Fail rõ ràng |

---

## MỤC LỤC
1. Mục tiêu kế hoạch đánh giá
2. Các chiều đánh giá (Evaluation Dimensions)
3. Chi tiết từng Metric & Ngưỡng đề xuất
4. Quy trình đánh giá con người (Human Evaluation)
5. Tập dữ liệu dùng để đánh giá
6. Bảng Tiêu chí Nghiệm thu tổng hợp (Go/No-Go Checklist)
7. Tích hợp đánh giá vào CI/CD (Regression Check)
8. Mẫu trình bày kết quả trong báo cáo đồ án

---

## 1. MỤC TIÊU KẾ HOẠCH ĐÁNH GIÁ

Đảm bảo mọi tuyên bố về chất lượng hệ thống (đặc biệt là "không bịa đặt thông tin") đều **có số liệu đo được, quy trình lặp lại được**, chứ không dừng ở nhận định chủ quan. Đây cũng là căn cứ để nhóm biết khi nào một chức năng "đủ tốt để demo" và khi nào cần tiếp tục cải thiện.

---

## 2. CÁC CHIỀU ĐÁNH GIÁ (EVALUATION DIMENSIONS)

| # | Chiều đánh giá | Trả lời câu hỏi | Use Case liên quan |
|---|---|---|---|
| 1 | Chất lượng tóm tắt | Bản tóm tắt có đầy đủ ý, súc tích, tự nhiên không? | UC-03 |
| 2 | **Độ trung thực (Faithfulness)** | Bản tóm tắt/câu trả lời có bịa hay thiếu ý so với nguồn không? | UC-03, UC-06 |
| 3 | Độ chính xác trích xuất thông tin | Số hiệu, ngày, cơ quan ban hành có trích đúng không? | UC-02 |
| 4 | Chất lượng hỏi-đáp (RAG) | Chatbot trả lời đúng, có trích dẫn hợp lệ không? | UC-06 |
| 5 | Chất lượng gợi ý báo cáo | Khung báo cáo đúng cấu trúc, không tự sinh nội dung? | UC-05 |
| 6 | Hiệu năng & trải nghiệm | Hệ thống phản hồi đủ nhanh, giao diện rõ ràng? | Toàn bộ |

> **Chiều số 2 (Faithfulness) là trọng tâm của đồ án** — các chiều còn lại quan trọng nhưng không phải điểm khác biệt chính.

---

## 3. CHI TIẾT TỪNG METRIC & NGƯỠNG ĐỀ XUẤT

### 3.1 Chất lượng tóm tắt

| Metric | Cách tính | Công cụ | Ngưỡng đề xuất |
|---|---|---|---|
| ROUGE-1, ROUGE-2 | Độ trùng khớp n-gram (1-gram, 2-gram) giữa tóm tắt sinh ra và gold summary | `rouge-score` (Python) | Mô hình chính (BARTpho/ViT5) phải **vượt baseline TextRank** trên cùng tập test |
| ROUGE-L | Độ trùng khớp chuỗi con dài nhất | `rouge-score` | Tương tự trên |
| BERTScore | Độ tương đồng ngữ nghĩa qua embedding (bổ sung cho ROUGE vì không chỉ so khớp từ) | `bert-score` (dùng PhoBERT làm base) | Mô hình chính phải đạt điểm F1 BERTScore cao hơn baseline |

> **Lưu ý quan trọng:** ROUGE/BERTScore chỉ đo *độ giống* với gold summary, **không đo được việc mô hình có bịa hay không** — đây là lý do bắt buộc phải có chỉ số Faithfulness riêng ở mục 3.2.

### 3.2 Độ trung thực (Faithfulness) — chỉ số quan trọng nhất

| Metric | Cách tính | Công cụ | Ngưỡng đề xuất |
|---|---|---|---|
| Faithfulness Score (per câu) | Chạy mô hình NLI: đoạn nguồn là "premise", câu tóm tắt là "hypothesis" → xác suất entailment | Mô hình NLI tiếng Việt (fine-tune từ PhoBERT/XLM-R trên tập NLI) | Câu đạt ngưỡng entailment ≥ 0.7 mới được hiển thị (ngưỡng cụ thể tinh chỉnh sau thực nghiệm) |
| Faithfulness Score (per văn bản) | % số câu trong bản tóm tắt đạt ngưỡng entailment | Tính trung bình trên toàn bộ câu của 1 văn bản | Trung bình toàn tập test **≥ 90%** *(đề xuất — cần thống nhất với GVHD, xem câu hỏi đã nêu trong Đề cương)* |
| Tỷ lệ câu bị loại bỏ | % câu bị hệ thống tự loại do không đạt ngưỡng | Đếm log hệ thống | Theo dõi xu hướng — tỷ lệ quá cao (>30%) cho thấy mô hình tóm tắt cần cải thiện, không chỉ là vấn đề của bộ lọc |

### 3.3 Độ chính xác trích xuất thông tin (NER)

| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Precision, Recall, F1 theo từng trường (số hiệu, ngày ban hành, cơ quan ban hành) | So khớp giá trị trích xuất với nhãn đã kiểm tra tay (theo Kế hoạch Dữ liệu mục 6.2) | F1 ≥ 0.85 cho các trường có format chuẩn (số hiệu, ngày); F1 ≥ 0.7 cho trường phức tạp hơn (yêu cầu báo cáo) |

### 3.4 Chất lượng hỏi-đáp (RAG)

| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Tỷ lệ trả lời đúng (Answer Accuracy) | Đánh giá con người: câu trả lời có đúng nội dung không (Đúng/Sai/Một phần) | ≥ 80% "Đúng" trên tập câu hỏi test |
| Tỷ lệ trích dẫn hợp lệ (Citation Validity) | % câu trả lời có trích dẫn thực sự chứa thông tin hỗ trợ câu trả lời | 100% — **không có ngoại lệ**, vì trả lời không trích dẫn hợp lệ đồng nghĩa vi phạm yêu cầu cốt lõi |
| Tỷ lệ từ chối đúng (Correct Refusal Rate) | Trong các câu hỏi **không có căn cứ trả lời** (cố ý đưa vào tập test), % hệ thống từ chối đúng thay vì suy đoán | ≥ 90% |
| Tỷ lệ từ chối nhầm (False Refusal Rate) | Trong các câu hỏi **có căn cứ trả lời**, % hệ thống từ chối nhầm dù có đủ thông tin | Theo dõi, không để quá cao (ảnh hưởng tính hữu dụng) — mục tiêu ≤ 15% |

### 3.5 Chất lượng gợi ý khung báo cáo

| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Đúng cấu trúc yêu cầu | Đối chiếu thủ công: các đề mục có khớp với yêu cầu nêu trong văn bản gốc không | 100% trên tập test (vì đây là logic có kiểm soát, không phải sinh tự do) |
| Không có nội dung tự sinh ở phần Số liệu/Kết luận | Audit thủ công 100% các khung báo cáo sinh ra | **Bắt buộc đạt 100%** — vi phạm điều này là lỗi nghiêm trọng |
| Trích dẫn căn cứ pháp lý hợp lệ | Kiểm tra link trích dẫn trỏ đúng văn bản/điều khoản | 100% |

### 3.6 Hiệu năng & trải nghiệm

| Metric | Ngưỡng đề xuất (theo NFR trong SRS) |
|---|---|
| Thời gian tóm tắt 1 văn bản ≤ 5 trang | ≤ 60 giây |
| Thời gian phản hồi câu hỏi | ≤ 5 giây (điều kiện demo) |
| Thời gian xử lý OCR + trích xuất | ≤ 60 giây |

---

## 4. QUY TRÌNH ĐÁNH GIÁ CON NGƯỜI (HUMAN EVALUATION)

Vì các chỉ số tự động (đặc biệt NLI) có thể chưa hoàn hảo với tiếng Việt, cần đối chiếu bằng đánh giá tay trên mẫu.

### 4.1 Rubric đánh giá Faithfulness thủ công

| Điểm | Mô tả |
|---|---|
| **Đạt** | Câu tóm tắt hoàn toàn được hỗ trợ bởi đoạn nguồn, không thêm/bớt ý quan trọng |
| **Đạt một phần** | Câu tóm tắt đúng ý chính nhưng diễn đạt gây hiểu nhầm nhẹ hoặc thiếu ngữ cảnh |
| **Không đạt** | Câu tóm tắt có thông tin không có trong nguồn, hoặc sai lệch ý nghĩa |

**Quy trình:** 2 thành viên **độc lập** đánh giá cùng một mẫu (khuyến nghị 10/20-30 văn bản test), sau đó so sánh kết quả với điểm NLI tự động để kiểm tra độ tin cậy của mô hình NLI. Nếu 2 người đánh giá lệch nhau nhiều → thảo luận thống nhất tiêu chí trước khi đánh giá tiếp phần còn lại.

### 4.2 Rubric đánh giá câu trả lời chatbot

| Điểm | Mô tả |
|---|---|
| **Đúng** | Trả lời chính xác, đầy đủ, trích dẫn đúng nguồn |
| **Một phần** | Trả lời đúng hướng nhưng thiếu chi tiết hoặc trích dẫn chưa tối ưu |
| **Sai** | Trả lời sai nội dung hoặc trích dẫn không liên quan |
| **Từ chối hợp lý** | Hệ thống từ chối trả lời vì không đủ căn cứ — tính là kết quả tốt nếu câu hỏi thực sự không có căn cứ |

---

## 5. TẬP DỮ LIỆU DÙNG ĐỂ ĐÁNH GIÁ

| Tập | Nguồn | Quy mô | Dùng để đo |
|---|---|---|---|
| Test set tóm tắt | 20-30 văn bản GD&ĐT (theo Kế hoạch Dữ liệu) | 20-30 văn bản | ROUGE, BERTScore, Faithfulness |
| Tập câu hỏi RAG | Câu hỏi thật từ cán bộ/giảng viên + nhóm tự soạn thêm, **có chủ đích chèn một số câu không có căn cứ trả lời** | Khuyến nghị ≥ 20 câu (trong đó ~5 câu "không có căn cứ" để test khả năng từ chối) | Answer Accuracy, Citation Validity, Refusal Rate |
| Tập văn bản có yêu cầu báo cáo | Trích từ 20-30 văn bản trên, lọc ra văn bản có yêu cầu báo cáo | Tùy thực tế thu thập được (dự kiến 3-5 văn bản) | Chất lượng khung báo cáo |

---

## 6. BẢNG TIÊU CHÍ NGHIỆM THU TỔNG HỢP (GO/NO-GO CHECKLIST)

| # | Tiêu chí | Đạt/Không đạt |
|---|---|---|
| 1 | Xử lý end-to-end thành công tối thiểu 20-25 văn bản thật | ☐ |
| 2 | ROUGE-L và BERTScore của mô hình chính cao hơn baseline TextRank | ☐ |
| 3 | Điểm Faithfulness trung bình đạt ngưỡng thống nhất với GVHD | ☐ |
| 4 | 100% câu tóm tắt hiển thị công khai có trích dẫn hợp lệ (không có ngoại lệ) | ☐ |
| 5 | Chatbot đạt ≥ 80% câu trả lời đúng trên tập test, 100% có trích dẫn hợp lệ | ☐ |
| 6 | Tỷ lệ từ chối đúng khi không đủ căn cứ ≥ 90% | ☐ |
| 7 | 100% khung báo cáo không chứa nội dung tự sinh ở mục Số liệu/Kết luận | ☐ |
| 8 | Hệ thống demo chạy được bằng Docker (một lệnh khởi động) | ☐ |
| 9 | Đánh giá con người (mẫu 10 văn bản) không phát hiện sai lệch nghiêm trọng so với điểm NLI tự động | ☐ |

> Đề xuất: sử dụng bảng này làm checklist duyệt cuối kỳ với GVHD trước khi báo cáo — đánh dấu Đạt/Không đạt kèm minh chứng số liệu cho từng dòng.

---

## 7. TÍCH HỢP ĐÁNH GIÁ VÀO CI/CD (REGRESSION CHECK)

Theo Tài liệu Kiến trúc (mục DevOps), mỗi lần merge code liên quan đến mô hình tóm tắt, pipeline CI sẽ:
1. Chạy script đánh giá tự động (ROUGE, BERTScore, Faithfulness) trên tập test cố định.
2. So sánh với kết quả baseline đã lưu (kết quả của lần merge trước).
3. Nếu điểm Faithfulness **giảm** so với baseline → cảnh báo, yêu cầu xem xét trước khi merge tiếp — tránh trường hợp một thay đổi nhỏ vô tình làm mô hình "bịa" nhiều hơn mà không ai phát hiện.

---

## 8. MẪU TRÌNH BÀY KẾT QUẢ TRONG BÁO CÁO ĐỒ ÁN

Khuyến nghị trình bày kết quả đánh giá trong báo cáo theo cấu trúc:
1. Bảng so sánh ROUGE/BERTScore: Baseline (TextRank) vs Mô hình chính (BARTpho/ViT5 fine-tune)
2. Biểu đồ phân phối điểm Faithfulness trên tập test (cho thấy phần lớn văn bản đạt ngưỡng cao)
3. Bảng ví dụ cụ thể: 1-2 trường hợp câu bị loại bỏ do faithfulness thấp — **kèm giải thích vì sao**, để minh chứng cơ chế hoạt động thật (không chỉ là số liệu trừu tượng)
4. Kết quả đánh giá con người đối chiếu với NLI tự động (bảng agreement)
5. Bảng Go/No-Go Checklist đã hoàn thành (mục 6 ở trên)

---

*Ngưỡng cụ thể (đặc biệt Faithfulness ≥ 90%) là con số đề xuất ban đầu — nên thống nhất chính thức với GVHD sau khi có kết quả thực nghiệm sơ bộ ở Sprint 3-4, vì ngưỡng quá cao có thể không khả thi với tài nguyên 12 tuần, còn ngưỡng quá thấp sẽ làm giảm giá trị của đồ án.*
