**CÁC THUẬT TOÁN CHÍNH**

**Nhóm 1 — Trích xuất & Phân loại thông tin**

- **TF-IDF (Term Frequency – Inverse Document Frequency)**
  - **Định nghĩa:** Đo mức độ "đặc trưng" của một từ trong một văn bản, bằng cách nhân tần suất từ đó xuất hiện trong văn bản (TF) với nghịch đảo số văn bản chứa từ đó trong toàn bộ tập dữ liệu (IDF). Từ xuất hiện nhiều trong 1 văn bản nhưng hiếm ở các văn bản khác sẽ có điểm cao.
  - **Hình dung thực tế:** Giống việc tìm "từ khóa riêng" của một cuốn sách trong cả thư viện. Các từ như "và", "là", "của" xuất hiện ở mọi cuốn sách nên vô giá trị để phân biệt. Nhưng từ "tín chỉ" chỉ xuất hiện dày đặc ở nhóm văn bản về đào tạo — đó chính là "dấu vân tay" giúp máy nhận ra chủ đề.

- **Classification model (phân loại văn bản)**
  - **Định nghĩa:** Bài toán học có giám sát — đưa vector biểu diễn văn bản qua một lớp phân loại để dự đoán xác suất văn bản thuộc mỗi nhãn (thông tư/quyết định/công văn/giáo trình), chọn nhãn có xác suất cao nhất.
  - **Hình dung thực tế:** Giống nhân viên bưu điện phân loại thư ngay khi vừa nhận: chỉ cần liếc qua tiêu đề, con dấu, cách trình bày là đoán ngay đây là "hóa đơn" hay "công văn nhà nước" — không cần đọc hết nội dung.

- **PhoBERT + CRF (NER — nhận diện thực thể)**
  - **Định nghĩa:** PhoBERT đọc câu theo cả 2 chiều để hiểu ngữ cảnh của từng từ (ví dụ phân biệt số "5" trong "Điều 5" với "5" trong "ngày 5 tháng 3"). Lớp CRF phía sau đảm bảo các nhãn liền kề nhất quán — một cụm ngày tháng phải được gán nhãn liên tục, không ngắt quãng vô lý.
  - **Hình dung thực tế:** Giống dùng bút highlight nhiều màu tô văn bản: vàng cho ngày tháng, xanh cho tên cơ quan, hồng cho số hiệu. PhoBERT là "người đọc hiểu ngữ cảnh" để biết tô màu gì, còn CRF là "người tô cẩn thận" — đã bắt đầu tô 1 cụm thì tô liền mạch hết cụm đó.

**Nhóm 2 — Tóm tắt văn bản (lõi của đồ án)**

- **TextRank**
  - **Định nghĩa:** Thuật toán xếp hạng dựa trên đồ thị, lấy cảm hứng từ PageRank của Google. Mỗi câu là một đỉnh, cạnh nối giữa 2 câu có trọng số bằng độ tương đồng nội dung. Câu nào "được nhiều câu khác giống ý" thì điểm càng cao, top câu điểm cao nhất được chọn làm tóm tắt.
  - **Hình dung thực tế:** Giống cách xác định "người có ảnh hưởng nhất lớp": nếu một bạn liên tục được các bạn khác nhắc tới, đồng tình, trích dẫn ý kiến — bạn đó trở nên "trung tâm". TextRank áp dụng y hệt logic đó cho câu văn: câu nào là "tâm điểm" mà các câu khác đều xoay quanh thì được chọn.

- **BARTpho / ViT5 (mô hình tóm tắt sinh câu mới — Transformer Seq2Seq)**
  - **Định nghĩa:** Kiến trúc encoder-decoder. Encoder đọc toàn bộ đoạn văn, dùng cơ chế self-attention để mỗi từ "chú ý" tới các từ khác nhằm hiểu ngữ cảnh. Decoder sinh từng từ của câu tóm tắt, mỗi bước vừa nhìn lại đoạn gốc (cross-attention) vừa nhìn các từ đã sinh trước đó để đảm bảo mạch lạc.
  - **Hình dung thực tế:** Giống nhờ một trợ lý đọc hết bản báo cáo dài (encoder = đọc hiểu), rồi tự viết lại bằng lời văn của chính mình thành bản ngắn gọn (decoder = viết lại), chứ không chỉ cắt-dán vài câu có sẵn như TextRank. Cơ chế "attention" giống việc trợ lý luôn liếc lại đúng đoạn liên quan trong tài liệu gốc khi viết, để không viết sai từ trí nhớ mang máng.

- **Mô hình NLI (kiểm tra Faithfulness — cơ chế chống bịa đặt)**
  - **Định nghĩa:** Bài toán phân loại quan hệ giữa "premise" (đoạn văn gốc) và "hypothesis" (câu tóm tắt) thành **1 trong 3 nhãn**: `Entailment` (câu suy ra được từ nguồn), `Contradiction` (câu mâu thuẫn với nguồn), `Neutral` (không đủ căn cứ để khẳng định đúng/sai). Câu `Entailment` được giữ lại kèm trích dẫn; câu `Contradiction` bị gắn cờ ưu tiên cao nhất và **chặn toàn bộ văn bản khỏi trạng thái `published`** cho tới khi cán bộ rà soát xong (Publish Gate); câu `Neutral` gắn cờ cảnh báo mức thấp hơn.
  - **Hình dung thực tế:** Giống giáo viên chấm bài "đúng/sai dựa trên đoạn văn cho sẵn": học sinh (mô hình tóm tắt) viết một câu, giáo viên (mô hình NLI) đọc lại đoạn gốc và phân loại — "suy ra được" (Entailment: cho qua), "mâu thuẫn rõ ràng" (Contradiction: gạch đỏ, cả bài chưa được nộp), "không rõ đúng sai" (Neutral: gạch vàng, cảnh báo thêm). Cả bài chỉ được công nhận khi không còn chỗ nào bị gạch đỏ.

**Nhóm 3 — Tra cứu ngữ nghĩa (RAG)**

- **Embedding + Vector Search (FAISS/Chroma)**
  - **Định nghĩa:** Embedding chuyển văn bản thành vector số nhiều chiều sao cho các đoạn có ý nghĩa gần nhau thì vector cũng nằm gần nhau trong không gian đó. Vector Search là công cụ lưu trữ và tìm kiếm nhanh trong hàng nghìn vector này, để khi có câu hỏi mới, hệ thống tìm ra ngay các đoạn có vector gần nhất — tức liên quan về nghĩa, dù không trùng từ khóa.
  - **Hình dung thực tế:** Giống sắp xếp sách trong thư viện không theo alphabet mà theo "mùi vị nội dung" — sách về quy chế học vụ đặt gần nhau, sách về tài chính đặt góc khác, dù tên sách chẳng chữ nào giống nhau. Khi độc giả hỏi một câu, thủ thư (embedding câu hỏi) biết ngay câu đó "có mùi giống góc kệ nào" và dẫn thẳng tới đó, thay vì lục từng cuốn theo tên.

**Nhóm 4 — Đánh giá chất lượng**

- **ROUGE**
  - **Định nghĩa:** Đo độ trùng khớp n-gram (chuỗi liên tiếp n từ) giữa bản tóm tắt máy sinh và bản tóm tắt chuẩn do con người viết (ROUGE-1: từ đơn, ROUGE-2: cặp từ liên tiếp, ROUGE-L: chuỗi con chung dài nhất).
  - **Hình dung thực tế:** Giống thầy cô so đáp án học sinh với đáp án mẫu, đếm xem trùng được bao nhiêu cụm từ — chỉ khác là ở đây ta mong muốn độ trùng cao, vì càng giống bài mẫu thì tóm tắt càng được coi là tốt.

- **BERTScore**
  - **Định nghĩa:** Thay vì so khớp từ y hệt như ROUGE, BERTScore chuyển từng từ của 2 câu thành embedding rồi tính độ tương đồng, nên phát hiện được trường hợp 2 câu dùng từ khác nhau nhưng nghĩa giống nhau (ví dụ "sinh viên" và "học viên").
  - **Hình dung thực tế:** Giống nhờ một người am hiểu ngôn ngữ đọc cả 2 bài văn rồi nhận xét "về ý nghĩa, hai bài này giống nhau đến đâu" — dù cách dùng từ khác biệt, người này vẫn nhận ra sự tương đồng, còn cách đếm chữ thuần túy (ROUGE) thì không.

---

**CÁC THUẬT TOÁN BỔ TRỢ KHÁC**

**Tiền xử lý — trước khi mọi thứ bắt đầu**

- **Word Segmentation / Tách từ tiếng Việt (underthesea, VnCoreNLP)**
  - **Định nghĩa:** Tiếng Việt không dùng khoảng trắng để phân tách từ (một từ có thể gồm nhiều tiếng, ví dụ "học sinh" là 1 từ chứ không phải 2). Thuật toán tách từ dùng mô hình thống kê/học máy để xác định đúng ranh giới từ trước khi đưa vào các bước xử lý khác.
  - **Hình dung thực tế:** Giống đọc một câu tiếng Anh bị dính liền không dấu cách: "thedoghouse" — phải nhận ra "dog house" đi liền với nhau mới hiểu đúng là "nhà chó", chứ không tách lung tung. Tách từ sai ngay từ đầu thì mọi bước tóm tắt/trích xuất phía sau đều sai theo.

- **OCR — Nhận dạng ký tự quang học (PaddleOCR/Tesseract)**
  - **Định nghĩa:** Chuyển hình ảnh chứa chữ (văn bản scan) thành văn bản số, qua 2 bước: phát hiện vùng có chữ, rồi nhận dạng từng ký tự trong vùng đó — dùng mạng nơ-ron đã học qua hàng triệu ảnh chữ với đủ loại font, độ nét khác nhau.
  - **Hình dung thực tế:** Giống việc chụp ảnh một trang sách rồi nhờ ai đó gõ lại thành file Word — chỉ khác "người gõ hộ" ở đây là AI, đã luyện mắt qua rất nhiều kiểu chữ và chất lượng ảnh khác nhau nên đọc được cả bản scan hơi mờ.

**Bên trong mô hình sinh câu — cách chọn từng từ**

- **Beam Search (thuật toán decoding)**
  - **Định nghĩa:** Khi mô hình tóm tắt sinh từng từ, tại mỗi bước nó phải chọn 1 từ trong hàng chục nghìn khả năng. Nếu chỉ luôn chọn từ có xác suất cao nhất ngay tại chỗ (greedy), rất dễ mắc kẹt vào một câu cụt nghĩa. Beam Search giữ song song k "ứng viên câu" có xác suất tổng thể cao nhất, mở rộng từng ứng viên qua nhiều bước, rồi mới chọn ứng viên tốt nhất cuối cùng.
  - **Hình dung thực tế:** Giống người chơi cờ giỏi không chỉ tính 1 nước đi tốt nhất ngay trước mắt (dễ sai vì thiển cận), mà giữ trong đầu vài phương án có triển vọng, đi tiếp vài nước rồi mới quyết định nhánh nào thực sự tốt nhất.

- **Cosine Similarity**
  - **Định nghĩa:** Phép đo độ tương đồng giữa 2 vector bằng góc giữa chúng — càng cùng hướng thì càng giống nhau về nghĩa, bất kể độ dài vector. Đây là phép tính nền chạy ngầm bên trong cả TextRank (so câu với câu) lẫn tìm kiếm ngữ nghĩa (so câu hỏi với đoạn văn bản) đã nói ở trên.
  - **Hình dung thực tế:** Giống so hướng đi của 2 người trên bản đồ — nếu cả 2 cùng đi về hướng Đông (dù người đi xa hơn, người đi gần hơn) thì coi là "cùng đường". Cosine similarity chỉ quan tâm hướng đi (nội dung), không quan tâm quãng đường dài ngắn (độ dài văn bản).

**Kỹ thuật huấn luyện & trích xuất bổ sung**

- **LoRA / PEFT (Low-Rank Adaptation) — kỹ thuật dự phòng nếu cần điều chỉnh mô hình**
  - **Định nghĩa:** Thay vì cập nhật toàn bộ hàng trăm triệu tham số của mô hình khi fine-tune (rất tốn tài nguyên), LoRA chỉ chèn thêm một lượng nhỏ tham số mới dạng ma trận hạng thấp vào các lớp của mô hình, và chỉ huấn luyện phần nhỏ này — phần lớn tham số gốc được giữ nguyên.
  - **Hình dung thực tế:** Giống dạy thêm 1 kỹ năng mới cho người đã có sẵn nền tảng vững, thay vì bắt họ học lại từ đầu — chỉ cần một khóa bổ sung ngắn trong khi nền tảng cũ vẫn giữ nguyên.
  - **Ghi chú trong dự án:** Do nguồn dữ liệu bị giới hạn ở chinhphu.vn và tài liệu nội bộ trường (không còn VietNews/VNDS quy mô lớn), chiến lược ưu tiên là **dùng thẳng BARTpho/ViT5 pretrained checkpoint sẵn có** thay vì fine-tune từ đầu. LoRA chỉ cân nhắc áp dụng nếu có dữ liệu gán nhãn đủ chất lượng và thời gian còn cho phép.

- **Rule-based / Regex Extraction (trích xuất theo mẫu cố định)**
  - **Định nghĩa:** Dùng biểu thức chính quy (regular expression) để nhận diện các mẫu ký tự có cấu trúc cố định — ví dụ số hiệu văn bản luôn theo dạng "Số: XX/YYYY/TT-BGDĐT". Không cần mô hình học máy, chỉ cần định nghĩa đúng khuôn mẫu cần tìm — đây là kỹ thuật hỗ trợ NER ở mục "gán nhãn bán tự động" trong Kế hoạch Dữ liệu.
  - **Hình dung thực tế:** Giống cách bạn tìm số điện thoại trong một đoạn văn bằng mắt: không cần hiểu nghĩa cả câu, chỉ cần quét tìm đúng khuôn "10 chữ số liên tiếp bắt đầu bằng số 0".
  - **Vai trò mở rộng trong dự án — Cây văn bản:** Ngoài hỗ trợ NER, Rule-based/Regex còn được dùng để **phát hiện quan hệ tường minh giữa các văn bản** ("thay thế", "sửa đổi", "bãi bỏ", "căn cứ" kèm số hiệu văn bản được nhắc tới) — đây là bước đầu tiên xây dựng tính năng Cây văn bản (WF-06), chi phí thấp vì không cần huấn luyện thêm mô hình.
