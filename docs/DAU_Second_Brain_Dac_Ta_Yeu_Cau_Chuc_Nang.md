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
| **Cán bộ Phòng Đào tạo** | Quản trị nội dung: nạp văn bản, xác nhận thông tin trích xuất, rà soát cảnh báo |
| **Giảng viên** | Người dùng cuối: tra cứu, đặt câu hỏi, tải khung báo cáo gợi ý |
| **Hệ thống (Scheduler/AI Pipeline)** | Actor tự động: chạy các bước xử lý nền (OCR, tóm tắt, kiểm tra faithfulness...) |

---

## 2. MA TRẬN ACTOR × USE CASE

| Use Case | Cán bộ Đào tạo | Giảng viên | Hệ thống (tự động) |
|---|:---:|:---:|:---:|
| UC-01 Nạp văn bản mới | ✔ | | |
| UC-02 Trích xuất & phân loại | | | ✔ |
| UC-03 Tóm tắt có trích dẫn | | | ✔ |
| UC-04 Rà soát cảnh báo faithfulness thấp | ✔ | | |
| UC-05 Gợi ý khung báo cáo | | ✔ | ✔ |
| UC-06 Tra cứu & hỏi đáp (RAG) | ✔ | ✔ | ✔ |
| UC-07 Đối chiếu trích dẫn | ✔ | ✔ | |

---

## 3. DANH SÁCH YÊU CẦU CHỨC NĂNG (FUNCTIONAL REQUIREMENTS)

| Mã | Yêu cầu | Use Case liên quan | Độ ưu tiên |
|---|---|---|---|
| FR-01 | Hệ thống cho phép nạp file PDF/ảnh scan qua giao diện web hoặc thư mục theo dõi tự động | UC-01 | Bắt buộc |
| FR-02 | Hệ thống tự động chia văn bản thành các đoạn theo cấu trúc Điều/Khoản, mỗi đoạn có ID và số trang | UC-02 | Bắt buộc |
| FR-03 | Hệ thống tự động phân loại văn bản (thông tư/quyết định/công văn/giáo trình) | UC-02 | Bắt buộc |
| FR-04 | Hệ thống tự động trích xuất số hiệu, ngày ban hành, cơ quan ban hành | UC-02 | Bắt buộc |
| FR-05 | Hệ thống tự động phát hiện yêu cầu báo cáo trong văn bản (nếu có): nội dung, hạn nộp, đơn vị chịu trách nhiệm | UC-02 | Bắt buộc |
| FR-06 | Hệ thống sinh bản tóm tắt, mỗi câu gắn kèm ID đoạn nguồn | UC-03 | Bắt buộc |
| FR-07 | Hệ thống kiểm tra từng câu tóm tắt bằng mô hình NLI trước khi hiển thị | UC-03 | Bắt buộc |
| FR-08 | Câu tóm tắt không đạt ngưỡng faithfulness phải bị loại/ẩn khỏi kết quả hiển thị, không được hiển thị cho người dùng cuối | UC-03, UC-04 | Bắt buộc (ràng buộc an toàn) |
| FR-09 | Cán bộ có thể xem danh sách văn bản có cảnh báo cần rà soát thủ công | UC-04 | Bắt buộc |
| FR-10 | Hệ thống sinh khung báo cáo (Word) gồm căn cứ pháp lý (có trích dẫn) và đề mục nội dung theo yêu cầu văn bản | UC-05 | Bắt buộc |
| FR-11 | Khung báo cáo không được tự động điền số liệu/nội dung thực tế — các phần này để trống cho người dùng | UC-05 | Bắt buộc (ràng buộc an toàn) |
| FR-12 | Người dùng có thể đặt câu hỏi tự nhiên và nhận câu trả lời kèm trích dẫn nguồn | UC-06 | Bắt buộc |
| FR-13 | Nếu không tìm được căn cứ đủ tin cậy, hệ thống phải từ chối trả lời thay vì suy đoán | UC-06 | Bắt buộc (ràng buộc an toàn) |
| FR-14 | Người dùng có thể xem đối chiếu từng câu tóm tắt với đoạn nguồn kèm điểm độ tin cậy | UC-07 | Nên có |
| FR-15 | Hệ thống ghi log mọi câu hỏi/câu trả lời kèm điểm faithfulness để phục vụ giám sát chất lượng | UC-06 | Nên có |

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
| **Luồng chính** | 1. Nếu văn bản là ảnh scan → chạy OCR (PaddleOCR/Tesseract).<br>2. Chia văn bản thành các đoạn theo Điều/Khoản/Mục, gán ID + số trang cho từng đoạn.<br>3. Chạy mô hình phân loại xác định loại văn bản.<br>4. Chạy mô hình NER trích xuất: số hiệu, ngày ban hành, cơ quan ban hành.<br>5. Kiểm tra văn bản có chứa yêu cầu báo cáo không; nếu có, trích xuất nội dung yêu cầu, hạn nộp, đơn vị chịu trách nhiệm.<br>6. Lưu toàn bộ kết quả vào cơ sở dữ liệu, chuyển văn bản sang bước tóm tắt (kích hoạt UC-03). |
| **Luồng ngoại lệ** | 1a. OCR chất lượng thấp (độ tin cậy < ngưỡng) → gắn cờ "cần nhập liệu thủ công", tạm dừng pipeline.<br>4a. NER trích xuất với độ tin cậy thấp → vẫn lưu nhưng gắn cờ "cần cán bộ xác nhận" |
| **Điều kiện sau** | Văn bản có cấu trúc đoạn rõ ràng, kèm metadata đã trích xuất |
| **Tiêu chí chấp nhận** | Độ chính xác NER (F1) đạt mức chấp nhận được trên tập test; 100% văn bản được chia đoạn có ID hợp lệ |

### UC-03 — Tóm tắt có trích dẫn *(use case lõi)*

| | |
|---|---|
| **Actor chính** | Hệ thống (tự động) |
| **Mô tả** | Sinh bản tóm tắt từ văn bản đã có cấu trúc, đảm bảo mỗi câu đều có căn cứ kiểm chứng được |
| **Điều kiện tiên quyết** | Văn bản đã hoàn tất UC-02 |
| **Luồng chính** | 1. Chạy TextRank chọn ra các đoạn quan trọng nhất làm ngữ cảnh giới hạn.<br>2. Mô hình BARTpho/ViT5 sinh câu tóm tắt **chỉ dựa trên** các đoạn đã chọn, mỗi câu gắn ID đoạn nguồn tương ứng.<br>3. Với mỗi câu tóm tắt, chạy mô hình NLI kiểm tra mức độ được suy ra (entailment) từ đoạn nguồn, ra điểm faithfulness (0-100%).<br>4. Nếu điểm ≥ ngưỡng quy định → giữ câu, gắn link trích dẫn hiển thị công khai.<br>5. Nếu điểm < ngưỡng → loại câu khỏi bản tóm tắt hiển thị, lưu lại để phục vụ UC-04.<br>6. Lưu bản tóm tắt hoàn chỉnh kèm bảng ánh xạ câu → nguồn, sẵn sàng phục vụ UC-06/UC-07. |
| **Luồng ngoại lệ** | 4a. Toàn bộ các câu sinh ra đều dưới ngưỡng → hệ thống không xuất bản tóm tắt, báo "không thể tóm tắt tự động, cần xử lý thủ công" thay vì cố hiển thị nội dung không đạt |
| **Điều kiện sau** | Bản tóm tắt (nếu đạt) có 100% câu đã qua kiểm tra faithfulness và có trích dẫn hợp lệ |
| **Tiêu chí chấp nhận** | Không có bất kỳ câu nào hiển thị công khai mà thiếu trích dẫn hoặc chưa qua kiểm tra NLI — đây là ràng buộc **không thể vi phạm**, kiểm thử bằng cách rà soát 100% output trên tập test |

### UC-04 — Rà soát cảnh báo faithfulness thấp

| | |
|---|---|
| **Actor chính** | Cán bộ Phòng Đào tạo |
| **Mô tả** | Cán bộ xem lại các câu/văn bản bị hệ thống gắn cờ do không đạt ngưỡng độ tin cậy |
| **Điều kiện tiên quyết** | Có ít nhất một văn bản có câu bị loại ở UC-03 |
| **Luồng chính** | 1. Cán bộ mở mục "Cần rà soát" trên dashboard quản trị.<br>2. Hệ thống hiển thị danh sách văn bản kèm số câu bị loại và điểm faithfulness.<br>3. Cán bộ xem chi tiết câu bị loại và đoạn nguồn liên quan.<br>4. Cán bộ quyết định: chỉnh sửa thủ công và duyệt lại, hoặc bỏ qua (không đưa câu đó vào bản tóm tắt chính thức). |
| **Luồng ngoại lệ** | Không có |
| **Điều kiện sau** | Trạng thái văn bản được cập nhật (đã rà soát / vẫn chờ rà soát) |
| **Tiêu chí chấp nhận** | Cán bộ có thể xem và xử lý toàn bộ danh sách cảnh báo trong vòng vài thao tác, không cần truy vấn thủ công vào cơ sở dữ liệu |

### UC-05 — Gợi ý khung báo cáo

| | |
|---|---|
| **Actor chính** | Giảng viên (sử dụng), Hệ thống (sinh tự động) |
| **Mô tả** | Hệ thống tự động tạo khung báo cáo dựa trên yêu cầu trích xuất được từ văn bản, giảng viên tải về và hoàn thiện |
| **Điều kiện tiên quyết** | Văn bản đã được xác định có chứa yêu cầu báo cáo (ở UC-02) |
| **Luồng chính** | 1. Giảng viên mở văn bản có gắn nhãn "Cần báo cáo".<br>2. Hệ thống hiển thị bản xem trước khung báo cáo: mục Căn cứ pháp lý (tự động điền, có trích dẫn), mục Nội dung (đề mục theo đúng yêu cầu văn bản), mục Số liệu và Kết luận (để trống).<br>3. Giảng viên bấm "Tải file Word".<br>4. Hệ thống xuất file .docx theo đúng khung đã xem trước. |
| **Luồng ngoại lệ** | 1a. Văn bản có yêu cầu báo cáo nhưng NER trích xuất không đủ tin cậy → hệ thống không tự tạo khung, thông báo cán bộ cần xác nhận thủ công trước |
| **Điều kiện sau** | File khung báo cáo được tải về máy giảng viên |
| **Tiêu chí chấp nhận** | 100% khung báo cáo sinh ra không chứa số liệu/nội dung tự bịa ở mục Số liệu và Kết luận; mục Căn cứ pháp lý luôn có trích dẫn hợp lệ |

### UC-06 — Tra cứu & Hỏi đáp (RAG)

| | |
|---|---|
| **Actor chính** | Giảng viên, Cán bộ Phòng Đào tạo |
| **Mô tả** | Người dùng đặt câu hỏi tự nhiên, hệ thống trả lời dựa trên kho văn bản kèm trích dẫn |
| **Điều kiện tiên quyết** | Có ít nhất một văn bản đã hoàn tất UC-03 (đã được index vào Vector DB) |
| **Luồng chính** | 1. Người dùng nhập câu hỏi vào ô tìm kiếm/chat.<br>2. Hệ thống sinh embedding câu hỏi, truy vấn Vector DB lấy các đoạn liên quan nhất.<br>3. Hệ thống sinh câu trả lời dựa trên các đoạn tìm được.<br>4. Hệ thống kiểm tra faithfulness của câu trả lời (như UC-03, bước 3).<br>5. Nếu đạt ngưỡng → hiển thị câu trả lời kèm trích dẫn.<br>6. Hệ thống ghi log câu hỏi, câu trả lời, điểm faithfulness. |
| **Luồng ngoại lệ** | 2a. Không tìm được đoạn nào đủ liên quan → trả lời "không tìm thấy thông tin liên quan trong kho văn bản hiện có", không suy đoán.<br>4a. Câu trả lời sinh ra không đạt ngưỡng faithfulness → từ chối trả lời, gợi ý người dùng tham khảo trực tiếp văn bản gốc (link kèm theo) |
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

---

## 5. YÊU CẦU PHI CHỨC NĂNG THEO TỪNG CHỨC NĂNG

| Use Case | Yêu cầu phi chức năng |
|---|---|
| UC-01 | Hỗ trợ file tối đa ~20MB; xử lý upload không chặn giao diện (bất đồng bộ) |
| UC-02 | Thời gian xử lý OCR + trích xuất cho 1 văn bản ≤ 5 trang: không quá 60 giây |
| UC-03 | Thời gian sinh tóm tắt cho 1 văn bản ≤ 5 trang: không quá 30-60 giây; **không có ngoại lệ nào cho phép hiển thị câu chưa qua kiểm tra faithfulness** |
| UC-05 | File khung báo cáo xuất ra phải đúng định dạng .docx, mở được bằng Microsoft Word/LibreOffice |
| UC-06 | Thời gian phản hồi câu hỏi ≤ 5 giây trong điều kiện demo (không tính thời gian mạng) |
| UC-07 | Giao diện đối chiếu phải hiển thị được cả trường hợp câu bị loại bỏ (để minh chứng cơ chế an toàn khi demo) |

---

*Tài liệu này cụ thể hóa các Workflow (WF-01 đến WF-07) trong Tài liệu Đặc tả Nghiệp vụ & Kiến trúc thành các Use Case có thể kiểm thử trực tiếp. Khi triển khai, mỗi User Story trong Sprint Backlog nên tham chiếu về đúng mã Use Case tương ứng.*
