# ĐẶC TẢ YÊU CẦU CHỨC NĂNG CHI TIẾT (SRS)
## Hệ Sinh Thái "DAU Second Brain"

| | |
|---|---|
| **Phiên bản** | 1.0 |
| **Tài liệu liên quan** | Tài liệu Đặc tả Nghiệp vụ & Kiến trúc (v1.0), Đề cương chi tiết đồ án |
| **Mục đích** | Cụ thể hóa từng chức năng thành use case đủ chi tiết để triển khai và kiểm thử |

---

## MỤC LỤC
1. Danh sách Actor
2. Ma trận Actor × Use Case
3. Danh sách Yêu cầu chức năng (Functional Requirements)
4. Đặc tả chi tiết từng Use Case
5. Yêu cầu phi chức năng theo từng chức năng

---

## 1. DANH SÁCH ACTOR

| Actor | Mô tả |
|---|---|
| **Cán bộ Phòng Đào tạo** | Quản trị nội dung: nạp văn bản, xác nhận thông tin trích xuất, rà soát & duyệt (human-in-the-loop), duyệt theo chủ đề |
| **Giảng viên** | Người dùng cuối: tra cứu, đặt câu hỏi, tải khung báo cáo gợi ý |
| **Hệ thống (Scheduler/AI Pipeline)** | Actor tự động: chạy các bước xử lý nền (OCR, tóm tắt, kiểm tra faithfulness...) |

---

## 2. MA TRẬN ACTOR × USE CASE

| Use Case | Cán bộ Đào tạo | Giảng viên | Hệ thống (tự động) |
|---|:---:|:---:|:---:|
| UC-01 Nạp văn bản mới | ✔ | | |
| UC-02 Trích xuất & phân loại (loại + chủ đề) | | | ✔ |
| UC-03 Tóm tắt có trích dẫn (NLI 3 nhãn) | | | ✔ |
| UC-04 Rà soát & Duyệt (Human-in-the-loop) | ✔ | | |
| UC-05 Gợi ý khung báo cáo theo Template | | ✔ | ✔ |
| UC-06 Tra cứu & hỏi đáp (RAG) | ✔ | ✔ | ✔ |
| UC-07 Đối chiếu trích dẫn | ✔ | ✔ | |
| UC-08 Xem văn bản liên quan ("Cây văn bản") | ✔ | ✔ | ✔ |
| UC-09 Duyệt văn bản theo chủ đề | ✔ | | |

---

## 3. DANH SÁCH YÊU CẦU CHỨC NĂNG (FUNCTIONAL REQUIREMENTS)

| Mã | Yêu cầu | Use Case liên quan | Độ ưu tiên |
|---|---|---|---|
| FR-01 | Hệ thống cho phép nạp file PDF/ảnh scan qua giao diện web hoặc thư mục theo dõi tự động, **nguồn dữ liệu gồm chinhphu.vn, moet.gov.vn và tài liệu liên quan trực tiếp tới trường** | UC-01 | Bắt buộc |
| FR-02 | Hệ thống tự động chia văn bản thành các đoạn theo cấu trúc Điều/Khoản, mỗi đoạn có ID và số trang | UC-02 | Bắt buộc |
| FR-03 | Hệ thống tự động phân loại văn bản theo **loại văn bản** (thông tư/quyết định/công văn/giáo trình) **và chủ đề/lĩnh vực** (theo danh mục cố định) | UC-02, UC-09 | Bắt buộc |
| FR-04 | Hệ thống tự động trích xuất số hiệu, ngày ban hành, cơ quan ban hành | UC-02 | Bắt buộc |
| FR-05 | Hệ thống tự động phát hiện yêu cầu báo cáo trong văn bản (nếu có): nội dung, hạn nộp, đơn vị chịu trách nhiệm | UC-02 | Bắt buộc |
| FR-06 | Hệ thống sinh bản tóm tắt, mỗi câu gắn kèm ID đoạn nguồn | UC-03 | Bắt buộc |
| FR-07 | Hệ thống phân loại từng câu tóm tắt bằng mô hình NLI thành 1 trong 3 nhãn: `entailment`/`contradiction`/`neutral` trước khi hiển thị | UC-03 | Bắt buộc |
| FR-08 | Văn bản có ít nhất 1 câu bị gắn nhãn `contradiction` **không được chuyển trạng thái `published`** — toàn bộ văn bản (không chỉ câu đó) phải chờ rà soát (UC-04) trước khi phục vụ tra cứu | UC-03, UC-04 | Bắt buộc (ràng buộc an toàn) |
| FR-09 | Cán bộ có thể xem danh sách các câu bị gắn cờ `contradiction`/`neutral` cần rà soát, **sắp xếp theo mức độ ưu tiên** (contradiction trước, neutral sau), mỗi câu hiển thị kèm đoạn văn gốc tương ứng | UC-04 | Bắt buộc |
| FR-09b | Cán bộ có thể duyệt giữ nguyên, sửa & duyệt lại, hoặc loại bỏ câu bị gắn cờ; nếu sửa, hệ thống phải **chạy lại kiểm tra NLI trên câu đã sửa** trước khi lưu | UC-04 | Bắt buộc (ràng buộc an toàn) |
| FR-09c | Hệ thống ghi lại **audit trail** đầy đủ cho mỗi lần rà soát: nội dung AI sinh ra ban đầu, nội dung sau sửa (nếu có), người duyệt, thời điểm | UC-04 | Bắt buộc |
| FR-10 | Hệ thống chọn **mẫu khung báo cáo (template) phù hợp với loại báo cáo và chủ đề văn bản** từ Thư viện Template; nếu không tìm được mẫu khớp, tự dựng khung từ chính đề mục trong văn bản gốc — **không dùng 1 khung cố định chung cho mọi loại văn bản** | UC-05 | Bắt buộc |
| FR-11 | Khung báo cáo không được tự động điền số liệu/nội dung thực tế — các phần này để trống cho người dùng | UC-05 | Bắt buộc (ràng buộc an toàn) |
| FR-12 | Người dùng có thể đặt câu hỏi tự nhiên và nhận câu trả lời kèm trích dẫn nguồn | UC-06 | Bắt buộc |
| FR-13 | Nếu không tìm được căn cứ đủ tin cậy, hoặc văn bản liên quan nhất chưa `published`, hệ thống phải từ chối trả lời thay vì suy đoán | UC-06 | Bắt buộc (ràng buộc an toàn) |
| FR-14 | Người dùng có thể xem đối chiếu từng câu tóm tắt với đoạn nguồn kèm điểm độ tin cậy và nhãn NLI | UC-07 | Nên có |
| FR-15 | Hệ thống ghi log mọi câu hỏi/câu trả lời kèm điểm faithfulness để phục vụ giám sát chất lượng | UC-06 | Nên có |
| FR-16 | Hệ thống hiển thị danh sách văn bản liên quan tới văn bản đang xem, phân theo quan hệ tường minh (căn cứ/thay thế/sửa đổi) và quan hệ ngữ nghĩa (cùng chủ đề), kèm mức độ áp dụng đối với trường | UC-08 | Bắt buộc |
| FR-17 | Hệ thống nhóm và hiển thị văn bản theo chủ đề dạng dashboard, thay cho danh sách hàng đợi phẳng | UC-09 | Bắt buộc |

---

## 4. ĐẶC TẢ CHI TIẾT TỪNG USE CASE

### UC-01 — Nạp văn bản mới

| | |
|---|---|
| **Actor chính** | Cán bộ Phòng Đào tạo |
| **Mô tả** | Cán bộ upload văn bản mới (PDF/ảnh scan) vào hệ thống để bắt đầu quy trình xử lý |
| **Điều kiện tiên quyết** | Cán bộ đã đăng nhập với quyền quản trị nội dung |
| **Luồng chính** | 1. Cán bộ chọn "Nạp văn bản mới" trên dashboard.<br>2. Cán bộ chọn file hoặc kéo-thả vào vùng upload.<br>3. Hệ thống kiểm tra định dạng file hợp lệ (PDF, JPG, PNG).<br>4. Hệ thống lưu file gốc vào Object Storage, sinh mã văn bản tạm thời.<br>5. Hệ thống đẩy văn bản vào hàng đợi xử lý (kích hoạt UC-02).<br>6. Hệ thống hiển thị trạng thái "Đang xử lý" trên danh sách hàng đợi. |
| **Luồng ngoại lệ** | 3a. File sai định dạng → hệ thống báo lỗi rõ ràng, không đưa vào hàng đợi.<br>4a. Lỗi lưu trữ (hết dung lượng...) → hệ thống báo lỗi, cho phép thử lại |
| **Điều kiện sau** | Văn bản được lưu trữ và sẵn sàng cho bước trích xuất |
| **Tiêu chí chấp nhận** | Upload thành công 1 file PDF chuẩn trong ≤ 5 giây; trạng thái "Đang xử lý" hiển thị ngay sau khi upload |

### UC-02 — Trích xuất & phân loại văn bản

| | |
|---|---|
| **Actor chính** | Hệ thống (tự động) |
| **Mô tả** | Hệ thống tự động OCR (nếu cần), chia đoạn, phân loại và trích xuất thông tin từ văn bản |
| **Điều kiện tiên quyết** | Văn bản đã hoàn tất UC-01 |
| **Luồng chính** | 1. Nếu văn bản là ảnh scan → chạy OCR (PaddleOCR/Tesseract).<br>2. Chia văn bản thành các đoạn theo Điều/Khoản/Mục, gán ID + số trang cho từng đoạn.<br>3. Chạy mô hình phân loại xác định **loại văn bản** và **chủ đề/lĩnh vực** (theo danh mục cố định — phục vụ UC-09).<br>4. Chạy mô hình NER trích xuất: số hiệu, ngày ban hành, cơ quan ban hành.<br>5. Kiểm tra văn bản có chứa yêu cầu báo cáo không; nếu có, trích xuất nội dung yêu cầu, hạn nộp, đơn vị chịu trách nhiệm.<br>6. Lưu toàn bộ kết quả vào cơ sở dữ liệu, chuyển văn bản sang bước tóm tắt (kích hoạt UC-03). |
| **Luồng ngoại lệ** | 1a. OCR chất lượng thấp (độ tin cậy < ngưỡng) → gắn cờ "cần nhập liệu thủ công", tạm dừng pipeline.<br>3a. Độ tin cậy phân loại chủ đề thấp → xếp vào nhóm "Chưa phân loại" trong UC-09, không tự ý gán bừa.<br>4a. NER trích xuất với độ tin cậy thấp → vẫn lưu nhưng gắn cờ "cần cán bộ xác nhận" |
| **Điều kiện sau** | Văn bản có cấu trúc đoạn rõ ràng, kèm metadata đã trích xuất (bao gồm loại văn bản và chủ đề) |
| **Tiêu chí chấp nhận** | Độ chính xác NER (F1) đạt mức chấp nhận được trên tập test; 100% văn bản được chia đoạn có ID hợp lệ; độ chính xác phân loại chủ đề ≥ 85% trên tập test |

### UC-03 — Tóm tắt có trích dẫn *(use case lõi)*

| | |
|---|---|
| **Actor chính** | Hệ thống (tự động) |
| **Mô tả** | Sinh bản tóm tắt từ văn bản đã có cấu trúc, phân loại độ trung thực từng câu bằng NLI, và quyết định văn bản có đủ điều kiện xuất bản hay phải chờ rà soát |
| **Điều kiện tiên quyết** | Văn bản đã hoàn tất UC-02 |
| **Luồng chính** | 1. Chạy TextRank chọn ra các đoạn quan trọng nhất làm ngữ cảnh giới hạn.<br>2. Mô hình BARTpho/ViT5 sinh câu tóm tắt **chỉ dựa trên** các đoạn đã chọn, mỗi câu gắn ID đoạn nguồn tương ứng.<br>3. Với mỗi câu tóm tắt, chạy mô hình NLI phân loại thành 1 trong 3 nhãn: `entailment`, `contradiction`, `neutral`.<br>4. Câu nhãn `entailment` → giữ nguyên, gắn link trích dẫn.<br>5. Câu nhãn `contradiction` hoặc `neutral` → đẩy vào hàng đợi rà soát (UC-04), gắn độ ưu tiên (`contradiction` cao hơn `neutral`).<br>6. Nếu văn bản có **ít nhất 1 câu `contradiction`** → toàn bộ văn bản chuyển trạng thái `pending_review`, **không xuất bản dù các câu còn lại đều đạt `entailment`**.<br>7. Nếu không có câu `contradiction` nào (kể cả khi có vài câu `neutral` đã tự động xử lý theo cấu hình) → văn bản chuyển trạng thái `published`.<br>8. Lưu bản tóm tắt hoàn chỉnh kèm bảng ánh xạ câu → nguồn → nhãn NLI. |
| **Luồng ngoại lệ** | 3a. Toàn bộ câu sinh ra đều bị `contradiction` → hệ thống báo "không thể tóm tắt tự động, cần xử lý thủ công toàn bộ văn bản" thay vì đẩy hàng loạt câu riêng lẻ vào hàng đợi |
| **Điều kiện sau** | Văn bản ở trạng thái `published` (sẵn sàng phục vụ UC-06/UC-07/UC-08) hoặc `pending_review` (chờ UC-04) |
| **Tiêu chí chấp nhận** | Không có bất kỳ văn bản nào ở trạng thái `published` mà còn câu `contradiction` chưa qua rà soát — kiểm thử bằng cách rà soát trực tiếp trạng thái trong database trên 100% tập test, không chỉ tin vào giao diện |

**Ví dụ minh họa (theo đúng kịch bản GVHD nêu):** Mô hình sinh 10 câu tóm tắt cho 1 văn bản. NLI phân loại: 8 câu `entailment`, 2 câu `contradiction` (AI diễn đạt sai một thuật ngữ pháp lý). Theo bước 6, **toàn bộ văn bản** chuyển `pending_review` — không chỉ ẩn riêng 2 câu lỗi rồi xuất bản 8 câu còn lại. Văn bản chỉ chính thức `published` sau khi UC-04 xử lý xong 2 câu này (xem UC-04 để biết chi tiết bước duyệt).

### UC-04 — Rà soát & Duyệt nội dung (Human-in-the-loop)

| | |
|---|---|
| **Actor chính** | Cán bộ Phòng Đào tạo |
| **Mô tả** | Cán bộ rà soát các câu bị NLI gắn nhãn `contradiction`/`neutral`, quyết định giữ/sửa/loại, và văn bản chỉ chính thức phục vụ tra cứu sau khi rà soát xong |
| **Điều kiện tiên quyết** | Có ít nhất một văn bản ở trạng thái `pending_review` (theo UC-03) |
| **Luồng chính** | 1. Cán bộ mở mục "Cần rà soát", danh sách hiển thị **sắp xếp theo độ ưu tiên** (`contradiction` lên đầu, `neutral` sau).<br>2. Cán bộ chọn 1 văn bản — hệ thống hiển thị **chính xác các câu bị gắn cờ** (ví dụ 2 trong 10 câu), **mỗi câu đặt cạnh đoạn văn gốc tương ứng** để đối chiếu ngay, không phải hiển thị lẫn với các câu đã đạt.<br>3. Cán bộ đọc, phát hiện lỗi (ví dụ: AI diễn đạt sai một thuật ngữ pháp lý).<br>4. Cán bộ chọn 1 trong 3 hành động cho từng câu: **Duyệt giữ nguyên**, **Sửa & duyệt**, hoặc **Loại bỏ**.<br>5. Nếu chọn "Sửa & duyệt": cán bộ sửa lại vài chữ cho chuẩn xác → hệ thống **chạy lại NLI trên câu đã sửa** trước khi lưu.<br>6. Hệ thống ghi **audit trail**: câu AI sinh ban đầu, câu sau sửa (nếu có), người duyệt, thời điểm.<br>7. Khi **toàn bộ câu bị gắn cờ của văn bản đó** đã được xử lý → văn bản **tự động chuyển từ `pending_review` sang `published`**, chính thức hoàn thiện để phục vụ tra cứu (UC-06/UC-08). |
| **Luồng ngoại lệ** | 5a. Câu sau khi sửa vẫn không đạt `entailment` khi chạy lại NLI → hệ thống không tự lưu, hiển thị cảnh báo và yêu cầu cán bộ xác nhận thêm một lần rõ ràng (tương tự nhánh "Duyệt giữ nguyên") trước khi chấp nhận.<br>6a. Cán bộ chọn "Duyệt giữ nguyên" dù câu vẫn ở nhãn `contradiction`/`neutral` → hệ thống gắn nhãn hiển thị "Đã xác nhận thủ công, độ tin cậy AI thấp" trên câu đó khi hiển thị công khai, không hiển thị giống hệt câu đạt `entailment` tự động |
| **Điều kiện sau** | Văn bản chuyển trạng thái `published` (nếu đã xử lý hết) hoặc vẫn `pending_review` (nếu còn câu chưa xử lý); audit trail được lưu đầy đủ cho mọi quyết định |
| **Tiêu chí chấp nhận** | (1) Danh sách rà soát luôn hiển thị đúng thứ tự ưu tiên; (2) mỗi câu bị gắn cờ hiển thị kèm đúng đoạn nguồn của nó, không lẫn văn bản khác; (3) 100% lượt "Sửa & duyệt" đều có bản ghi audit trail và kết quả chạy lại NLI; (4) văn bản chỉ chuyển `published` khi không còn câu `contradiction`/`neutral` nào ở trạng thái chờ |

**Ví dụ minh họa (khớp với mô tả của GVHD):** Văn bản có 10 câu tóm tắt, 2 câu bị NLI chấm `contradiction`. Văn bản không tự động `published`, bị đẩy vào "Cần rà soát". Cán bộ Đào tạo mở danh sách, thấy đúng 2 câu lỗi nằm cạnh đoạn văn gốc của chúng. Cán bộ nhận ra AI dùng sai một thuật ngữ pháp lý, sửa lại vài chữ, hệ thống chạy lại NLI xác nhận câu đã đạt `entailment`, cán bộ bấm duyệt — cả 2 câu được xử lý xong, văn bản lúc này mới chuyển `published` và chính thức phục vụ tra cứu.

### UC-05 — Gợi ý khung báo cáo

| | |
|---|---|
| **Actor chính** | Giảng viên (sử dụng), Hệ thống (sinh tự động) |
| **Mô tả** | Hệ thống chọn/dựng khung báo cáo **riêng phù hợp với từng văn bản** (không dùng 1 khung chung cho mọi loại), giảng viên tải về và hoàn thiện |
| **Điều kiện tiên quyết** | Văn bản đã được xác định có chứa yêu cầu báo cáo (ở UC-02) và đã ở trạng thái `published` |
| **Luồng chính** | 1. Giảng viên mở văn bản có gắn nhãn "Cần báo cáo".<br>2. Hệ thống tra cứu Thư viện Template theo loại báo cáo + chủ đề văn bản.<br>3a. **Tìm được template khớp** → dùng cấu trúc đề mục riêng của template đó.<br>3b. **Không tìm được template khớp** → hệ thống tự dựng khung trực tiếp từ các đề mục liệt kê trong chính văn bản gốc (không rơi về khung mặc định), và đề xuất lưu làm template mới.<br>4. Hệ thống hiển thị bản xem trước: mục Căn cứ pháp lý (tự động điền, có trích dẫn), các mục Nội dung (đề mục **khác nhau tùy loại văn bản**, lấy từ bước 3), mục Số liệu và Kết luận (luôn để trống).<br>5. Giảng viên bấm "Tải file Word".<br>6. Hệ thống xuất file .docx theo đúng khung đã xem trước. |
| **Luồng ngoại lệ** | 1a. Văn bản có yêu cầu báo cáo nhưng NER trích xuất không đủ tin cậy → hệ thống không tự tạo khung, thông báo cán bộ cần xác nhận thủ công trước |
| **Điều kiện sau** | File khung báo cáo được tải về máy giảng viên; nếu là template mới tự dựng, được lưu vào Thư viện Template để tái sử dụng cho văn bản cùng loại sau này |
| **Tiêu chí chấp nhận** | 100% khung báo cáo sinh ra không chứa số liệu/nội dung tự bịa ở mục Số liệu và Kết luận; mục Căn cứ pháp lý luôn có trích dẫn hợp lệ; **tối thiểu 2 loại văn bản khác nhau trong tập test phải cho ra khung có cấu trúc đề mục khác nhau rõ rệt** (chứng minh không dùng chung 1 khuôn) |

### UC-06 — Tra cứu & Hỏi đáp (RAG)

| | |
|---|---|
| **Actor chính** | Giảng viên, Cán bộ Phòng Đào tạo |
| **Mô tả** | Người dùng đặt câu hỏi tự nhiên, hệ thống trả lời dựa trên kho văn bản kèm trích dẫn |
| **Điều kiện tiên quyết** | Có ít nhất một văn bản ở trạng thái `published` (đã qua UC-03, và UC-04 nếu từng bị gắn cờ) |
| **Luồng chính** | 1. Người dùng nhập câu hỏi vào ô tìm kiếm/chat.<br>2. Hệ thống sinh embedding câu hỏi, truy vấn Vector DB — **chỉ tìm trong các đoạn thuộc văn bản `published`**.<br>3. Hệ thống sinh câu trả lời dựa trên các đoạn tìm được.<br>4. Hệ thống phân loại NLI cho câu trả lời (như UC-03, bước 3); nếu bị gắn nhãn `contradiction`/`neutral` → coi như không đủ căn cứ.<br>5. Nếu đạt `entailment` → hiển thị câu trả lời kèm trích dẫn.<br>6. Hệ thống ghi log câu hỏi, câu trả lời, nhãn NLI. |
| **Luồng ngoại lệ** | 2a. Không tìm được đoạn nào đủ liên quan (hoặc văn bản liên quan nhất vẫn `pending_review`) → trả lời "không tìm thấy thông tin liên quan trong kho văn bản hiện có", không suy đoán.<br>4a. Câu trả lời sinh ra bị `contradiction`/`neutral` → từ chối trả lời, gợi ý người dùng tham khảo trực tiếp văn bản gốc (link kèm theo) |
| **Điều kiện sau** | Câu hỏi và câu trả lời được lưu vào log |
| **Tiêu chí chấp nhận** | Tỷ lệ câu trả lời đúng và có trích dẫn hợp lệ đạt tối thiểu mức đề ra trên tập câu hỏi test; không có trường hợp trả lời sai kèm trích dẫn không liên quan |

### UC-07 — Đối chiếu trích dẫn

| | |
|---|---|
| **Actor chính** | Giảng viên, Cán bộ Phòng Đào tạo |
| **Mô tả** | Người dùng xem chi tiết từng câu trong bản tóm tắt/câu trả lời được lấy từ đoạn nào trong văn bản gốc |
| **Điều kiện tiên quyết** | Văn bản đã có bản tóm tắt (UC-03) |
| **Luồng chính** | 1. Người dùng mở văn bản, chọn "Xem đối chiếu trích dẫn".<br>2. Hệ thống hiển thị danh sách từng câu tóm tắt kèm đoạn nguồn tương ứng và điểm % khớp.<br>3. Người dùng có thể bấm vào từng đoạn nguồn để xem nguyên văn trong file gốc. |
| **Luồng ngoại lệ** | Không có |
| **Điều kiện sau** | Không thay đổi trạng thái hệ thống (chỉ xem) |
| **Tiêu chí chấp nhận** | Mọi câu tóm tắt hiển thị trong UC-03 đều truy vết được về đúng đoạn nguồn khi vào màn hình này |

### UC-08 — Xem văn bản liên quan ("Cây văn bản")

| | |
|---|---|
| **Actor chính** | Giảng viên, Cán bộ Phòng Đào tạo |
| **Mô tả** | Khi xem một văn bản, người dùng thấy được các văn bản liên quan và mức độ áp dụng của văn bản đó đối với trường |
| **Điều kiện tiên quyết** | Văn bản đang xem ở trạng thái `published` |
| **Luồng chính** | 1. Người dùng mở chi tiết 1 văn bản.<br>2. Hệ thống hiển thị 2 nhóm: (a) **Quan hệ trực tiếp** — văn bản mà văn bản này căn cứ vào, hoặc thay thế/bị thay thế (phát hiện bằng rule/NER); (b) **Quan hệ ngữ nghĩa** — các văn bản `published` khác gần nghĩa nhất (tái sử dụng Embedding + Vector DB đã có ở UC-06, truy vấn bằng chính nội dung văn bản thay vì câu hỏi người dùng).<br>3. Hệ thống hiển thị nhãn **mức độ áp dụng cho trường** (ví dụ: "Áp dụng trực tiếp — có quy chế nội bộ trường cụ thể hóa" / "Áp dụng chung, chưa có văn bản nội bộ tương ứng" / "Chỉ mang tính tham khảo"). |
| **Luồng ngoại lệ** | Không tìm được văn bản nào đủ gần nghĩa (dưới ngưỡng similarity) → hiển thị "Chưa phát hiện văn bản liên quan", không ép hiển thị kết quả không đủ liên quan |
| **Điều kiện sau** | Không thay đổi trạng thái hệ thống (chỉ xem), trừ khi cán bộ chủ động xác nhận lại nhãn mức độ áp dụng |
| **Tiêu chí chấp nhận** | Với văn bản có quan hệ tường minh thực sự tồn tại trong kho (ví dụ văn bản B ghi rõ "thay thế văn bản A"), hệ thống phải phát hiện được quan hệ đó tối thiểu 90% trường hợp trên tập test |

### UC-09 — Duyệt văn bản theo chủ đề (Topic Dashboard)

| | |
|---|---|
| **Actor chính** | Cán bộ Phòng Đào tạo |
| **Mô tả** | Thay vì xem một danh sách hàng đợi phẳng, cán bộ duyệt văn bản theo từng chủ đề (Đào tạo, Tuyển sinh, Tài chính...) |
| **Điều kiện tiên quyết** | Đã có văn bản được phân loại chủ đề (UC-02) |
| **Luồng chính** | 1. Cán bộ mở màn hình quản trị nội dung.<br>2. Hệ thống hiển thị các thẻ chủ đề, mỗi thẻ ghi số lượng văn bản thuộc chủ đề đó.<br>3. Cán bộ bấm vào 1 chủ đề → xem danh sách thông tư/quyết định/công văn thuộc chủ đề, kèm trạng thái (`published`/`pending_review`).<br>4. Khu vực nạp văn bản mới (UC-01) và hàng đợi xử lý vẫn hiển thị trong cùng màn hình như một khu vực riêng — không bị thay thế. |
| **Luồng ngoại lệ** | Văn bản chưa phân loại được chủ đề (độ tin cậy thấp) → xếp vào nhóm "Chưa phân loại" riêng, không gán bừa vào 1 chủ đề |
| **Điều kiện sau** | Không thay đổi trạng thái hệ thống (chỉ xem/điều hướng) |
| **Tiêu chí chấp nhận** | Văn bản được nhóm đúng chủ đề cho tối thiểu 85% trường hợp trên tập test (đối chiếu với gán nhãn tay) |

---

## 5. YÊU CẦU PHI CHỨC NĂNG THEO TỪNG CHỨC NĂNG

| Use Case | Yêu cầu phi chức năng |
|---|---|
| UC-01 | Hỗ trợ file tối đa ~20MB; xử lý upload không chặn giao diện (bất đồng bộ) |
| UC-02 | Thời gian xử lý OCR + trích xuất cho 1 văn bản ≤ 5 trang: không quá 60 giây |
| UC-03 | Thời gian sinh tóm tắt cho 1 văn bản ≤ 5 trang: không quá 30-60 giây; **không có ngoại lệ nào cho phép văn bản còn câu `contradiction` chuyển trạng thái `published`** |
| UC-04 | Danh sách "Cần rà soát" phải tải và sắp xếp theo ưu tiên trong ≤ 2 giây với tối đa vài trăm mục (quy mô demo) |
| UC-05 | File khung báo cáo xuất ra phải đúng định dạng .docx, mở được bằng Microsoft Word/LibreOffice |
| UC-06 | Thời gian phản hồi câu hỏi ≤ 5 giây trong điều kiện demo (không tính thời gian mạng) |
| UC-07 | Giao diện đối chiếu phải hiển thị được cả trường hợp câu bị loại bỏ (để minh chứng cơ chế an toàn khi demo) |
| UC-08 | Truy vấn văn bản liên quan (tái sử dụng Vector DB) phản hồi ≤ 3 giây |
| UC-09 | Dashboard theo chủ đề tải danh sách thẻ chủ đề ≤ 2 giây với quy mô 20-30 văn bản (demo) |

---

*Tài liệu này cụ thể hóa các Workflow (WF-01 đến WF-08) trong Tài liệu Đặc tả Nghiệp vụ & Kiến trúc thành các Use Case có thể kiểm thử trực tiếp. Khi triển khai, mỗi User Story trong Sprint Backlog nên tham chiếu về đúng mã Use Case tương ứng.*
