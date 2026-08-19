# TÀI LIỆU THIẾT KẾ GIAO DIỆN (UI/UX SPEC)
## Hệ Sinh Thái "DAU Second Brain"

| | |
|---|---|
| **Phiên bản** | 1.0 |
| **Tài liệu liên quan** | Đặc tả Yêu cầu Chức năng (SRS) — tham chiếu UC-01 đến UC-07 |
| **Phạm vi** | 4 màn hình cốt lõi cho bản demo 12 tuần |

---

## MỤC LỤC
1. Nguyên tắc thiết kế
2. Sơ đồ luồng màn hình
3. Hệ thống quy ước thị giác (Design System)
4. Đặc tả chi tiết từng màn hình
5. Trạng thái đặc biệt cần thiết kế (Empty / Loading / Error states)

---

## 1. NGUYÊN TẮC THIẾT KẾ

1. **Trích dẫn luôn hiển thị, không ẩn giấu** — mọi nội dung do AI sinh ra (tóm tắt, câu trả lời, khung báo cáo) phải có chỉ dấu trích dẫn ngay trong tầm mắt người dùng, không phải bấm thêm để tìm.
2. **Trạng thái tin cậy phải nhìn thấy được** — người dùng cần phân biệt được ngay bằng màu sắc/badge: nội dung nào đã qua kiểm tra, nội dung nào bị cảnh báo, nội dung nào bị từ chối hiển thị.
3. **Không làm giao diện "quá mượt" đến mức che giấu rủi ro** — ví dụ câu bị loại do faithfulness thấp phải hiển thị rõ ràng ở đâu đó (màn hình rà soát), không được âm thầm biến mất không dấu vết.
4. **Ưu tiên tác vụ chính, giảm thao tác thừa** — cán bộ/giảng viên là người bận, luồng thao tác chính (tra cứu, tải báo cáo) không quá 2-3 bước.

---

## 2. SƠ ĐỒ LUỒNG MÀN HÌNH

```
                    ┌─────────────────────────┐
                    │   Màn hình 1: Dashboard   │
                    │   Tra cứu & Hỏi đáp        │
                    └───────────┬───────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                   │
              ▼                 ▼                   ▼
  ┌───────────────────┐ ┌───────────────┐ ┌──────────────────────┐
  │ Màn hình 4:         │ │ (danh sách VB) │ │ Màn hình 3:            │
  │ Đối chiếu trích dẫn │ │  → mở văn bản  │ │ Khung báo cáo gợi ý    │
  └─────────────────────┘ └───────┬────────┘ └──────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │ Màn hình 2:              │
                        │ Quản trị nội dung        │
                        │ (chỉ Cán bộ Đào tạo)     │
                        └───────────────────────┘
```

**Điểm vào (entry point):** Màn hình 1 (Dashboard) — mặc định cho mọi người dùng sau đăng nhập.
**Chỉ Cán bộ Đào tạo mới thấy:** Màn hình 2 (Quản trị nội dung), qua menu điều hướng riêng.
**Từ Dashboard, người dùng có thể:** mở chi tiết văn bản → xem đối chiếu trích dẫn (Màn hình 4), hoặc nếu văn bản có yêu cầu báo cáo → mở khung báo cáo gợi ý (Màn hình 3).

---

## 3. HỆ THỐNG QUY ƯỚC THỊ GIÁC (DESIGN SYSTEM)

### 3.1 Quy ước màu trạng thái

| Màu | Ý nghĩa | Áp dụng |
|---|---|---|
| Xanh lá (success) | Đạt / Còn hiệu lực / Độ tin cậy cao | Badge "Còn hiệu lực", điểm khớp ≥ ngưỡng |
| Vàng (warning) | Cần chú ý / Cần hành động | Badge "Cần báo cáo", "Cần rà soát" |
| Đỏ (danger) | Từ chối / Đã loại bỏ / Hết hiệu lực | Badge "Đã thay thế", câu bị loại do faithfulness thấp |
| Xanh dương (accent) | Thông tin trích dẫn, thao tác chính | Badge trích dẫn, icon thương hiệu |
| Xám (muted) | Thông tin phụ, siêu dữ liệu | Ngày tháng, số trang nguồn |

> Quy ước này áp dụng nhất quán trên toàn bộ 4 màn hình để người dùng không phải học lại ý nghĩa màu sắc ở mỗi nơi.

### 3.2 Thành phần dùng chung (Shared Components)

| Thành phần | Mô tả | Dùng ở màn hình |
|---|---|---|
| Citation Badge | Thẻ nhỏ hiển thị nguồn trích dẫn (số hiệu văn bản + điều/khoản), có thể bấm để mở nguồn gốc | 1, 3, 4 |
| Status Badge | Thẻ trạng thái văn bản (còn hiệu lực/cần báo cáo/đã thay thế) | 1, 2 |
| Faithfulness Score | Chỉ số % kèm màu, thể hiện độ tin cậy của một câu/đoạn | 4 (chi tiết), 2 (tổng hợp) |
| Document Card | Khối hiển thị 1 văn bản: tên, loại, trạng thái | 1, 2 |
| Chat Bubble | Khối hội thoại hỏi-đáp, phân biệt người dùng/hệ thống | 1 |

---

## 4. ĐẶC TẢ CHI TIẾT TỪNG MÀN HÌNH

### Màn hình 1 — Dashboard Tra cứu & Hỏi đáp

**Mục đích:** Điểm vào chính, phục vụ UC-06 (tra cứu/hỏi đáp) và tổng quan hệ thống.
**Actor:** Giảng viên, Cán bộ Đào tạo

**Thành phần giao diện:**
| Vùng | Nội dung |
|---|---|
| Thanh trên cùng | Logo hệ thống, tên đơn vị đăng nhập |
| Ô tìm kiếm/hỏi đáp | Input dạng chat, placeholder gợi ý loại câu hỏi |
| Thẻ thống kê | 3 số liệu nhanh: văn bản đã xử lý, faithfulness trung bình, số câu hỏi đã trả lời |
| Khung hội thoại | Hiển thị câu hỏi gần nhất + câu trả lời kèm Citation Badge |
| Danh sách văn bản gần đây | Document Card + Status Badge, bấm vào để mở chi tiết văn bản |

**Hành vi tương tác:**
- Người dùng gõ câu hỏi → hệ thống hiện trạng thái "đang tìm..." → trả lời kèm trích dẫn (theo UC-06).
- Nếu không đủ căn cứ trả lời → hiển thị thông báo rõ ràng "Không tìm thấy thông tin liên quan", **không hiển thị câu trả lời mơ hồ**.
- Bấm vào Citation Badge → mở văn bản gốc đúng vị trí điều/khoản được trích dẫn.
- Bấm vào 1 văn bản trong danh sách → điều hướng sang chi tiết văn bản (dẫn tới Màn hình 4, và Màn hình 3 nếu có yêu cầu báo cáo).

### Màn hình 2 — Quản trị nội dung

**Mục đích:** Phục vụ UC-01 (nạp văn bản) và UC-04 (rà soát cảnh báo).
**Actor:** Cán bộ Phòng Đào tạo (không hiển thị cho Giảng viên)

**Thành phần giao diện:**
| Vùng | Nội dung |
|---|---|
| Nút "Nạp văn bản mới" | Mở luồng upload |
| Vùng kéo-thả (Dropzone) | Chấp nhận PDF/ảnh, hiển thị hướng dẫn |
| Danh sách hàng đợi xử lý | Từng dòng: tên văn bản, bước xử lý hiện tại, trạng thái (Đang xử lý / Hoàn tất / Cần rà soát) |
| Banner cảnh báo | Xuất hiện khi có văn bản bị loại câu do faithfulness thấp, mô tả ngắn + link tới chi tiết |

**Hành vi tương tác:**
- Upload file → chuyển ngay sang trạng thái "Đang xử lý" trong danh sách hàng đợi (theo UC-01).
- Trạng thái hàng đợi cập nhật theo thời gian thực khi từng bước (OCR → phân loại → tóm tắt → kiểm tra faithfulness) hoàn tất.
- Văn bản có cảnh báo → banner vàng/đỏ xuất hiện, bấm vào mở đúng Màn hình 4 của văn bản đó để cán bộ rà soát (theo UC-04).

### Màn hình 3 — Khung báo cáo gợi ý

**Mục đích:** Phục vụ UC-05.
**Actor:** Giảng viên

**Thành phần giao diện:**
| Vùng | Nội dung |
|---|---|
| Tiêu đề + nguồn | Tên báo cáo, văn bản căn cứ |
| Badge thông tin | Hạn nộp, đơn vị chịu trách nhiệm (trích xuất tự động) |
| Bản xem trước khung báo cáo | 4 mục: Căn cứ pháp lý (có Citation Badge), Nội dung báo cáo (đề mục), Số liệu (viền nét đứt, để trống), Kết luận (viền nét đứt, để trống) |
| Nút "Tải file Word" | Xuất file .docx theo đúng khung xem trước |

**Hành vi tương tác:**
- Mục "Số liệu" và "Kết luận" **luôn** hiển thị bằng khung viền nét đứt kèm chú thích "để trống" — đây là quy ước bắt buộc, không được thay bằng nội dung do AI sinh, để nhất quán với ràng buộc FR-11 trong SRS.
- Bấm "Tải file Word" → tải file có cấu trúc y hệt bản xem trước.

### Màn hình 4 — Đối chiếu trích dẫn

**Mục đích:** Phục vụ UC-07 (và hỗ trợ UC-04 khi cán bộ rà soát).
**Actor:** Giảng viên, Cán bộ Phòng Đào tạo

**Thành phần giao diện:**
| Vùng | Nội dung |
|---|---|
| Tiêu đề văn bản + Status Badge | Tên văn bản, trạng thái hiệu lực |
| Danh sách đối chiếu | Mỗi khối: câu tóm tắt, nguồn (điều/khoản + trang), Faithfulness Score |
| Khối câu bị loại | Hiển thị mờ + gạch ngang, kèm icon cảnh báo và nhãn "Đã loại bỏ" thay vì ẩn hoàn toàn |

**Hành vi tương tác:**
- Mỗi khối đối chiếu là độc lập, không cần thao tác gì thêm để xem — đúng nguyên tắc "trích dẫn luôn hiển thị".
- Câu bị loại **vẫn hiển thị** (ở dạng mờ/gạch ngang) thay vì biến mất — mục đích minh chứng cho người xem (kể cả hội đồng chấm đồ án) rằng cơ chế lọc đang hoạt động thật, không phải "giấu lỗi".

---

## 5. TRẠNG THÁI ĐẶC BIỆT CẦN THIẾT KẾ

| Trạng thái | Màn hình | Mô tả hiển thị |
|---|---|---|
| Chưa có văn bản nào | 1, 2 | Thông báo hướng dẫn cán bộ nạp văn bản đầu tiên |
| Đang xử lý (loading) | 1 (hỏi đáp), 2 (hàng đợi) | Chỉ báo dạng spinner/dòng chữ "Đang tìm..." / "Đang xử lý...", không để trắng màn hình |
| Không tìm thấy câu trả lời | 1 | Thông báo trung thực "Không tìm thấy thông tin liên quan", kèm gợi ý thử câu hỏi khác |
| Toàn bộ tóm tắt bị loại | 2, 4 | Thông báo rõ "Không thể tóm tắt tự động — cần xử lý thủ công", không hiển thị bản tóm tắt rỗng gây hiểu lầm |
| Lỗi upload/OCR | 2 | Thông báo lỗi cụ thể (sai định dạng / chất lượng ảnh thấp), hướng dẫn khắc phục |

---

*Ghi chú: 4 màn hình trên đã được dựng bản mô phỏng trực quan (mockup) trong quá trình trao đổi trước khi viết tài liệu này — dùng làm tham chiếu hình ảnh khi trình bày trước GVHD hoặc đưa vào slide bảo vệ đề cương.*
