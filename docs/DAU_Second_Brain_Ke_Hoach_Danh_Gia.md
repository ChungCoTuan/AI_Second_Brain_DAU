# KẾ HOẠCH ĐÁNH GIÁ & TIÊU CHÍ NGHIỆM THU CHI TIẾT
## Hệ Sinh Thái "DAU Second Brain"

| | |
|---|---|
| **Phiên bản** | 2.0 |
| **Tài liệu liên quan** | SRS, Kế hoạch Dữ liệu, Tài liệu Kiến trúc |
| **Mục đích** | Đánh giá độ chính xác của hệ thống bóc tách dữ liệu pháp chế (Information Extraction) và chất lượng giao diện (Dashboard/UIUX) |

---

## MỤC LỤC
1. Mục tiêu kế hoạch đánh giá
2. Các chiều đánh giá (Evaluation Dimensions)
3. Chi tiết từng Metric & Ngưỡng đề xuất
4. Tập dữ liệu dùng để đánh giá
5. Bảng Tiêu chí Nghiệm thu tổng hợp (Go/No-Go Checklist)
6. Mẫu trình bày kết quả trong báo cáo đồ án

---

## 1. MỤC TIÊU KẾ HOẠCH ĐÁNH GIÁ

Với sự dịch chuyển yêu cầu sang hướng **Bóc tách Pháp chế & Kiểm định**, mục tiêu cốt lõi của việc đánh giá không còn nằm ở chất lượng Tóm tắt (Summarization) mà nằm ở **Độ chính xác khi trích xuất dữ liệu có cấu trúc** từ văn bản thô. Hệ thống phải đảm bảo việc tự động bóc tách các "Sự kiện hiệu lực", "Nghĩa vụ", và "Con số chốt" đạt độ tin cậy cao nhất để phục vụ cho các tính năng Rà soát chéo (Cross-Auditing).

---

## 2. CÁC CHIỀU ĐÁNH GIÁ (EVALUATION DIMENSIONS)

| # | Chiều đánh giá | Trả lời câu hỏi | Phục vụ Tính năng UI |
|---|---|---|---|
| 1 | Bóc tách Sự kiện hiệu lực | AI có tìm đúng văn bản cũ bị thay thế/bãi bỏ không? | Mọi lần đổi hiệu lực, Văn bản khai tử |
| 2 | Bóc tách Nghĩa vụ | AI có xác định đúng ai phải làm gì, hạn chót ra sao? | Việc phải làm, Hạn chót & mốc |
| 3 | Bóc tách Con số chốt | Định mức, tỷ lệ phần trăm, thời gian chuẩn có đúng không? | Sổ tra ngưỡng & định mức |
| 4 | Cảnh báo Pháp lý (Cross-Auditing) | Phát hiện chính xác các quy chế nội bộ đang trích dẫn sai Luật? | Rà soát ưu tiên, Đồ thị ảnh hưởng |
| 5 | Tốc độ và Trải nghiệm (UI/UX) | Giao diện React hiển thị mượt mà dữ liệu lớn không? | Toàn bộ Dashboard |

---

## 3. CHI TIẾT TỪNG METRIC & NGƯỠNG ĐỀ XUẤT

### 3.1 Đánh giá Bóc tách Sự kiện hiệu lực (suKienHieuLuc)
| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Precision / Recall cho Số hiệu cũ | Khớp chính xác (Exact match) với nhãn Gold Standard | F1 ≥ 0.90 |
| Tỷ lệ xác định đúng Lý do | Bãi bỏ/Thay thế/Sửa đổi (Accuracy) | ≥ 95% |

### 3.2 Đánh giá Bóc tách Nghĩa vụ (nghiaVu)
| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Độ chính xác Chủ thể (Actor) | Trích xuất đúng đối tượng phải thực hiện (Precision) | ≥ 85% |
| Khớp Hạn chót (Deadline) | Khớp định dạng ngày/tháng hoặc thời gian tương đối | ≥ 85% |
| Tính trọn vẹn Nội dung | Semantic Similarity giữa nội dung trích xuất và câu gốc (do LLM sinh) | BERTScore / Cosine Similarity ≥ 0.85 |

### 3.3 Đánh giá Bóc tách Con số chốt (conSoChot)
| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Exact Match Giá trị | Trích xuất chính xác con số (ví dụ: "10%", "30 ngày") | ≥ 95% (Rất quan trọng) |

### 3.4 Đánh giá Rà soát chéo (Cross-Auditing)
| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Tỷ lệ phát hiện (Detection Rate) | Số lượng liên kết trích dẫn "chết" được hệ thống cảnh báo / Tổng số liên kết "chết" thực tế trong tập test | 100% |

### 3.5 Hiệu năng Giao diện
| Metric | Cách tính | Ngưỡng đề xuất |
|---|---|---|
| Thời gian render lần đầu | Đo bằng React DevTools cho các danh sách dài (ví dụ trang Nghĩa vụ > 100 item) | ≤ 1 giây |
| Thao tác Filter / Search | Thời gian đáp ứng khi nhập từ khóa tìm kiếm (Sử dụng State React) | Mượt mà (≤ 200ms) |

---

## 4. TẬP DỮ LIỆU DÙNG ĐỂ ĐÁNH GIÁ

| Tập | Nguồn | Quy mô | Dùng để đo |
|---|---|---|---|
| **Gold Standard Test Set** | Văn bản đã gán nhãn thủ công (xem Kế hoạch dữ liệu) | 15-20 văn bản | F1, Precision, Recall cho các task IE |
| **Cross-Auditing Mock Set** | Các quy chế trường tự chế hoặc lấy thực tế có chứa liên kết đến luật cũ đã hết hạn | 5-10 trường hợp cảnh báo | Đánh giá tính năng Rà soát chéo |

---

## 5. BẢNG TIÊU CHÍ NGHIỆM THU TỔNG HỢP (GO/NO-GO CHECKLIST)

| # | Tiêu chí | Đạt/Không đạt |
|---|---|---|
| 1 | Bóc tách thành công Sự kiện hiệu lực với F1 ≥ 0.90 | ☐ |
| 2 | Bóc tách thành công Nghĩa vụ (Chủ thể, Hạn chót) đạt F1 ≥ 0.85 | ☐ |
| 3 | Trích xuất Con số chốt chính xác (Exact match) ≥ 95% | ☐ |
| 4 | Hệ thống hiển thị Cảnh báo đúng 100% các văn bản nội bộ trỏ sai Luật hết hạn | ☐ |
| 5 | Giao diện React hiển thị toàn bộ module (Dashboard, Thresholds, Obligations, Cross-Auditing) đúng thiết kế UI | ☐ |
| 6 | Tính năng DocumentDetailDrawer (Popup trượt) hoạt động chính xác cho mọi văn bản | ☐ |
| 7 | Tốc độ lọc/tìm kiếm trên Frontend xử lý tốt danh sách hàng trăm dòng mà không bị giật lag | ☐ |

> **Ghi chú**: Bảng này phản ánh chính xác 5 yêu cầu bổ sung của GVHD về "Sổ tra ngưỡng", "Việc phải làm", và "Rà soát chéo".

---

## 6. MẪU TRÌNH BÀY KẾT QUẢ TRONG BÁO CÁO ĐỒ ÁN

Khuyến nghị trình bày kết quả trong báo cáo theo cấu trúc:
1. **Bảng so sánh độ chính xác (Precision/Recall/F1)** của mô hình IE đối với 3 loại dữ liệu chính: Sự kiện, Nghĩa vụ, Con số.
2. **Minh họa Rà soát chéo**: Đưa ra 1-2 ví dụ quy chế nội bộ của trường bị phát hiện sai phạm nhờ đồ thị liên kết.
3. **Đánh giá hiệu suất Frontend**: Chứng minh việc chuyển đổi từ DOM Vanilla JS sang React Hooks đã giúp tăng tốc độ phản hồi tìm kiếm/lọc văn bản như thế nào.
4. Bảng Go/No-Go Checklist đã hoàn thành (mục 5).
