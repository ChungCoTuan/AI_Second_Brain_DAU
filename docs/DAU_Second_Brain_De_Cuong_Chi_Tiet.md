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
| 2 | Đảm bảo tính trung thực của bản tóm tắt (không bịa, không thiếu ý quan trọng) | Điểm Faithfulness (qua kiểm tra NLI **3 nhãn**) ≥ ngưỡng đề ra |
| 3 | Trích xuất thông tin có cấu trúc từ văn bản (số hiệu, ngày ban hành, yêu cầu báo cáo...) và **phân loại chủ đề/lĩnh vực** theo danh mục cố định | Độ chính xác (F1) của mô hình NER; độ chính xác phân loại chủ đề ≥ 85% trên tập test |
| 4 | Gợi ý khung báo cáo cho giảng viên, **mỗi loại văn bản có template riêng** từ Thư viện Template, không tự sinh số liệu | Tỷ lệ khung báo cáo đúng cấu trúc; ≥ 2 template khác nhau rõ rệt trên tập test |
| 5 | Tra cứu ngữ nghĩa và hỏi-đáp (chatbot) có trích dẫn, **chỉ trên văn bản đã `published`** | Tỷ lệ câu trả lời đúng & có trích dẫn hợp lệ; không dùng văn bản `pending_review` |
| 6 | **Cơ chế rà soát & duyệt (Review Service)** — cán bộ kiểm tra câu bị NLI gắn nhãn `contradiction`/`neutral`, có audit trail đầy đủ | 100% văn bản có câu `contradiction` không được `published` trước khi rà soát xong |
| 7 | **Cây văn bản** — hiển thị văn bản liên quan (quan hệ tường minh + ngữ nghĩa) và mức độ áp dụng đối với trường | ≥ 80% văn bản có văn bản liên quan thực sự tìm được trong kho; quan hệ tường minh phát hiện ≥ 90% trường hợp |
| 8 | **Dashboard theo chủ đề** — cán bộ duyệt văn bản theo nhóm chủ đề thay vì danh sách hàng đợi phẳng | Văn bản được nhóm đúng chủ đề ≥ 85% trường hợp trên tập test |

---

## 3. ĐỐI TƯỢNG VÀ PHẠM VI

### 3.1 Đối tượng sử dụng
- **Cán bộ Phòng Đào tạo** — quản trị nội dung, tra cứu văn bản hiện hành
- **Giảng viên** — nhận gợi ý khung báo cáo, tra cứu quy định liên quan
- **Sinh viên** (định hướng mở rộng) — tra cứu quy định học tập

### 3.2 Phạm vi thực hiện (trong 12 tuần)

**Trong phạm vi:**
- Thu thập và xử lý văn bản pháp quy từ **Cổng Thông tin điện tử Chính phủ (chinhphu.vn) và tài liệu liên quan trực tiếp tới trường** (không dùng dataset công khai ngoài ngành)
- Tóm tắt có trích dẫn, kiểm tra độ trung thực bằng mô hình **NLI 3 nhãn** (entailment/contradiction/neutral)
- **Review Service** — cơ chế rà soát & duyệt (Human-in-the-loop), gồm Publish Gate và audit trail đầy đủ
- Trích xuất thông tin có cấu trúc (NER) và **phân loại văn bản theo loại + chủ đề**
- Gợi ý khung báo cáo theo **Thư viện Template** (mỗi loại văn bản có template riêng — không dùng 1 khuôn chung) — không tự sinh nội dung/số liệu thực tế
- Tra cứu ngữ nghĩa và chatbot hỏi-đáp có trích dẫn (chỉ trên văn bản `published`)
- **Cây văn bản** (phạm vi rút gọn) — hiển thị văn bản liên quan (quan hệ tường minh + ngữ nghĩa), mức độ áp dụng cho trường; tái sử dụng hạ tầng embedding đã xây
- **Dashboard theo chủ đề** — cán bộ duyệt văn bản theo nhóm chủ đề (thống kê, quản lý)
- Dashboard demo (web) cho toàn bộ luồng trên

**Ngoài phạm vi (định hướng phát triển tương lai):**
- **Quản lý vòng đời văn bản đầy đủ** (cảnh báo tự động khi văn bản hết hiệu lực, quy trình phê duyệt thay thế có kiểm duyệt) — Cây văn bản (hiển thị quan hệ) và quản lý vòng đời đầy đủ là 2 khái niệm khác nhau
- Chuyển giọng nói thành văn bản (speech-to-text) cho bài giảng ghi âm
- Ứng dụng di động
- Tích hợp trực tiếp với hệ thống quản lý đào tạo (LMS/SIS) hiện có của trường

> Lý do thu hẹp phạm vi: với nhóm 2 người và 12 tuần, việc giữ trọng tâm vào cơ chế **tóm tắt có trích dẫn đáng tin cậy + Review Service an toàn** — phần khó và có giá trị học thuật cao nhất — quan trọng hơn việc dàn trải nhiều tính năng nhưng làm nông.

---

## 4. PHƯƠNG PHÁP THỰC HIỆN (TỔNG QUAN)

Hệ thống được xây dựng theo pipeline 5 bước: **Thu thập → Trích xuất & Phân loại → Tóm tắt có trích dẫn → Gợi ý báo cáo / Tra cứu → Giao diện người dùng**.

Các mô hình/kỹ thuật AI chính sẽ sử dụng:
- **TextRank** — baseline tóm tắt trích xuất (extractive); chọn đoạn quan trọng làm ngữ cảnh giới hạn cho bước abstractive
- **BARTpho / ViT5** (pretrained checkpoint sẵn có, **không fine-tune từ đầu** do nguồn dữ liệu giới hạn) — mô hình tóm tắt sinh câu mới (abstractive), giới hạn ngữ cảnh theo đoạn đã chọn để giảm nguy cơ bịa
- **PhoBERT + CRF** — trích xuất thông tin có cấu trúc (NER)
- **Mô hình NLI (3 nhãn: entailment/contradiction/neutral)** — kiểm tra từng câu tóm tắt; câu `contradiction` kích hoạt Publish Gate chặn toàn bộ văn bản cho tới khi cán bộ rà soát xong
- **Embedding + Vector Search (FAISS/Chroma)** — phục vụ tra cứu ngữ nghĩa, chatbot RAG, và **Cây văn bản** (tái sử dụng cùng hạ tầng)
- **Rule-based / Regex** — phát hiện quan hệ tường minh giữa các văn bản (phục vụ Cây văn bản)
- **Classification model** — phân loại loại văn bản và chủ đề/lĩnh vực (phục vụ Dashboard theo chủ đề)

### Phân quyền truy cập API
*Ghi chú: Phân quyền truy cập áp dụng cả cho việc xem file gốc (API `GET /documents/{id}/file`), không chỉ nội dung tóm tắt — quan trọng nếu sau này có văn bản nội bộ nhạy cảm.*

*(Chi tiết kiến trúc kỹ thuật được trình bày đầy đủ trong Tài liệu Đặc tả Nghiệp vụ & Kiến trúc kèm theo.)*

---

## 5. KẾT QUẢ DỰ KIẾN (SẢN PHẨM BÀN GIAO)

1. Hệ thống demo chạy được end-to-end (đóng gói bằng Docker), gồm:
   - Dashboard tra cứu & hỏi-đáp có trích dẫn
   - Màn hình quản trị nạp và theo dõi xử lý văn bản; **Dashboard theo chủ đề** nhóm văn bản theo lĩnh vực
   - Chức năng **rà soát & duyệt (Review Service)**: hiển thị câu bị gắn cờ đặt cạnh đoạn gốc, thao tác Duyệt/Sửa/Loại bỏ, audit trail đầy đủ
   - Chức năng xuất khung báo cáo gợi ý (file Word) theo đúng template tương ứng
   - Màn hình đối chiếu trích dẫn (minh chứng cơ chế chống bịa đặt)
   - Tính năng **Cây văn bản** (hiển thị văn bản liên quan + mức độ áp dụng cho trường)
2. Bộ dữ liệu đã xử lý: tối thiểu 20-25 văn bản thật từ **chinhphu.vn và tài liệu liên quan tới trường**
3. Báo cáo đồ án đầy đủ, kèm kết quả đánh giá định lượng (ROUGE, BERTScore, Faithfulness)
4. Mã nguồn và tài liệu kỹ thuật trên Git

---

## 6. KẾ HOẠCH THỰC HIỆN TỔNG QUÁT (12 TUẦN)

| Giai đoạn | Tuần | Nội dung chính |
|---|---|---|
| Chuẩn bị | 1–2 | Thu thập dữ liệu mẫu (**chinhphu.vn + tài liệu trường**), thiết kế kiến trúc & data model |
| Xây dựng nền tảng | 3–6 | Ingestion, Trích xuất/Phân loại **loại + chủ đề**/NER, chuẩn bị checkpoint BARTpho/ViT5 |
| Xây dựng phần lõi | 7–8 | Tích hợp NLI **3 nhãn** + cơ chế trích dẫn + **Review Service (Publish Gate, audit trail)** — trọng tâm kỹ thuật |
| Mở rộng tính năng | 9–10 | Gợi ý khung báo cáo **theo Thư viện Template**, tra cứu ngữ nghĩa & chatbot RAG, **Cây văn bản** |
| Hoàn thiện | 11 | Ghép nối toàn bộ pipeline, hoàn thiện dashboard (kể cả Dashboard theo chủ đề + hiển thị Cây văn bản) |
| Đánh giá & Báo cáo | 12 | Đánh giá định lượng, viết báo cáo, chuẩn bị demo |

*(Kế hoạch sprint chi tiết theo Scrum, phân công theo 2 track song song, được trình bày trong Tài liệu Đặc tả Nghiệp vụ & Kiến trúc.)*

---

## 7. Ý NGHĨA KHOA HỌC VÀ THỰC TIỄN

**Về mặt khoa học:** đề tài tiếp cận trực diện vấn đề hallucination trong mô hình sinh văn bản — một trong những thách thức lớn nhất của NLP hiện đại — áp dụng cụ thể cho tiếng Việt và văn bản hành chính, lĩnh vực còn ít công cụ hỗ trợ tốt. Cơ chế NLI 3 nhãn + Review Service đóng góp thêm góc độ **human-in-the-loop** vào bài toán grounded summarization tiếng Việt.

**Về mặt thực tiễn:** giải quyết đúng nhu cầu có thật của Phòng Đào tạo và giảng viên: tra cứu nhanh theo chủ đề, không bỏ sót văn bản, tiết kiệm thời gian soạn báo cáo, nắm bắt quan hệ giữa các văn bản — có khả năng triển khai thực tế nếu được đầu tư tiếp sau đồ án.

---

## 8. CÂU HỎI XIN Ý KIẾN GVHD

*(Phần này nên giữ lại khi gửi đề cương — giúp buổi duyệt đề cương có trọng tâm, tránh trao đổi chung chung.)*

1. Phạm vi 12 tuần đã liệt kê ở mục 3.2 có phù hợp với kỳ vọng của thầy/cô không, hay cần điều chỉnh thêm/bớt?
2. Nguồn dữ liệu văn bản thật (chinhphu.vn + tài liệu nội bộ trường) có cần thầy/cô hỗ trợ tiếp cận thêm không?
3. Ngưỡng đánh giá "đạt yêu cầu" cho điểm Faithfulness — thầy/cô có con số cụ thể mong muốn, hay nhóm được tự đề xuất dựa trên thực nghiệm?

