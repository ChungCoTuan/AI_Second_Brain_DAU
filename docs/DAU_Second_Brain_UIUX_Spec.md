# TÀI LIỆU THIẾT KẾ GIAO DIỆN (UI/UX SPEC)
## Hệ Sinh Thái "DAU Second Brain"

| | |
|---|---|
| **Phiên bản** | 1.0 |
| **Tài liệu liên quan** | Đặc tả Yêu cầu Chức năng (SRS) — tham chiếu UC-01 đến UC-09 |
| **Phạm vi** | 6 màn hình cốt lõi cho bản demo 12 tuần (2 màn hình mới bổ sung: Rà soát & Duyệt, Cây văn bản) |

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
        ┌───────────────┬───────┼───────┬───────────────┐
        │               │       │       │               │
        ▼               ▼       ▼       ▼               ▼
┌───────────────┐ ┌───────────┐ (mở 1 VB) ┌──────────┐ ┌─────────────┐
│ Màn hình 4:     │ │ Màn hình 6:│         │Màn hình 3:│ │  (chi tiết   │
│ Đối chiếu       │ │ Cây văn bản│         │Khung báo  │ │   văn bản)   │
│ trích dẫn       │ │            │         │cáo gợi ý  │ │              │
└───────┬─────────┘ └───────────┘         └──────────┘ └─────────────┘
        │ (nếu có câu contradiction/neutral)
        ▼
┌─────────────────────┐
│ Màn hình 5:            │
│ Rà soát & Duyệt        │
│ (chỉ Cán bộ Đào tạo)   │
└─────────────────────┘

┌───────────────────────┐
│ Màn hình 2:              │
│ Dashboard theo chủ đề    │  ← điểm vào riêng cho Cán bộ Đào tạo
│ (chỉ Cán bộ Đào tạo)     │     (thay cho "Quản trị nội dung" cũ)
└───────────┬───────────────┘
            │ bấm vào 1 chủ đề → danh sách văn bản → mở chi tiết (như trên)
            │ bấm "Cần rà soát" → Màn hình 5
            ▼
      (danh sách văn bản theo chủ đề)
```

**Điểm vào (entry point):** Màn hình 1 (Dashboard) — mặc định cho mọi người dùng sau đăng nhập.
**Chỉ Cán bộ Đào tạo mới thấy:** Màn hình 2 (Dashboard theo chủ đề) và Màn hình 5 (Rà soát & Duyệt), qua menu điều hướng riêng.
**Từ Dashboard hoặc Dashboard theo chủ đề, người dùng có thể:** mở chi tiết văn bản → xem đối chiếu trích dẫn (Màn hình 4) và văn bản liên quan (Màn hình 6), hoặc nếu văn bản có yêu cầu báo cáo → mở khung báo cáo gợi ý (Màn hình 3).
**Đường dẫn mới quan trọng:** văn bản `pending_review` (có câu `contradiction`/`neutral`) → banner trên Màn hình 2 hoặc Màn hình 4 dẫn thẳng tới Màn hình 5 để xử lý.

---

## 3. HỆ THỐNG QUY ƯỚC THỊ GIÁC (DESIGN SYSTEM)

### 3.1 Quy ước màu trạng thái

| Màu | Ý nghĩa | Áp dụng |
|---|---|---|
| Xanh lá (success) | Đạt / Còn hiệu lực / `entailment` / Đã `published` | Badge "Còn hiệu lực", nhãn NLI `entailment`, trạng thái văn bản "Đã published" |
| Vàng (warning) | Cần chú ý / Cần hành động / `neutral` | Badge "Cần báo cáo", nhãn NLI `neutral`, trạng thái "Chưa phân loại chủ đề" |
| Đỏ (danger) | Từ chối / `contradiction` / Hết hiệu lực | Badge "Đã thay thế", nhãn NLI `contradiction`, trạng thái "Đang chờ rà soát" |
| Xanh dương (accent) | Thông tin trích dẫn, thao tác chính | Badge trích dẫn, icon thương hiệu |
| Xám (muted) | Thông tin phụ, siêu dữ liệu | Ngày tháng, số trang nguồn, nhãn "Đã xác nhận thủ công" |

> Quy ước này áp dụng nhất quán trên toàn bộ 6 màn hình để người dùng không phải học lại ý nghĩa màu sắc ở mỗi nơi. **Lưu ý quan trọng:** đỏ dùng chung cho cả "hết hiệu lực" và "contradiction" — 2 khái niệm khác nhau — nên luôn đi kèm text rõ ràng, không dùng màu đơn độc để phân biệt.

### 3.2 Thành phần dùng chung (Shared Components)

| Thành phần | Mô tả | Dùng ở màn hình |
|---|---|---|
| Citation Badge | Thẻ nhỏ hiển thị nguồn trích dẫn (số hiệu văn bản + điều/khoản), có thể bấm để mở nguồn gốc | 1, 3, 4, 5 |
| Status Badge | Thẻ trạng thái văn bản: còn hiệu lực/đã thay thế/**đã published/đang chờ rà soát** | 1, 2, 4 |
| NLI Label Badge *(mới)* | Thẻ hiển thị nhãn `entailment`/`contradiction`/`neutral` kèm màu tương ứng — thay thế cách gọi "Faithfulness Score" đơn thuần bằng số % | 4, 5 |
| Priority Indicator *(mới)* | Chỉ báo mức độ ưu tiên rà soát (contradiction = cao, neutral = thấp hơn), dùng để sắp xếp danh sách | 5 |
| Manual Override Badge *(mới)* | Nhãn xám "Đã xác nhận thủ công" — gắn cho câu cán bộ chọn giữ nguyên dù điểm NLI thấp, để không lẫn với câu tự động đạt | 4, 5 |
| Document Card | Khối hiển thị 1 văn bản: tên, loại, chủ đề, trạng thái | 1, 2 |
| Topic Card *(mới)* | Thẻ đại diện 1 chủ đề, hiển thị tên + số lượng văn bản, bấm để xem danh sách | 2 |
| Relation List *(mới)* | Danh sách văn bản liên quan, chia 2 nhóm (quan hệ trực tiếp / quan hệ ngữ nghĩa) kèm nhãn mức độ áp dụng | 6 |
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
- Người dùng gõ câu hỏi → hệ thống hiện trạng thái "đang tìm..." → trả lời kèm trích dẫn, **chỉ dựa trên văn bản đã `published`** (theo UC-06).
- Nếu không đủ căn cứ trả lời → hiển thị thông báo rõ ràng "Không tìm thấy thông tin liên quan", **không hiển thị câu trả lời mơ hồ**.
- Bấm vào Citation Badge → mở văn bản gốc đúng vị trí điều/khoản được trích dẫn.
- Bấm vào 1 văn bản trong danh sách → điều hướng sang chi tiết văn bản (dẫn tới Màn hình 4 — Đối chiếu trích dẫn, Màn hình 6 — Cây văn bản, và Màn hình 3 nếu có yêu cầu báo cáo).

### Màn hình 2 — Dashboard theo chủ đề

**Mục đích:** Phục vụ UC-09 (duyệt văn bản theo chủ đề) và UC-01 (nạp văn bản) — **thay thế hoàn toàn** cách bố trí "hàng đợi phẳng" trước đây theo yêu cầu GVHD.
**Actor:** Cán bộ Phòng Đào tạo (không hiển thị cho Giảng viên)

**Thành phần giao diện:**
| Vùng | Nội dung |
|---|---|
| Lưới thẻ chủ đề | Mỗi Topic Card = 1 chủ đề (Đào tạo, Tuyển sinh, Tài chính — Học phí, Nhân sự, Cơ sở vật chất, Khác), hiển thị số lượng văn bản; thêm 1 thẻ riêng "Chưa phân loại" |
| Banner "Cần rà soát" | Đếm số văn bản đang `pending_review`, bấm vào dẫn thẳng tới Màn hình 5 |
| Khu vực nạp văn bản (giữ nguyên từ bản trước) | Nút "Nạp văn bản mới" + Vùng kéo-thả (Dropzone) — đặt trong 1 khu vực riêng, không chiếm vị trí trung tâm của màn hình vì đây không còn là tác vụ chính khi mở màn hình |
| Danh sách hàng đợi xử lý (thu gọn) | Vẫn giữ, nhưng đặt trong tab/khu vực phụ "Đang xử lý" tách khỏi lưới chủ đề — từng dòng: tên văn bản, bước xử lý hiện tại, trạng thái |
| Danh sách văn bản trong 1 chủ đề (khi bấm vào Topic Card) | Document Card cho từng văn bản, kèm Status Badge (`published`/`pending_review`), loại văn bản |

**Hành vi tương tác:**
- Mở màn hình → mặc định hiển thị **lưới chủ đề** trước tiên (không phải hàng đợi xử lý), đúng theo yêu cầu "dashboard dành cho các chủ đề".
- Bấm vào 1 Topic Card → chuyển sang danh sách văn bản thuộc chủ đề đó.
- Upload file mới (UC-01) → chuyển ngay sang trạng thái "Đang xử lý" trong khu vực hàng đợi riêng; sau khi phân loại xong (UC-02) → tự động xuất hiện trong đúng Topic Card tương ứng.
- Banner "Cần rà soát" luôn hiển thị ở đầu trang bất kể đang xem chủ đề nào — không để cán bộ phải tự tìm văn bản có vấn đề.
- Văn bản chưa phân loại được chủ đề (độ tin cậy thấp) → rơi vào Topic Card "Chưa phân loại", không tự ý gán bừa (theo UC-09, luồng ngoại lệ).

### Màn hình 3 — Khung báo cáo gợi ý

**Mục đích:** Phục vụ UC-05 — **mỗi văn bản hiển thị khung báo cáo riêng theo Thư viện Template**, không dùng chung 1 bố cục.
**Actor:** Giảng viên

**Thành phần giao diện:**
| Vùng | Nội dung |
|---|---|
| Tiêu đề + nguồn | Tên báo cáo, văn bản căn cứ |
| Badge thông tin | Hạn nộp, đơn vị chịu trách nhiệm (trích xuất tự động), **tên template đang dùng** (ví dụ "Mẫu: Báo cáo định kỳ" hoặc "Tự dựng từ văn bản gốc" nếu không khớp mẫu nào) |
| Bản xem trước khung báo cáo | Các mục **thay đổi theo template đã chọn** — luôn có Căn cứ pháp lý (có Citation Badge) và các mục để trống (Số liệu/Kết luận hoặc tương đương), nhưng số lượng và tên đề mục nội dung khác nhau tùy loại văn bản |
| Nút "Tải file Word" | Xuất file .docx theo đúng khung xem trước |

**Ví dụ minh họa 2 template khác nhau (để thấy rõ không dùng chung 1 khung):**
- *Báo cáo định kỳ* (ví dụ: báo cáo quý về đào tạo tín chỉ): I. Căn cứ pháp lý → II. Kết quả thực hiện theo từng chỉ tiêu → III. Số liệu → IV. Khó khăn vướng mắc → V. Kiến nghị.
- *Báo cáo đột xuất* (ví dụ: báo cáo sự việc theo yêu cầu công văn): I. Căn cứ pháp lý → II. Diễn biến sự việc → III. Biện pháp đã xử lý → IV. Đề xuất hướng xử lý tiếp theo.

**Hành vi tương tác:**
- Mục để trống (số liệu/nội dung thực tế) **luôn** hiển thị bằng khung viền nét đứt kèm chú thích "để trống", bất kể đang dùng template nào — quy ước bắt buộc, nhất quán với ràng buộc FR-11 trong SRS.
- Nếu hệ thống không tìm được template khớp, badge "Tự dựng từ văn bản gốc" hiển thị rõ để giảng viên biết đây không phải mẫu đã được kiểm chứng nhiều lần.
- Bấm "Tải file Word" → tải file có cấu trúc y hệt bản xem trước.

### Màn hình 4 — Đối chiếu trích dẫn

**Mục đích:** Phục vụ UC-07 (đối chiếu) và liên kết sang UC-04 khi cần rà soát.
**Actor:** Giảng viên, Cán bộ Phòng Đào tạo

**Thành phần giao diện:**
| Vùng | Nội dung |
|---|---|
| Tiêu đề văn bản + Status Badge | Tên văn bản, trạng thái hiệu lực **và trạng thái xuất bản** (`Đã published` / `Đang chờ rà soát`) |
| Danh sách đối chiếu | Mỗi khối: câu tóm tắt, nguồn (điều/khoản + trang), **NLI Label Badge** (thay cho chỉ hiển thị % đơn thuần) |
| Khối câu `contradiction`/`neutral` | Hiển thị mờ + gạch ngang (nếu đã bị loại) hoặc viền cảnh báo (nếu đang chờ xử lý), kèm nút "Xem trong Rà soát" dẫn sang Màn hình 5 |
| Banner trạng thái văn bản | Nếu văn bản đang `pending_review`: banner đỏ ghi rõ "Văn bản chưa hoàn thiện — còn N câu chờ rà soát", link sang Màn hình 5 |

**Hành vi tương tác:**
- Mỗi khối đối chiếu là độc lập, không cần thao tác gì thêm để xem — đúng nguyên tắc "trích dẫn luôn hiển thị".
- Câu bị gắn cờ **vẫn hiển thị** (không biến mất) — mục đích minh chứng cho người xem (kể cả hội đồng chấm đồ án) rằng cơ chế lọc đang hoạt động thật, không phải "giấu lỗi".
- Câu đã qua rà soát và được giữ dù điểm thấp → hiển thị kèm Manual Override Badge ("Đã xác nhận thủ công"), không trộn lẫn với câu tự động đạt `entailment`.

### Màn hình 5 — Rà soát & Duyệt (Cần rà soát)

**Mục đích:** Phục vụ UC-04 — màn hình dành riêng cho human-in-the-loop, nơi cán bộ xử lý các câu bị gắn nhãn `contradiction`/`neutral` trước khi văn bản được `published`.
**Actor:** Cán bộ Phòng Đào tạo (không hiển thị cho Giảng viên)

**Thành phần giao diện:**
| Vùng | Nội dung |
|---|---|
| Danh sách hàng đợi rà soát | Sắp xếp theo Priority Indicator (`contradiction` lên đầu, `neutral` sau); mỗi mục ghi tên văn bản + số câu cần xử lý |
| Khối đối chiếu câu cần rà soát | Với văn bản đang mở: **chỉ hiển thị đúng các câu bị gắn cờ** (ví dụ 2/10 câu), mỗi câu đặt cạnh đoạn văn gốc tương ứng — không lẫn với 8 câu đã đạt |
| Vùng chỉnh sửa | Ô nhập cho phép cán bộ sửa trực tiếp câu tóm tắt (nếu chọn "Sửa & duyệt") |
| 3 nút hành động | "Duyệt giữ nguyên" / "Sửa & duyệt" / "Loại bỏ" cho từng câu |
| Thanh tiến độ văn bản | Ví dụ "1/2 câu đã xử lý" — cho biết còn bao nhiêu câu nữa văn bản mới chuyển `published` |
| Khu vực Audit Trail (mở rộng được) | Lịch sử: câu AI sinh ban đầu → câu sau sửa → người duyệt → thời điểm |

**Hành vi tương tác:**
- Bấm "Sửa & duyệt" → sau khi cán bộ nhập câu mới, hệ thống tự động gọi lại NLI và hiển thị kết quả revalidate ngay tại chỗ (đạt `entailment` hay vẫn chưa đạt) trước khi cho lưu.
- Nếu revalidate vẫn không đạt → hiện cảnh báo, yêu cầu cán bộ bấm xác nhận thêm 1 lần ("Vẫn giữ câu này dù độ tin cậy thấp?") trước khi chấp nhận.
- Khi thanh tiến độ đạt 100% (hết câu chờ) → hệ thống tự động chuyển văn bản sang `published` và hiển thị thông báo xác nhận ngay trên màn hình, không cần thao tác "publish" riêng.

### Màn hình 6 — Cây văn bản (Văn bản liên quan)

**Mục đích:** Phục vụ UC-08 — hiển thị văn bản liên quan và mức độ áp dụng cho trường khi xem chi tiết 1 văn bản.
**Actor:** Giảng viên, Cán bộ Phòng Đào tạo

**Thành phần giao diện:**
| Vùng | Nội dung |
|---|---|
| Badge mức độ áp dụng cho trường | Hiển thị ngay đầu trang: "Áp dụng trực tiếp — có quy chế nội bộ trường cụ thể hóa" / "Áp dụng chung, chưa có văn bản nội bộ tương ứng" / "Chỉ mang tính tham khảo" |
| Relation List — Quan hệ trực tiếp | Danh sách văn bản mà văn bản này căn cứ vào, hoặc thay thế/bị thay thế (phát hiện bằng rule) |
| Relation List — Quan hệ ngữ nghĩa | Danh sách văn bản `published` khác có nội dung gần nhất (tận dụng lại Vector DB của Màn hình 1), kèm % độ tương đồng |

**Hành vi tương tác:**
- Bấm vào 1 văn bản trong Relation List → điều hướng sang chi tiết văn bản đó (mở lại đúng bộ Màn hình 4/6 tương ứng).
- Nếu không tìm được văn bản liên quan nào đủ gần nghĩa → hiển thị "Chưa phát hiện văn bản liên quan" thay vì ép hiển thị kết quả không liên quan (theo UC-08, luồng ngoại lệ).
- 2 nhóm quan hệ hiển thị **tách biệt rõ ràng** (không gộp chung 1 danh sách) — để người dùng phân biệt được đâu là quan hệ chắc chắn (tường minh) và đâu là gợi ý (ngữ nghĩa, có thể không hoàn toàn chính xác).

---

## 5. TRẠNG THÁI ĐẶC BIỆT CẦN THIẾT KẾ

| Trạng thái | Màn hình | Mô tả hiển thị |
|---|---|---|
| Chưa có văn bản nào | 1, 2 | Thông báo hướng dẫn cán bộ nạp văn bản đầu tiên |
| Chủ đề chưa có văn bản | 2 | Topic Card hiển thị "0 văn bản", vẫn bấm được nhưng hiện thông báo trống thay vì lỗi |
| Đang xử lý (loading) | 1 (hỏi đáp), 2 (hàng đợi) | Chỉ báo dạng spinner/dòng chữ "Đang tìm..." / "Đang xử lý...", không để trắng màn hình |
| Không tìm thấy câu trả lời | 1 | Thông báo trung thực "Không tìm thấy thông tin liên quan", kèm gợi ý thử câu hỏi khác |
| Toàn bộ tóm tắt bị `contradiction` | 2, 4, 5 | Thông báo rõ "Không thể tóm tắt tự động — cần xử lý thủ công toàn bộ văn bản", không hiển thị bản tóm tắt rỗng gây hiểu lầm |
| Văn bản đang `pending_review` | 1, 2, 4, 6 | Không xuất hiện trong kết quả tra cứu (Màn hình 1) hoặc Cây văn bản (Màn hình 6) của văn bản khác; Status Badge màu đỏ "Đang chờ rà soát" |
| Hàng đợi rà soát trống | 5 | Thông báo tích cực "Không có câu nào cần rà soát" thay vì màn hình trống không rõ nghĩa |
| Không tìm thấy văn bản liên quan | 6 | "Chưa phát hiện văn bản liên quan" — không ép hiển thị kết quả không đủ liên quan |
| Lỗi upload/OCR | 2 | Thông báo lỗi cụ thể (sai định dạng / chất lượng ảnh thấp), hướng dẫn khắc phục |

---

*Ghi chú: Màn hình 1–4 đã được dựng bản mô phỏng trực quan (mockup) trong quá trình trao đổi trước khi viết tài liệu này. Màn hình 5 (Rà soát & Duyệt) và Màn hình 6 (Cây văn bản) là bổ sung mới theo yêu cầu GVHD, chưa có mockup trực quan — nên dựng mockup cho 2 màn hình này trước khi đưa vào slide bảo vệ đề cương, vì đây là 2 màn hình thể hiện rõ nhất cơ chế an toàn (human-in-the-loop) và điểm khác biệt mới (Cây văn bản) của đồ án.*
