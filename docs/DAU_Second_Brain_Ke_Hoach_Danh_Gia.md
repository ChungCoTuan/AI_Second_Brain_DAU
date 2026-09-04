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
| 2 | **Độ trung thực (Faithfulness — 3 nhãn NLI)** | Bản tóm tắt/câu trả lời có bịa hay thiếu ý so với nguồn không? | UC-03, UC-04, UC-06 |
| 3 | Độ chính xác trích xuất thông tin (NER + chủ đề) | Số hiệu, ngày, cơ quan ban hành, chủ đề có đúng không? | UC-02, UC-09 |
| 4 | Chất lượng hỏi-đáp (RAG) | Chatbot trả lời đúng, có trích dẫn hợp lệ không? | UC-06 |
| 5 | Chất lượng gợi ý báo cáo (Template Library) | Khung báo cáo đúng cấu trúc riêng theo loại, không tự sinh nội dung? | UC-05 |
| 6 | Chất lượng "Cây văn bản" | Văn bản liên quan gợi ý ra có thực sự liên quan không? | UC-08 |
| 7 | Hiệu năng & trải nghiệm | Hệ thống phản hồi đủ nhanh, giao diện rõ ràng? | Toàn bộ |

> **Chiều số 2 (Faithfulness) là trọng tâm của đồ án** — các chiều còn lại quan trọng nhưng không phải điểm khác biệt chính.

---

## 3. CHI TIẾT TỪNG METRIC & NGƯỠNG ĐỀ XUẤT

### 3.1 Chất lượng tóm tắt

> **Cập nhật theo Phương án A (Kế hoạch Dữ liệu, mục 3):** không còn "mô hình fine-tune" — mô hình chính là **checkpoint BARTpho/ViT5 pretrained sẵn cho tóm tắt tiếng Việt**, dùng nguyên bản. Việc so sánh với baseline TextRank vẫn giữ nguyên ý nghĩa: chứng minh mô hình sinh câu mới (dù không tự huấn luyện) vẫn tốt hơn cách cắt-chọn câu có sẵn.

| Metric | Cách tính | Công cụ | Ngưỡng đề xuất |
|---|---|---|---|
| ROUGE-1, ROUGE-2 | Độ trùng khớp n-gram (1-gram, 2-gram) giữa tóm tắt sinh ra và gold summary | `rouge-score` (Python) | Mô hình chính (BARTpho/ViT5 **pretrained**) phải **vượt baseline TextRank** trên cùng tập test |
| ROUGE-L | Độ trùng khớp chuỗi con dài nhất | `rouge-score` | Tương tự trên |
| BERTScore | Độ tương đồng ngữ nghĩa qua embedding (bổ sung cho ROUGE vì không chỉ so khớp từ) | `bert-score` (dùng PhoBERT làm base) | Mô hình chính phải đạt điểm F1 BERTScore cao hơn baseline |
| **(Mới)** So sánh nhiều checkpoint pretrained | Nếu có từ 2 checkpoint pretrained trở lên khả dụng (ví dụ bản BARTpho gốc vs bản đã có ai đó fine-tune sẵn cho summarization công khai), chạy cả hai trên tập test, chọn checkpoint tốt nhất | `rouge-score`, `bert-score` | Không bắt buộc, nhưng nên làm nếu Sprint 2 còn dư thời gian — thay thế phần "huấn luyện" đã bị lược bỏ bằng phần "lựa chọn mô hình có căn cứ" |

> **Lưu ý quan trọng:** ROUGE/BERTScore chỉ đo *độ giống* với gold summary, **không đo được việc mô hình có bịa hay không** — đây là lý do bắt buộc phải có chỉ số Faithfulness riêng ở mục 3.2.

### 3.2 Độ trung thực (Faithfulness) — chỉ số quan trọng nhất

> **Cập nhật:** NLI giờ phân loại theo **3 nhãn rời rạc** (`entailment`/`contradiction`/`neutral`) thay vì chỉ đưa ra 1 điểm số liên tục — khớp với cơ chế human-in-the-loop ở UC-04.

| Metric | Cách tính | Công cụ | Ngưỡng đề xuất |
|---|---|---|---|
| Phân loại NLI (per câu) | Chạy mô hình NLI: đoạn nguồn là "premise", câu tóm tắt là "hypothesis" → phân loại 1 trong 3 nhãn | Mô hình NLI tiếng Việt (PhoBERT/XLM-R đã fine-tune cho NLI, dùng nguyên bản pretrained — không tự huấn luyện thêm trong 12 tuần) | Chỉ câu `entailment` được hiển thị công khai không qua rà soát |
| Tỷ lệ `entailment` (per văn bản) | % số câu trong bản tóm tắt được phân loại `entailment` | Tính trung bình trên toàn bộ câu của 1 văn bản | Trung bình toàn tập test **≥ 80%** *(đề xuất — cần thống nhất với GVHD)* |
| Tỷ lệ `contradiction` | % số câu bị phân loại mâu thuẫn với nguồn | Đếm log hệ thống | Theo dõi xu hướng — tỷ lệ quá cao (>20%) cho thấy mô hình pretrained hoạt động kém trên domain này, cần xem lại Phương án A/B (Kế hoạch Dữ liệu, mục 3) |
| Tỷ lệ `neutral` | % số câu không đủ căn cứ khẳng định đúng/sai | Đếm log hệ thống | Theo dõi, không có ngưỡng cứng — bản chất `neutral` ít nghiêm trọng hơn `contradiction` |
| **Document Publish Gate Correctness** *(mới)* | Kiểm tra: 100% văn bản có ≥1 câu `contradiction` phải ở trạng thái `pending_review`, không được `published`, tại mọi thời điểm trong suốt Sprint 3-6 | Truy vấn trực tiếp database, không tin giao diện | **Bắt buộc đạt 100%** — đây là ràng buộc an toàn cốt lõi, vi phạm là lỗi nghiêm trọng |
| Thời gian trung bình từ `pending_review` đến `published` | Đo thời gian cán bộ xử lý xong hàng đợi rà soát (UC-04) | Log hệ thống (ReviewLog) | Theo dõi — không để văn bản "treo" quá lâu ở trạng thái chờ (ảnh hưởng tính hữu dụng) |

### 3.3 Độ chính xác trích xuất thông tin (NER + Chủ đề)

| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Precision, Recall, F1 theo từng trường (số hiệu, ngày ban hành, cơ quan ban hành) | So khớp giá trị trích xuất với nhãn đã kiểm tra tay (theo Kế hoạch Dữ liệu mục 6.2) | F1 ≥ 0.85 cho các trường có format chuẩn (số hiệu, ngày); F1 ≥ 0.7 cho trường phức tạp hơn (yêu cầu báo cáo) |
| **(Mới)** Độ chính xác phân loại Chủ đề | % văn bản được gán đúng chủ đề, đối chiếu với nhãn tay (Kế hoạch Dữ liệu mục 6.4) | ≥ 85% trên tập test |
| **(Mới)** Độ chính xác nhãn Mức độ áp dụng cho trường | % văn bản được gán đúng 1 trong 3 mức (Áp dụng trực tiếp/Áp dụng chung/Tham khảo), đối chiếu nhãn tay | ≥ 75% — ngưỡng thấp hơn chủ đề vì đây là phân loại tinh tế hơn, phụ thuộc nhiều vào việc có văn bản nội bộ trường tương ứng hay không |

### 3.4 Chất lượng hỏi-đáp (RAG)

| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Tỷ lệ trả lời đúng (Answer Accuracy) | Đánh giá con người: câu trả lời có đúng nội dung không (Đúng/Sai/Một phần) | ≥ 80% "Đúng" trên tập câu hỏi test |
| Tỷ lệ trích dẫn hợp lệ (Citation Validity) | % câu trả lời có trích dẫn thực sự chứa thông tin hỗ trợ câu trả lời | 100% — **không có ngoại lệ**, vì trả lời không trích dẫn hợp lệ đồng nghĩa vi phạm yêu cầu cốt lõi |
| Tỷ lệ từ chối đúng (Correct Refusal Rate) | Trong các câu hỏi **không có căn cứ trả lời** (cố ý đưa vào tập test), % hệ thống từ chối đúng thay vì suy đoán | ≥ 90% |
| Tỷ lệ từ chối nhầm (False Refusal Rate) | Trong các câu hỏi **có căn cứ trả lời**, % hệ thống từ chối nhầm dù có đủ thông tin | Theo dõi, không để quá cao (ảnh hưởng tính hữu dụng) — mục tiêu ≤ 15% |

### 3.5 Chất lượng gợi ý khung báo cáo (Template Library)

| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Đúng cấu trúc yêu cầu | Đối chiếu thủ công: các đề mục có khớp với yêu cầu nêu trong văn bản gốc không | 100% trên tập test (vì đây là logic có kiểm soát, không phải sinh tự do) |
| **(Mới)** Đa dạng template | Số lượng cấu trúc đề mục **khác nhau rõ rệt** xuất hiện trên tập test có yêu cầu báo cáo | ≥ 2 template khác nhau — chứng minh không dùng chung 1 khung cho mọi văn bản (theo yêu cầu GVHD) |
| **(Mới)** Tỷ lệ khớp Template Library vs tự dựng khung | % văn bản dùng được template có sẵn so với % phải tự dựng khung từ đề mục gốc | Theo dõi — tỷ lệ tự dựng cao cho thấy Thư viện Template cần bổ sung thêm mẫu |
| Không có nội dung tự sinh ở phần Số liệu/Kết luận | Audit thủ công 100% các khung báo cáo sinh ra | **Bắt buộc đạt 100%** — vi phạm điều này là lỗi nghiêm trọng |
| Trích dẫn căn cứ pháp lý hợp lệ | Kiểm tra link trích dẫn trỏ đúng văn bản/điều khoản | 100% |

### 3.6 Chất lượng "Cây văn bản" (Document Relations)

| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Độ chính xác quan hệ tường minh (rule-based) | Với văn bản có quan hệ "căn cứ/thay thế/sửa đổi" thực sự tồn tại trong kho, % được hệ thống phát hiện đúng | ≥ 90% trên tập test — vì đây là rule-based, kỳ vọng độ chính xác cao |
| Độ liên quan của gợi ý ngữ nghĩa (Relevance@k) | Đánh giá con người: trong top-k văn bản gợi ý theo quan hệ ngữ nghĩa, bao nhiêu % thực sự liên quan | ≥ 70% — ngưỡng thấp hơn quan hệ tường minh vì bản chất là gợi ý "gần nghĩa", không tuyệt đối |
| Độ chính xác nhãn mức độ áp dụng | Xem mục 3.3 (đã gộp chung) | ≥ 75% |

### 3.7 Hiệu năng & trải nghiệm

| Metric | Ngưỡng đề xuất (theo NFR trong SRS) |
|---|---|
| Thời gian tóm tắt 1 văn bản ≤ 5 trang | ≤ 60 giây |
| Thời gian phản hồi câu hỏi | ≤ 5 giây (điều kiện demo) |
| Thời gian xử lý OCR + trích xuất | ≤ 60 giây |
| Tải danh sách "Cần rà soát" (UC-04) | ≤ 2 giây |
| Truy vấn văn bản liên quan — Cây văn bản (UC-08) | ≤ 3 giây |

---

## 4. QUY TRÌNH ĐÁNH GIÁ CON NGƯỜI (HUMAN EVALUATION)

Vì các chỉ số tự động (đặc biệt NLI) có thể chưa hoàn hảo với tiếng Việt, cần đối chiếu bằng đánh giá tay trên mẫu.

### 4.1 Rubric đánh giá Faithfulness thủ công

| Nhãn con người gán | Tương ứng nhãn NLI kỳ vọng | Mô tả |
|---|---|---|
| **Đạt** | `entailment` | Câu tóm tắt hoàn toàn được hỗ trợ bởi đoạn nguồn, không thêm/bớt ý quan trọng |
| **Mâu thuẫn** | `contradiction` | Câu tóm tắt có thông tin không có trong nguồn, hoặc sai lệch ý nghĩa |
| **Không rõ ràng** | `neutral` | Câu tóm tắt đúng ý chính nhưng diễn đạt gây hiểu nhầm nhẹ, thiếu ngữ cảnh, hoặc không đủ căn cứ khẳng định |

**Quy trình:** 2 thành viên **độc lập** đánh giá cùng một mẫu (khuyến nghị 10 văn bản trong tập test), gán 1 trong 3 nhãn trên cho từng câu, sau đó so sánh với nhãn mà mô hình NLI tự động đưa ra để tính **độ đồng thuận (agreement)** — nếu tỷ lệ đồng thuận thấp, đây là tín hiệu cho thấy ngưỡng/mô hình NLI cần xem lại trước khi tin tưởng hoàn toàn vào cơ chế publish gate. Nếu 2 người đánh giá lệch nhau nhiều → thảo luận thống nhất tiêu chí trước khi đánh giá tiếp phần còn lại.

### 4.2 Rubric đánh giá câu trả lời chatbot

| Điểm | Mô tả |
|---|---|
| **Đúng** | Trả lời chính xác, đầy đủ, trích dẫn đúng nguồn |
| **Một phần** | Trả lời đúng hướng nhưng thiếu chi tiết hoặc trích dẫn chưa tối ưu |
| **Sai** | Trả lời sai nội dung hoặc trích dẫn không liên quan |
| **Từ chối hợp lý** | Hệ thống từ chối trả lời vì không đủ căn cứ — tính là kết quả tốt nếu câu hỏi thực sự không có căn cứ |

### 4.3 Rubric đánh giá "Cây văn bản" (mới)

| Điểm | Mô tả |
|---|---|
| **Liên quan** | Văn bản được gợi ý thực sự cùng chủ đề/nội dung liên quan trực tiếp tới văn bản đang xem |
| **Liên quan một phần** | Có điểm chung nhưng khá xa (ví dụ cùng nhắc tới "đào tạo" nhưng khác cấp độ áp dụng) |
| **Không liên quan** | Gợi ý sai, không có mối liên hệ thực chất |

**Quy trình:** với mỗi văn bản trong tập test, 1 thành viên chấm top-3 kết quả "quan hệ ngữ nghĩa" theo rubric trên, dùng để tính Relevance@k ở mục 3.6.

---

## 5. TẬP DỮ LIỆU DÙNG ĐỂ ĐÁNH GIÁ

| Tập | Nguồn | Quy mô | Dùng để đo |
|---|---|---|---|
| Test set tóm tắt | 20-30 (khuyến nghị 30-40) văn bản chinhphu.vn + trường (theo Kế hoạch Dữ liệu, Phương án A — toàn bộ dùng cho đánh giá, không chia train) | 20-40 văn bản | ROUGE, BERTScore, Faithfulness (3 nhãn), NER, Chủ đề |
| Tập câu hỏi RAG | Câu hỏi thật từ cán bộ/giảng viên + nhóm tự soạn thêm, **có chủ đích chèn một số câu không có căn cứ trả lời** | Khuyến nghị ≥ 20 câu (trong đó ~5 câu "không có căn cứ" để test khả năng từ chối) | Answer Accuracy, Citation Validity, Refusal Rate |
| Tập văn bản có yêu cầu báo cáo | Trích từ tập trên, lọc ra văn bản có yêu cầu báo cáo | Tùy thực tế thu thập được (dự kiến 3-5 văn bản, cần đa dạng loại để kiểm tra Template Library) | Chất lượng khung báo cáo, đa dạng template |
| **(Mới)** Tập cặp văn bản có quan hệ đã biết | Chọn ra trong tập trên các cặp văn bản có quan hệ "căn cứ/thay thế" đã xác nhận bằng tay | Tùy thực tế (dự kiến 5-10 cặp) | Độ chính xác quan hệ tường minh, Relevance@k |

---

## 6. BẢNG TIÊU CHÍ NGHIỆM THU TỔNG HỢP (GO/NO-GO CHECKLIST)

| # | Tiêu chí | Đạt/Không đạt |
|---|---|---|
| 1 | Xử lý end-to-end thành công tối thiểu 20-25 văn bản thật từ chinhphu.vn + trường | ☐ |
| 2 | ROUGE-L và BERTScore của mô hình chính (pretrained) cao hơn baseline TextRank | ☐ |
| 3 | Tỷ lệ `entailment` trung bình đạt ngưỡng thống nhất với GVHD | ☐ |
| 4 | 100% câu tóm tắt hiển thị công khai có trích dẫn hợp lệ (không có ngoại lệ) | ☐ |
| 5 | **100% văn bản có câu `contradiction` bị giữ ở trạng thái `pending_review`, không tự động `published`** (Document Publish Gate Correctness) | ☐ |
| 6 | Chatbot đạt ≥ 80% câu trả lời đúng trên tập test, 100% có trích dẫn hợp lệ, chỉ dựa trên văn bản `published` | ☐ |
| 7 | Tỷ lệ từ chối đúng khi không đủ căn cứ ≥ 90% | ☐ |
| 8 | 100% khung báo cáo không chứa nội dung tự sinh ở mục Số liệu/Kết luận | ☐ |
| 9 | Tối thiểu 2 template báo cáo khác nhau rõ rệt xuất hiện trong tập test | ☐ |
| 10 | Độ chính xác phân loại chủ đề ≥ 85% trên tập test | ☐ |
| 11 | Quan hệ tường minh (Cây văn bản) phát hiện đúng ≥ 90% trường hợp đã biết | ☐ |
| 12 | Hệ thống demo chạy được bằng Docker (một lệnh khởi động) | ☐ |
| 13 | Đánh giá con người (mẫu 10 văn bản) không phát hiện sai lệch nghiêm trọng so với nhãn NLI tự động | ☐ |

> Đề xuất: sử dụng bảng này làm checklist duyệt cuối kỳ với GVHD trước khi báo cáo — đánh dấu Đạt/Không đạt kèm minh chứng số liệu cho từng dòng.

---

## 7. TÍCH HỢP ĐÁNH GIÁ VÀO CI/CD (REGRESSION CHECK)

Theo Tài liệu Kiến trúc (mục DevOps), mỗi lần merge code liên quan đến pipeline tóm tắt/NLI, pipeline CI sẽ:
1. Chạy script đánh giá tự động (ROUGE, BERTScore, phân phối 3 nhãn NLI) trên tập test cố định.
2. So sánh với kết quả baseline đã lưu (kết quả của lần merge trước).
3. Nếu tỷ lệ `entailment` **giảm** hoặc tỷ lệ `contradiction` **tăng** so với baseline → cảnh báo, yêu cầu xem xét trước khi merge tiếp — tránh trường hợp một thay đổi nhỏ vô tình làm mô hình "bịa" nhiều hơn mà không ai phát hiện.
4. **(Mới)** Pin rõ phiên bản checkpoint pretrained đang dùng (ví dụ `bartpho-summary-v1` cụ thể) trong file cấu hình — vì Phương án A không tự huấn luyện, thay đổi version checkpoint là thay đổi đáng kể cần chạy lại toàn bộ đánh giá, không chỉ regression check thông thường.

---

## 8. MẪU TRÌNH BÀY KẾT QUẢ TRONG BÁO CÁO ĐỒ ÁN

Khuyến nghị trình bày kết quả đánh giá trong báo cáo theo cấu trúc:
1. Bảng so sánh ROUGE/BERTScore: Baseline (TextRank) vs Mô hình chính (BARTpho/ViT5 **pretrained**, không fine-tune — nêu rõ lý do ở phần Cơ sở lý thuyết/Phương pháp)
2. Biểu đồ phân phối 3 nhãn NLI (`entailment`/`contradiction`/`neutral`) trên tập test — thay cho biểu đồ phân phối điểm liên tục trước đây
3. Bảng ví dụ cụ thể: 1-2 trường hợp câu bị gắn `contradiction`, kèm cách cán bộ xử lý ở UC-04 — để minh chứng cơ chế human-in-the-loop hoạt động thật (không chỉ là số liệu trừu tượng)
4. Kết quả đánh giá con người đối chiếu với nhãn NLI tự động (bảng agreement)
5. Bảng kết quả "Cây văn bản" (Relevance@k) và độ chính xác phân loại chủ đề
6. Bảng Go/No-Go Checklist đã hoàn thành (mục 6 ở trên)

---

*Ngưỡng cụ thể (đặc biệt tỷ lệ `entailment` ≥ 80%) là con số đề xuất ban đầu — nên thống nhất chính thức với GVHD sau khi có kết quả thực nghiệm sơ bộ ở Sprint 2-3, vì ngưỡng quá cao có thể không khả thi khi dùng mô hình pretrained không fine-tune riêng cho domain này, còn ngưỡng quá thấp sẽ làm giảm giá trị của đồ án.*
