# ĐỀ CƯƠNG CHI TIẾT ĐỒ ÁN

## Hệ thống Tóm tắt & Tra cứu Văn bản Thông minh có Trích dẫn — "DAU Second Brain"

| | |
|---|---|
| **Loại đồ án** | Đồ án môn Trí tuệ Nhân tạo |
| **Lĩnh vực** | Xử lý ngôn ngữ tự nhiên (NLP) — Tóm tắt văn bản có căn cứ (Grounded Summarization) |
| **Nhóm thực hiện** | 2 sinh viên |
| **Thời gian thực hiện** | 12 tuần |
| **Đơn vị áp dụng** | Trường Đại học Kiến trúc (Phòng Đào tạo, Giảng viên) |

---

## 1. LÝ DO CHỌN ĐỀ TÀI

### 1.1 Vấn đề chung
Khối lượng văn bản mà một trường đại học phải xử lý mỗi ngày ngày càng lớn: thông tư, quyết định, công văn từ Bộ Giáo dục và Đào tạo; kèm theo tài liệu giảng dạy nội bộ. Cán bộ phòng đào tạo và giảng viên phải tự đọc, tự nhớ, tự tra cứu thủ công — dễ bỏ sót thông tin, nhầm lẫn văn bản đã hết hiệu lực, và tốn nhiều thời gian mỗi khi cần lập báo cáo theo yêu cầu.

### 1.2 Khoảng trống hiện tại
Các công cụ tóm tắt phổ biến hiện nay chủ yếu tối ưu cho tiếng Anh, khi áp dụng cho tiếng Việt thường cho kết quả kém tự nhiên hoặc bỏ sót ý quan trọng. Quan trọng hơn, các công cụ AI tạo sinh nói chung (kể cả các mô hình ngôn ngữ lớn) đều có nguy cơ **hallucination** — tự "bịa" ra thông tin không có trong nguồn — điều này **không được phép xảy ra** với văn bản hành chính/pháp quy, vì sai lệch có thể dẫn đến hiểu sai quy định và hậu quả thực tế.

### 1.3 Vì sao cần giải pháp AI
Tóm tắt thủ công không thể mở rộng quy mô khi số lượng văn bản lớn. Phương pháp rule-based đơn giản (ví dụ lấy câu đầu đoạn) không hiểu ngữ nghĩa, dễ bỏ sót ý quan trọng. Mô hình học sâu hiện đại (BARTpho, ViT5) có khả năng hiểu ngữ cảnh và tóm tắt tự nhiên hơn — nhưng cần được **kiểm soát chặt để đảm bảo tính trung thực**, đây chính là trọng tâm kỹ thuật của đồ án.

### 1.4 Phát biểu bài toán
> Xây dựng hệ thống tự động tóm tắt văn bản tiếng Việt có khả năng rút gọn nội dung dài thành bản tóm tắt ngắn gọn, **mỗi câu tóm tắt đều có trích dẫn kiểm chứng được về nguồn gốc**, đồng thời hỗ trợ gợi ý khung báo cáo và tra cứu ngữ nghĩa, nhằm giúp Phòng Đào tạo và giảng viên tiết kiệm thời gian tiếp cận và xử lý thông tin.

---

## 2. MỤC TIÊU ĐỀ TÀI

### 2.1 Mục tiêu tổng quát
Xây dựng một hệ thống AI hỗ trợ quản lý tri thức cho trường đại học, tập trung vào văn bản pháp quy giáo dục, với đặc điểm nổi bật là **khả năng chống bịa đặt thông tin (grounded/attributed generation)**.

### 2.2 Mục tiêu cụ thể

| # | Mục tiêu | Thước đo dự kiến |
|---|---|---|
| 1 | Tóm tắt tự động văn bản tiếng Việt, có trích dẫn theo từng câu | ROUGE-L, BERTScore so với baseline extractive |
| 2 | Đảm bảo tính trung thực của bản tóm tắt (không bịa, không thiếu ý quan trọng) | Điểm Faithfulness (qua kiểm tra NLI) ≥ ngưỡng đề ra |
| 3 | Trích xuất thông tin có cấu trúc từ văn bản (số hiệu, ngày ban hành, yêu cầu báo cáo...) | Độ chính xác (F1) của mô hình NER |
| 4 | Gợi ý khung báo cáo cho giảng viên dựa trên yêu cầu trong văn bản, không tự sinh số liệu | Tỷ lệ khung báo cáo đúng cấu trúc yêu cầu |
| 5 | Tra cứu ngữ nghĩa và hỏi-đáp (chatbot) có trích dẫn trên toàn bộ kho văn bản | Tỷ lệ câu trả lời đúng & có trích dẫn hợp lệ |

---

## 3. ĐỐI TƯỢNG VÀ PHẠM VI

### 3.1 Đối tượng sử dụng
- **Cán bộ Phòng Đào tạo** — quản trị nội dung, tra cứu văn bản hiện hành
- **Giảng viên** — nhận gợi ý khung báo cáo, tra cứu quy định liên quan
- **Sinh viên** (định hướng mở rộng) — tra cứu quy định học tập

### 3.2 Phạm vi thực hiện (trong 12 tuần)

**Trong phạm vi:**
- Thu thập và xử lý văn bản pháp quy (thông tư/quyết định/công văn của Bộ GD&ĐT) và tài liệu giảng dạy cơ bản
- Tóm tắt có trích dẫn, kiểm tra độ trung thực bằng mô hình NLI
- Trích xuất thông tin có cấu trúc (NER) và phân loại văn bản
- Gợi ý khung báo cáo (không tự sinh nội dung/số liệu thực tế)
- Tra cứu ngữ nghĩa và chatbot hỏi-đáp có trích dẫn
- Dashboard demo (web) cho toàn bộ luồng trên

**Ngoài phạm vi (định hướng phát triển tương lai):**
- Quản lý vòng đời văn bản (theo dõi quan hệ thay thế/sửa đổi giữa các văn bản)
- Chuyển giọng nói thành văn bản (speech-to-text) cho bài giảng ghi âm
- Ứng dụng di động
- Tích hợp trực tiếp với hệ thống quản lý đào tạo (LMS/SIS) hiện có của trường

> Lý do thu hẹp phạm vi: với nhóm 2 người và 12 tuần, việc giữ trọng tâm vào cơ chế **tóm tắt có trích dẫn đáng tin cậy** — phần khó và có giá trị học thuật cao nhất — quan trọng hơn việc dàn trải nhiều tính năng nhưng làm nông.

---

## 4. PHƯƠNG PHÁP THỰC HIỆN (TỔNG QUAN)

Hệ thống được xây dựng theo pipeline 5 bước: **Thu thập → Trích xuất & Phân loại → Tóm tắt có trích dẫn → Gợi ý báo cáo / Tra cứu → Giao diện người dùng**.

Các mô hình/kỹ thuật AI chính sẽ sử dụng:
- **TextRank** — baseline tóm tắt trích xuất (extractive)
- **BARTpho / ViT5** (fine-tune) — mô hình tóm tắt sinh câu mới (abstractive), giới hạn ngữ cảnh theo đoạn đã chọn để giảm nguy cơ bịa
- **PhoBERT + CRF** — trích xuất thông tin có cấu trúc (NER)
- **Mô hình NLI** — kiểm tra từng câu tóm tắt có được suy ra từ đoạn nguồn không (cơ chế chống hallucination)
- **Embedding + Vector Search (FAISS/Chroma)** — phục vụ tra cứu ngữ nghĩa và chatbot RAG

*(Chi tiết kiến trúc kỹ thuật được trình bày đầy đủ trong Tài liệu Đặc tả Nghiệp vụ & Kiến trúc kèm theo.)*

---

## 5. KẾT QUẢ DỰ KIẾN (SẢN PHẨM BÀN GIAO)

1. Hệ thống demo chạy được end-to-end (đóng gói bằng Docker), gồm:
   - Dashboard tra cứu & hỏi-đáp có trích dẫn
   - Màn hình quản trị nạp và theo dõi xử lý văn bản
   - Chức năng xuất khung báo cáo gợi ý (file Word)
   - Màn hình đối chiếu trích dẫn (minh chứng cơ chế chống bịa đặt)
2. Bộ dữ liệu đã xử lý: tối thiểu 20-25 văn bản thật từ Bộ GD&ĐT
3. Báo cáo đồ án đầy đủ, kèm kết quả đánh giá định lượng (ROUGE, BERTScore, Faithfulness)
4. Mã nguồn và tài liệu kỹ thuật trên Git

---

## 6. KẾ HOẠCH THỰC HIỆN TỔNG QUÁT (12 TUẦN)

| Giai đoạn | Tuần | Nội dung chính |
|---|---|---|
| Chuẩn bị | 1–2 | Thu thập dữ liệu mẫu, thiết kế kiến trúc & data model |
| Xây dựng nền tảng | 3–6 | Ingestion, trích xuất/phân loại/NER, bắt đầu fine-tune mô hình tóm tắt |
| Xây dựng phần lõi | 7–8 | Tích hợp kiểm tra faithfulness (NLI) + cơ chế trích dẫn — trọng tâm kỹ thuật |
| Mở rộng tính năng | 9–10 | Gợi ý khung báo cáo, tra cứu ngữ nghĩa & chatbot RAG |
| Hoàn thiện | 11 | Ghép nối toàn bộ pipeline, hoàn thiện dashboard |
| Đánh giá & Báo cáo | 12 | Đánh giá định lượng, viết báo cáo, chuẩn bị demo |

*(Kế hoạch sprint chi tiết theo Scrum, phân công theo 2 track song song, được trình bày trong Tài liệu Đặc tả Nghiệp vụ & Kiến trúc.)*

---

## 7. Ý NGHĨA KHOA HỌC VÀ THỰC TIỄN

**Về mặt khoa học:** đề tài tiếp cận trực diện vấn đề hallucination trong mô hình sinh văn bản — một trong những thách thức lớn nhất của NLP hiện đại — áp dụng cụ thể cho tiếng Việt và văn bản hành chính, lĩnh vực còn ít công cụ hỗ trợ tốt.

**Về mặt thực tiễn:** giải quyết đúng nhu cầu có thật của Phòng Đào tạo và giảng viên: tra cứu nhanh, không bỏ sót văn bản, tiết kiệm thời gian soạn báo cáo — có khả năng triển khai thực tế nếu được đầu tư tiếp sau đồ án.

---

## 8. CÂU HỎI XIN Ý KIẾN GVHD

*(Phần này nên giữ lại khi gửi đề cương — giúp buổi duyệt đề cương có trọng tâm, tránh trao đổi chung chung.)*

1. Phạm vi 12 tuần đã liệt kê ở mục 3.2 có phù hợp với kỳ vọng của thầy/cô không, hay cần điều chỉnh thêm/bớt?
2. Nguồn dữ liệu văn bản thật (dự kiến lấy từ moet.gov.vn và văn bản nội bộ trường) có cần thầy/cô hỗ trợ tiếp cận thêm nguồn nào không?
3. Ngưỡng đánh giá "đạt yêu cầu" cho điểm Faithfulness — thầy/cô có con số cụ thể mong muốn, hay nhóm được tự đề xuất dựa trên thực nghiệm?
