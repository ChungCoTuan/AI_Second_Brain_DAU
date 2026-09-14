# KẾ HOẠCH THU THẬP & XỬ LÝ DỮ LIỆU
## Hệ Sinh Thái "DAU Second Brain"

| | |
|---|---|
| **Phiên bản** | 2.0 |
| **Tài liệu liên quan** | Đề cương chi tiết đồ án, Tài liệu Đặc tả Kiến trúc |
| **Ràng buộc** | Nhóm 2 người, 12 tuần — kế hoạch dữ liệu tập trung vào bóc tách thông tin pháp chế (Information Extraction) có độ chính xác cao |

---

## MỤC LỤC
1. Mục tiêu & nguyên tắc
2. Nguồn dữ liệu
3. Chiến lược bóc tách thông tin (Information Extraction)
4. Quy trình thu thập & Tiền xử lý
5. Quy trình gán nhãn (Annotation) cho các thực thể pháp chế
6. Phân chia tập dữ liệu
7. Kiểm soát chất lượng dữ liệu
8. Vấn đề pháp lý & đạo đức dữ liệu
9. Timeline thu thập dữ liệu

---

## 1. MỤC TIÊU & NGUYÊN TẮC

**Mục tiêu:** Xây dựng tập dữ liệu chất lượng cao để đánh giá khả năng bóc tách thông tin pháp chế có cấu trúc từ văn bản thô, bao gồm: **Sự kiện hiệu lực (suKienHieuLuc)**, **Nghĩa vụ (nghiaVu)**, và **Con số chốt (conSoChot)**. Từ đó hỗ trợ hệ thống Cảnh báo pháp lý và Sổ tra ngưỡng.

**Nguyên tắc thực tế cho nhóm 2 người/12 tuần:**
- **Chuyển trọng tâm từ Tóm tắt (Summarization) sang Bóc tách thông tin (Information Extraction - IE)**: Thay vì chỉ tóm tắt văn bản, hệ thống cần trích xuất chính xác các điều khoản bắt buộc, con số định lượng, và tình trạng hiệu lực để tạo ra các tính năng tra cứu hữu ích cho nhà trường.
- **Dữ liệu mỏ neo**: Lấy các văn bản của Bộ GD&ĐT làm trung tâm, sau đó đối chiếu quy chế nội bộ của Trường Đại học Kiến trúc để thực hiện rà soát chéo (Cross-Auditing).
- **Tận dụng LLM hiện đại (Zero-shot / Few-shot)**: Thay vì fine-tune mô hình từ đầu, sử dụng kỹ thuật Prompt Engineering trên các mô hình ngôn ngữ lớn (LLM) để trích xuất JSON có cấu trúc, dùng tập dữ liệu gán nhãn thủ công làm tập Test để đo đạc độ chính xác.

---

## 2. NGUỒN DỮ LIỆU

### 2.1 Nguồn dữ liệu chính

| Nguồn | Nội dung | Cách lấy |
|---|---|---|
| **Cổng Thông tin điện tử Chính phủ / Bộ GD&ĐT** | Văn bản quy phạm pháp luật đầy đủ (Luật, Nghị định, Thông tư) liên quan đến giáo dục đại học. Đặc biệt chú trọng các văn bản có tính quy phạm cao. | Tải trực tiếp bản PDF/HTML/Word; tập trung vào lĩnh vực "Giáo dục - Đào tạo". |
| **Tài liệu văn bản nội bộ của trường** | Quy chế đào tạo, Quy định tài chính, Thông báo nội bộ của Trường Đại học Kiến trúc. | Xin cung cấp từ GVHD/Phòng Đào tạo (chỉ dùng bản công khai hoặc được phép sử dụng). |

---

## 3. CHIẾN LƯỢC BÓC TÁCH THÔNG TIN (INFORMATION EXTRACTION)

Vì mục tiêu là tạo ra cơ sở dữ liệu JSON chặt chẽ (như trong giao diện demo), chiến lược xử lý dữ liệu tập trung vào:

```
BƯỚC 1 — Trích xuất cấu trúc văn bản (Parsing)
   Chuyển đổi PDF/DOCX thành text có cấu trúc phân tầng: 
   Chương -> Mục -> Điều -> Khoản -> Điểm.
   Giữ nguyên tham chiếu (citation) để phục vụ UI.

BƯỚC 2 — Sử dụng LLM để bóc tách thực thể (IE)
   Thiết kế Prompt để LLM trích xuất 3 loại dữ liệu chính:
   - Sự kiện hiệu lực (Thay thế, bãi bỏ, sửa đổi)
   - Nghĩa vụ (Ai phải làm gì, hạn chót)
   - Con số chốt (Tỷ lệ, định mức, số lượng)

BƯỚC 3 — Đối chiếu & Đánh giá (Cross-Auditing)
   Sử dụng tập Test do con người gán nhãn để đo lường
   độ chính xác của LLM.
```

---

## 4. QUY TRÌNH THU THẬP & TIỀN XỬ LÝ

1. **Thu thập**: Tải 30-50 văn bản cốt lõi (ví dụ: Luật Giáo dục Đại học, Thông tư chuẩn chương trình đào tạo, Quy chế đào tạo tín chỉ của trường).
2. **Trích xuất Text (OCR / PDF Parser)**: Sử dụng các công cụ như `pdfplumber` hoặc `PaddleOCR` (với văn bản scan) để lấy text.
3. **Làm sạch & Cấu trúc hóa**: Chạy script Regex để phân tách các "Điều", "Khoản". Lưu lại dưới dạng `DocumentChunk` để đảm bảo khi LLM trích xuất, nó có thể tham chiếu ngược lại đoạn text gốc (thuộc tính `nguon` / `dieu`).

---

## 5. QUY TRÌNH GÁN NHÃN (ANNOTATION) CHO CÁC THỰC THỂ PHÁP CHẾ

Để có tập Test chuẩn xác (Gold Standard) phục vụ đánh giá, 2 thành viên sẽ tiến hành gán nhãn thủ công cho khoảng 15-20 văn bản đại diện.

### 5.1 Gán nhãn Sự kiện hiệu lực (suKienHieuLuc)
- **Đầu vào**: Các điều khoản ở cuối văn bản (thường là Điều "Hiệu lực thi hành").
- **Nhãn cần gán**: `văn bản bị thay thế/bãi bỏ`, `văn bản mới`, `lý do` (thay thế, bãi bỏ một phần/toàn bộ).

### 5.2 Gán nhãn Nghĩa vụ (nghiaVu)
- **Đầu vào**: Các điều khoản quy định trách nhiệm thực hiện.
- **Nhãn cần gán**: `chủ thể` (ai làm), `hành động/nội dung`, `hạn chót` (nếu có), `loại` (đào tạo, tài chính, báo cáo...).

### 5.3 Gán nhãn Con số chốt (conSoChot)
- **Đầu vào**: Các định mức, tỷ lệ, thời gian chuẩn.
- **Nhãn cần gán**: `giá trị` (con số + đơn vị), `ý nghĩa` (mô tả ngắn gọn).

### 5.4 Quan hệ Rà soát chéo (Cross-Auditing)
- Xác định thủ công các văn bản nội bộ của trường đang trích dẫn sai/trích dẫn Luật đã hết hiệu lực để làm bộ test cho tính năng Cảnh báo pháp lý.

---

## 6. PHÂN CHIA TẬP DỮ LIỆU

Vì tiếp cận theo hướng dùng LLM (Zero-shot/Few-shot prompt) thay vì huấn luyện (train), toàn bộ dữ liệu gán nhãn thủ công sẽ được dùng làm **Tập Kiểm thử (Test Set)**.

| Tập | Nguồn | Quy mô | Mục đích |
|---|---|---|---|
| **Test Set (Gold Standard)** | 15-20 văn bản chọn lọc (gồm cả văn bản Bộ và Quy chế Trường) | 100% dữ liệu gán nhãn tay | Đánh giá độ chính xác (Precision/Recall) của pipeline bóc tách tự động bằng AI |
| **Tập Demo (Unlabeled)** | Các văn bản còn lại thu thập được | Tùy ý | Chạy thực tế trên hệ thống để trình diễn UI/UX |

---

## 7. KIỂM SOÁT CHẤT LƯỢNG DỮ LIỆU

- **Cross-Annotation**: Ít nhất 5 văn bản đầu tiên phải được cả 2 thành viên cùng gán nhãn độc lập. Sau đó đối chiếu để thống nhất tiêu chí (Inter-Annotator Agreement) trước khi chia nhau gán nhãn các văn bản còn lại.
- **Độ phủ (Coverage)**: Đảm bảo tập Test có đủ các trường hợp khó (ví dụ: bãi bỏ một phần, hạn chót được diễn đạt vòng vèo "trong vòng 30 ngày kể từ ngày...").

---

## 8. VẤN ĐỀ PHÁP LÝ & ĐẠO ĐỨC DỮ LIỆU

- Văn bản quy phạm pháp luật công khai không thuộc diện bảo hộ bản quyền.
- Các tài liệu nội bộ của trường cần được làm mờ (anonymize) các thông tin nhạy cảm (nếu có) trước khi đưa vào hệ thống demo.

---

## 9. TIMELINE THU THẬP DỮ LIỆU

| Thời điểm | Công việc |
|---|---|
| Tuần 1-2 | Thu thập PDF/Docx của 30-50 văn bản; Xây dựng script parse PDF ra JSON cấu trúc (Điều/Khoản). |
| Tuần 3-4 | Gán nhãn thủ công (Gold Standard) cho 15-20 văn bản (Nghĩa vụ, Con số, Sự kiện hiệu lực). |
| Tuần 5-6 | Thử nghiệm Prompt LLM để tự động bóc tách; đối chiếu kết quả với tập Test. |
| Tuần 7-8 | Hoàn thiện dữ liệu cho Cây văn bản và Rà soát chéo (Cross-Auditing). |
| Tuần 9-10| Chạy toàn bộ pipeline để tạo ra file `data.ts` cuối cùng phục vụ UI Demo. |

---
*Kế hoạch này đảm bảo tính khả thi và tập trung trực tiếp vào giá trị cốt lõi mới của hệ thống: Biến văn bản pháp luật tĩnh thành cơ sở dữ liệu có thể hành động (Actionable Insights).*
