**Q&A**

**1. Tài liệu được lưu ở đâu?**

Hệ thống không lưu mọi thứ vào một chỗ, mà tách ra 3 lớp lưu trữ khác nhau (đã có trong tài liệu kiến trúc, mục "Data Layer"), mỗi lớp phục vụ một mục đích:

| Lớp lưu trữ | Lưu gì | Vì sao cần tách riêng |
| --- | --- | --- |
| Object Storage (ổ đĩa/MinIO) | File PDF/ảnh gốc, nguyên bản | Giữ nguyên bản gốc để người dùng đối chiếu, không đụng vào |
| Relational DB (PostgreSQL) | Metadata: số hiệu, ngày ban hành, loại văn bản, trạng thái hiệu lực, quan hệ giữa các bảng | Cần truy vấn có cấu trúc, chính xác tuyệt đối (ví dụ "tìm tất cả thông tư năm 2024") |
| Vector DB (FAISS/Chroma) | Embedding (vector số) của từng đoạn văn bản | Phục vụ tìm kiếm ngữ nghĩa — không thể tìm "ý nghĩa gần giống" bằng database thông thường |

Khi bạn nạp 1 văn bản: file gốc → Object Storage; các trường trích xuất (số hiệu, ngày...) → Relational DB; từng đoạn sau khi chia theo Điều/Khoản → sinh embedding → Vector DB. Ba nơi này liên kết với nhau qua ID chung của văn bản.

**2. Nạp nhiều tài liệu có bị xung đột không?**

Ở quy mô 20-30 văn bản (phạm vi đồ án 12 tuần), gần như không có rủi ro này — nhưng đáng để hiểu cơ chế:

- **Trùng ID/tên file:** mỗi văn bản khi nạp được gán 1 mã định danh duy nhất (UUID hoặc số tự tăng) do hệ thống sinh ra, không phụ thuộc vào tên file người dùng đặt — nên 2 file trùng tên vẫn không đè lên nhau.
- **Trùng nội dung (nạp nhầm 2 lần cùng 1 văn bản):** đây là lý do bước "kiểm tra trùng lặp theo số hiệu văn bản" đã có trong Kế hoạch Dữ liệu (mục 8) — hệ thống nên so số hiệu trước khi lưu, cảnh báo nếu trùng thay vì âm thầm tạo bản sao.
- **Nhiều người nạp cùng lúc:** vì dùng cơ sở dữ liệu có giao dịch (transaction), 2 thao tác ghi cùng lúc vẫn được xử lý tuần tự, không ghi đè lẫn nhau — đây là cơ chế chuẩn của mọi hệ quản trị CSDL, không cần tự xây thêm gì đặc biệt cho đồ án.

Điều đáng nói thật: rủi ro thật sự không phải là "xung đột dữ liệu" mà là hiệu năng khi số lượng lớn lên nhiều (hàng nghìn văn bản trở lên) — FAISS ở chế độ đơn giản chạy trong bộ nhớ, tìm kiếm chậm dần khi vector quá nhiều, lúc đó cần chuyển sang vector DB có index tối ưu hơn hoặc chia nhỏ theo phân vùng (sharding). Với quy mô đồ án thì chưa chạm ngưỡng này, nhưng đây là điểm hay để bạn nêu trong phần "Hướng phát triển" của báo cáo — cho thấy bạn hiểu giới hạn của giải pháp hiện tại.

**3. Tìm kiếm sai / xếp loại sai có xảy ra không?**

Có thể, và đây là điều cần thành thật thừa nhận — không có mô hình phân loại hay tìm kiếm ngữ nghĩa nào đúng 100%:

- **Phân loại sai loại văn bản hoặc chủ đề:** mô hình classification có thể nhầm giữa "công văn" và "thông báo", hoặc gán sai chủ đề (ví dụ nhầm giữa "Đào tạo" và "Tuyển sinh") nếu 2 loại có văn phong gần giống nhau. Cách giảm thiểu: hiển thị độ tin cậy của dự đoán, nếu thấp thì xếp vào nhóm "Chưa phân loại" để cán bộ xác nhận tay thay vì tự động lưu luôn (UC-02/UC-09).
- **Tìm kiếm ngữ nghĩa trả kết quả không đúng ý:** vì semantic search dựa trên "độ gần nghĩa" (cosine similarity), khi kho văn bản lớn, có thể trả về đoạn gần giống nhưng không phải điều người dùng thực sự cần — ví dụ hỏi về "học phí" có thể lẫn với đoạn nói về "học bổng" vì ngữ cảnh gần nhau. Cách giảm thiểu thực tế: kết hợp lọc theo metadata trước khi tìm ngữ nghĩa (hybrid search) — ví dụ chỉ tìm trong nhóm văn bản đã phân loại "Đào tạo", thay vì tìm mù trên toàn bộ kho.

Đây cũng là lý do UC-06 (chatbot) có bước kiểm tra NLI **3 nhãn** sau khi tìm được đoạn liên quan — nếu đoạn tìm được không thực sự support được câu trả lời (gắn nhãn `contradiction` hoặc `neutral`), hệ thống từ chối thay vì trả lời sai dựa trên kết quả tìm kiếm lệch.

**4. Tài liệu dung lượng lớn thì sao?**

Đây là giới hạn kỹ thuật thật sự cần lưu ý, tách làm 2 lớp:

- **a) Giới hạn kích thước file khi upload:**
  Theo yêu cầu phi chức năng đã đặt ra (UC-01), hệ thống giới hạn dung lượng file (đề xuất ~20MB) — file quá lớn (ví dụ bản scan độ phân giải rất cao) sẽ bị từ chối kèm thông báo rõ ràng, thay vì cố xử lý rồi treo hệ thống.

- **b) Giới hạn "trí nhớ" của mô hình tóm tắt — đây là vấn đề quan trọng hơn:**
  Các mô hình như BARTpho/ViT5 có giới hạn số lượng token đọc được trong 1 lần (thường vài trăm đến ~1024 token, tùy phiên bản) — văn bản dài hơn giới hạn này sẽ bị cắt bớt nếu đưa thẳng vào mô hình, dẫn đến tóm tắt thiếu ý ở phần cuối.

May mắn là kiến trúc bạn đang có đã vô tình giải quyết được phần lớn vấn đề này: vì hệ thống luôn chia văn bản theo Điều/Khoản trước khi tóm tắt (phục vụ mục đích trích dẫn), mỗi đoạn nhỏ này thường đủ ngắn để nằm gọn trong giới hạn token của mô hình — tóm tắt được thực hiện theo từng đoạn chứ không phải nhồi cả văn bản 50 trang vào một lần.

Với văn bản cực dài (nhiều chục trang, nhiều chương), cần thêm 1 bước đã nhắc tới trước đây: tóm tắt phân cấp (hierarchical/map-reduce) — tóm tắt từng Điều/Khoản trước, rồi tóm tắt của các tóm tắt đó thành bản tổng quan cấp cao hơn. Nếu 12 tuần không đủ thời gian làm bước này, nên ghi rõ trong báo cáo là giới hạn đã biết (known limitation): "hệ thống tóm tắt tốt với văn bản đơn lẻ có cấu trúc điều khoản rõ ràng (là phần lớn văn bản mục tiêu của đồ án); với văn bản rất dài, nhiều chương phức tạp, cần bổ sung tóm tắt phân cấp ở giai đoạn phát triển tiếp theo" — nói thẳng giới hạn này ra còn tốt hơn là để hội đồng tự phát hiện khi demo.

**5. "Cây văn bản" hoạt động thế nào, có cần xây mô hình riêng không?**

Không — đây là điểm thiết kế quan trọng giúp giữ khối lượng công việc trong tầm kiểm soát. "Cây văn bản" (WF-06/UC-08) được xây bằng cách **tái sử dụng hoàn toàn hạ tầng đã có**, không cần huấn luyện thêm mô hình mới:

- **Quan hệ tường minh (rule-based/regex):** dùng biểu thức chính quy phát hiện các cụm từ chỉ quan hệ ("thay thế", "sửa đổi", "bãi bỏ", "căn cứ") kèm số hiệu văn bản được nhắc tới trong câu đó → tạo quan hệ `can_cu`/`thay_the`/`sua_doi` giữa 2 văn bản. Chi phí rất thấp, không cần GPU.
- **Quan hệ ngữ nghĩa (embedding):** dùng chính Vector DB đã xây cho chatbot RAG — thay vì đầu vào là câu hỏi của người dùng, đầu vào là nội dung văn bản đang xem → truy vấn top-k văn bản gần nghĩa nhất. Về mặt kỹ thuật, chỉ cần thay 1 dòng đầu vào của Retrieval Service, không cần thêm service riêng.
- **Mức độ áp dụng cho trường:** gán nhãn bán tự động (hệ thống đề xuất, cán bộ xác nhận) — nếu quan hệ ngữ nghĩa tìm được văn bản nội bộ trường đủ gần nghĩa thì đề xuất "Áp dụng trực tiếp", ngược lại đề xuất "Áp dụng chung".

Lý do tính năng này được đưa lại vào phạm vi sau khi ban đầu bị cắt: chi phí triển khai thực tế thấp hơn nhiều so với ước tính ban đầu (không cần model mới), trong khi giá trị với người dùng cuối khá cao (cán bộ thấy ngay văn bản mình đang đọc liên quan tới những văn bản nào khác).

**6. Tại sao không fine-tune BARTpho/ViT5 mà dùng thẳng pretrained?**

Đây là quyết định thực dụng xuất phát từ ràng buộc dữ liệu: theo yêu cầu GVHD, nguồn dữ liệu chỉ được lấy từ chinhphu.vn và tài liệu liên quan trực tiếp tới trường — không dùng thêm dataset công khai ngoài ngành (VietNews, VNDS). Với ~20-30 văn bản, fine-tune từ đầu (cập nhật toàn bộ tham số) có nguy cơ **overfitting cao** và kết quả tệ hơn pretrained.

Thay vào đó, chiến lược mới là:
1. **Dùng thẳng BARTpho/ViT5 checkpoint sẵn có** (đã được pretrained trên hàng triệu văn bản tiếng Việt) — mô hình này đã biết cách tóm tắt tiếng Việt, chỉ cần điều chỉnh prompt/context phù hợp với domain văn bản pháp quy.
2. **Tập trung vào cơ chế kiểm soát đầu ra** (NLI 3 nhãn + Review Service) thay vì tập trung vào fine-tune — đây chính là đóng góp kỹ thuật cốt lõi của đồ án: không cần mô hình "thông minh hơn", chỉ cần hệ thống kiểm soát "chắc hơn".
3. Nếu có thời gian và dữ liệu gán nhãn đủ chất lượng, có thể thử LoRA/PEFT để điều chỉnh nhẹ mô hình mà không bị overfitting — nhưng đây là bước không bắt buộc trong 12 tuần.
