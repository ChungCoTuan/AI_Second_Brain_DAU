# KẾ HOẠCH THU THẬP & XỬ LÝ DỮ LIỆU
## Hệ Sinh Thái "DAU Second Brain"

| | |
|---|---|
| **Phiên bản** | 1.0 |
| **Tài liệu liên quan** | Đề cương chi tiết đồ án, Tài liệu Đặc tả Kiến trúc |
| **Ràng buộc** | Nhóm 2 người, 12 tuần — kế hoạch dữ liệu phải thực tế, không dựa vào việc gán nhãn thủ công quy mô lớn |

---

## MỤC LỤC
1. Mục tiêu & nguyên tắc
2. Nguồn dữ liệu
3. Chiến lược dữ liệu 2 tầng (Train vs Domain-specific)
4. Quy trình thu thập
5. Quy trình tiền xử lý
6. Quy trình gán nhãn (Annotation)
7. Phân chia tập dữ liệu
8. Kiểm soát chất lượng dữ liệu
9. Vấn đề pháp lý & đạo đức dữ liệu
10. Timeline thu thập dữ liệu

---

## 1. MỤC TIÊU & NGUYÊN TẮC

**Mục tiêu:** Có đủ dữ liệu để (a) fine-tune mô hình tóm tắt tiếng Việt, và (b) xây được tập kiểm thử (test set) chất lượng để đo ROUGE, BERTScore, và đặc biệt là **Faithfulness** — chỉ số quan trọng nhất của đồ án.

**Nguyên tắc thực tế cho nhóm 2 người/12 tuần:**
- **Không tự gán nhãn tóm tắt chuẩn (gold summary) cho hàng trăm văn bản** — quá tốn thời gian, không khả thi.
- **Tận dụng tối đa dữ liệu công khai đã có sẵn** để huấn luyện khả năng tóm tắt chung, chỉ tự thu thập/gán nhãn một tập nhỏ, chất lượng cao cho phần đặc thù (văn bản pháp quy giáo dục).
- **Tận dụng cấu trúc có sẵn của văn bản hành chính** (trích yếu, mục lục điều khoản) thay vì phải gán nhãn từ đầu.

---

## 2. NGUỒN DỮ LIỆU

### 2.1 Dữ liệu công khai (dùng để huấn luyện khả năng tóm tắt chung)

| Nguồn | Nội dung | Quy mô | Mục đích |
|---|---|---|---|
| **VietNews** | Cặp (bài báo, tóm tắt) tiếng Việt | ~150.000 cặp | Fine-tune mô hình tóm tắt tiếng Việt tổng quát (base) |
| **VNDS (Vietnamese News Dataset Summarization)** | Cặp (bài báo, tóm tắt) | ~150.000 cặp | Bổ sung/so sánh với VietNews |

### 2.2 Dữ liệu đặc thù (dùng để đánh giá & domain-adapt)

| Nguồn | Nội dung | Cách lấy |
|---|---|---|
| **Cổng thông tin điện tử Bộ GD&ĐT** (moet.gov.vn) | Thông tư, quyết định, công văn | Tải trực tiếp bản PDF công khai |
| **Cơ sở dữ liệu quốc gia về văn bản pháp luật** (vbpl.vn) | Văn bản pháp quy đối chiếu, kiểm tra hiệu lực | Tra cứu bổ sung để xác nhận trạng thái hiệu lực |
| **Văn bản nội bộ trường** (nếu GVHD/phòng đào tạo cung cấp) | Quy chế, thông báo nội bộ | Xin cung cấp trực tiếp — **cần xác nhận phạm vi được phép sử dụng** |

### 2.3 Đối tượng người dùng thử nghiệm (cho việc đánh giá chatbot)
Nếu có thể, xin 3-5 câu hỏi thực tế từ cán bộ Phòng Đào tạo/giảng viên để xây tập câu hỏi test cho UC-06 (tra cứu/hỏi đáp), thay vì nhóm tự nghĩ ra câu hỏi — giúp tập test sát với nhu cầu thật hơn.

---

## 3. CHIẾN LƯỢC DỮ LIỆU 2 TẦNG

```
TẦNG 1 — Huấn luyện khả năng tóm tắt chung
   Dữ liệu: VietNews / VNDS (~150k cặp, có sẵn)
   Mục đích: Mô hình biết tóm tắt tiếng Việt tự nhiên, đúng ngữ pháp
                          │
                          ▼
TẦNG 2 — Đánh giá & tinh chỉnh cho domain văn bản pháp quy
   Dữ liệu: 20-30 văn bản GD&ĐT tự thu thập, có gold summary
   Mục đích: Đo lường mô hình hoạt động tốt đến đâu trên đúng loại
             văn bản mục tiêu; tinh chỉnh thêm nếu kết quả chưa tốt
```

**Lý do chọn chiến lược này:** tự thu thập đủ dữ liệu huấn luyện (hàng chục nghìn cặp) riêng cho văn bản pháp quy giáo dục là không khả thi trong 12 tuần. Dùng dữ liệu công khai để mô hình có nền tảng tóm tắt tốt, sau đó **đánh giá nghiêm túc trên đúng domain mục tiêu** — đây vẫn là đóng góp có giá trị vì cho thấy mô hình tổng quát hoạt động ra sao khi áp dụng vào lĩnh vực chuyên biệt, có kiểm chứng bằng Faithfulness.

---

## 4. QUY TRÌNH THU THẬP

| Bước | Nội dung | Công cụ |
|---|---|---|
| 1 | Tải dữ liệu VietNews/VNDS | Script tải tự động (dataset có sẵn trên các nguồn nghiên cứu công khai) |
| 2 | Thu thập 20-30 văn bản GD&ĐT | Tải thủ công hoặc script đơn giản từ moet.gov.vn (chỉ crawl trang công khai, không yêu cầu đăng nhập) |
| 3 | Phân loại sơ bộ khi thu thập | Gắn nhãn thô: loại văn bản, năm ban hành, lĩnh vực (đào tạo/tài chính/nhân sự...) để đảm bảo tập dữ liệu đa dạng, không dồn vào 1 chủ đề |
| 4 | Lưu trữ có tổ chức | Thư mục theo cấu trúc `data/raw/<loai_van_ban>/<so_hieu>.pdf` kèm file `metadata.csv` ghi nguồn gốc |

> **Lưu ý:** Chỉ thu thập văn bản **công khai** (thông tư/quyết định/công văn đã ban hành chính thức). Không crawl dữ liệu yêu cầu đăng nhập hoặc có dấu hiệu nội bộ/mật.

---

## 5. QUY TRÌNH TIỀN XỬ LÝ

1. **Chuyển PDF sang văn bản thô**: dùng thư viện trích xuất text (pdfplumber/PyMuPDF); với văn bản dạng scan, chạy OCR (PaddleOCR/Tesseract).
2. **Chia đoạn theo cấu trúc Điều/Khoản**: dùng rule-based (regex nhận diện "Điều X", "Khoản Y") vì văn bản hành chính có cấu trúc khá chuẩn hóa — đây là lợi thế giúp việc chia đoạn chính xác hơn nhiều so với văn bản tự do.
3. **Làm sạch**: loại bỏ header/footer lặp lại, số trang, ký tự lỗi do OCR.
4. **Chuẩn hóa**: thống nhất cách viết ngày tháng, số hiệu văn bản.

---

## 6. QUY TRÌNH GÁN NHÃN (ANNOTATION)

### 6.1 Gán nhãn tóm tắt chuẩn (Gold Summary) — tận dụng "trích yếu"
Phần lớn thông tư/quyết định của Bộ GD&ĐT có sẵn mục **"Trích yếu"** hoặc phần mở đầu tóm lược nội dung — đây có thể dùng làm gold summary ban đầu, **giảm đáng kể khối lượng viết tay**. Với văn bản không có trích yếu rõ ràng, 2 thành viên tự viết tóm tắt tay cho một tập nhỏ (khuyến nghị 20-30 văn bản dùng làm test set — đúng bằng số văn bản đã thu thập ở mục 2.2).

### 6.2 Gán nhãn NER — bán tự động
Số hiệu văn bản, ngày ban hành, cơ quan ban hành đều có **format khá cố định** trong văn bản hành chính Việt Nam (ví dụ: "Số: 08/2024/TT-BGDĐT", "Hà Nội, ngày ... tháng ... năm ..."). Đề xuất:
1. Viết rule/regex trích xuất tự động trước (độ chính xác kỳ vọng khá cao vì format chuẩn).
2. Người thu thập chỉ cần **kiểm tra và sửa lỗi** thay vì gán nhãn từ đầu — tiết kiệm thời gian đáng kể so với gán nhãn thủ công 100%.

### 6.3 Gán nhãn đánh giá Faithfulness
Với tập test (20-30 văn bản), sau khi mô hình sinh tóm tắt, 2 thành viên **cùng đọc và đánh giá thủ công** một mẫu ngẫu nhiên (ví dụ 10 văn bản) để đối chiếu với điểm mà mô hình NLI tự động đưa ra — nhằm kiểm tra mô hình NLI có đáng tin không, không chỉ tin tưởng hoàn toàn vào số liệu tự động.

---

## 7. PHÂN CHIA TẬP DỮ LIỆU

| Tập | Nguồn | Quy mô | Mục đích |
|---|---|---|---|
| Train | VietNews/VNDS | ~90% của bộ dữ liệu công khai | Fine-tune mô hình tóm tắt chung |
| Validation | VietNews/VNDS | ~10% của bộ dữ liệu công khai | Theo dõi trong quá trình fine-tune, tránh overfitting |
| **Test (domain-specific)** | 20-30 văn bản GD&ĐT tự thu thập | 100% tập tự thu thập | Đánh giá cuối: ROUGE, BERTScore, Faithfulness — **đây là kết quả chính báo cáo trong đồ án** |

---

## 8. KIỂM SOÁT CHẤT LƯỢNG DỮ LIỆU

- Kiểm tra trùng lặp văn bản (cùng số hiệu xuất hiện 2 lần).
- Kiểm tra văn bản không bị lỗi OCR nghiêm trọng (tỷ lệ ký tự lỗi quá cao → loại khỏi tập test, không cố gắng "sửa" bằng tay quá nhiều để tránh sai lệch).
- Đảm bảo tập test đa dạng loại văn bản (không chỉ toàn thông tư về 1 chủ đề như học phí, mà có cả đào tạo/tuyển sinh/nhân sự...) để đánh giá không bị thiên lệch.

---

## 9. VẤN ĐỀ PHÁP LÝ & ĐẠO ĐỨC DỮ LIỆU

- Văn bản pháp quy do cơ quan nhà nước ban hành công khai **không thuộc diện bảo hộ bản quyền theo quy định pháp luật Việt Nam về sở hữu trí tuệ đối với văn bản quy phạm pháp luật** — an toàn để sử dụng cho mục đích nghiên cứu/học thuật.
- Nếu sử dụng tài liệu nội bộ trường (không công khai), **cần xin xác nhận bằng văn bản/email từ GVHD hoặc Phòng Đào tạo** trước khi đưa vào hệ thống, và cân nhắc ẩn danh hóa nếu tài liệu có thông tin nhạy cảm.
- Không thu thập hoặc lưu trữ dữ liệu cá nhân (thông tin sinh viên/giảng viên cụ thể) trong tập dữ liệu huấn luyện.

---

## 10. TIMELINE THU THẬP DỮ LIỆU

| Thời điểm | Công việc |
|---|---|
| Tuần 1 | Tải VietNews/VNDS; bắt đầu thu thập văn bản GD&ĐT (song song, Track A phụ trách) |
| Tuần 2 | Hoàn tất thu thập 20-30 văn bản; xây xong pipeline tiền xử lý (chia đoạn, làm sạch) |
| Tuần 3-4 | Gán nhãn gold summary (tận dụng trích yếu + viết tay phần còn thiếu); kiểm tra NER bán tự động |
| Tuần 7-8 (song song Sprint 3) | Đánh giá thủ công mẫu Faithfulness, đối chiếu với điểm NLI tự động |

> Việc thu thập dữ liệu nằm trọn trong Sprint 0 (tuần 1-2) theo kế hoạch Scrum đã có trong Tài liệu Kiến trúc — không kéo dài sang các sprint sau để tránh ảnh hưởng tiến độ phát triển mô hình.

---

*Kế hoạch này ưu tiên tính khả thi trong 12 tuần hơn là quy mô dữ liệu lớn — chất lượng và tính đại diện của tập test 20-30 văn bản quan trọng hơn số lượng, vì đây là cơ sở duy nhất để chứng minh hệ thống hoạt động đúng như cam kết (không bịa đặt thông tin).*
