# BẢNG PHÂN CÔNG CÔNG VIỆC NHÓM (RACI)
## Hệ Sinh Thái "DAU Second Brain"

| | |
|---|---|
| **Phiên bản** | 1.0 |
| **Tài liệu liên quan** | Tài liệu Kiến trúc (mục 3 — Scrum), toàn bộ Epic/Use Case đã đặc tả |
| **Áp dụng cho** | Nhóm 2 sinh viên, 12 tuần |

---

## MỤC LỤC
1. Thành viên & vai trò tổng quát
2. Giải thích ký hiệu RACI
3. Ma trận RACI theo Epic
4. Phân công chi tiết theo Sprint
5. Quy tắc phối hợp giữa 2 track
6. Ước lượng khối lượng công việc (Effort Estimation)
7. Xử lý khi mất cân bằng công việc

---

## 1. THÀNH VIÊN & VAI TRÒ TỔNG QUÁT

| Vai trò | Người đảm nhận | Track phụ trách chính |
|---|---|---|
| Thành viên 1 (TV1) | *(điền tên)* | Track A — Data & Pipeline (Ingestion, Extraction, NER, Report Suggestion, Dashboard/DevOps) |
| Thành viên 2 (TV2) | *(điền tên)* | Track B — AI Core (Fine-tune tóm tắt, Faithfulness/NLI, Embedding & RAG) |
| Giảng viên hướng dẫn (GVHD) | *(điền tên)* | Product Owner — định hướng, duyệt tiêu chí nghiệm thu, tham vấn kỹ thuật |

> Cách chia Track này giữ nguyên theo Tài liệu Kiến trúc (mục 3.1.1) — tài liệu này chỉ cụ thể hóa thêm mức độ trách nhiệm và lịch làm việc.

---

## 2. GIẢI THÍCH KÝ HIỆU RACI

| Ký hiệu | Ý nghĩa |
|---|---|
| **R** (Responsible) | Người trực tiếp thực hiện công việc |
| **A** (Accountable) | Người chịu trách nhiệm cuối cùng về chất lượng/kết quả (có thể trùng với R nếu công việc độc lập) |
| **C** (Consulted) | Người cần được hỏi ý kiến trước khi quyết định |
| **I** (Informed) | Người cần được thông báo kết quả, không tham gia quyết định |

---

## 3. MA TRẬN RACI THEO EPIC

| Epic / Hạng mục | TV1 (Track A) | TV2 (Track B) | GVHD |
|---|---|---|---|
| Thu thập & tiền xử lý dữ liệu (Sprint 0) | R, A | C | I |
| EPIC-1: Ingestion Service | R, A | C | I |
| EPIC-2: Extraction, Classification, NER | R, A | C | I |
| EPIC-3: Fine-tune mô hình tóm tắt | C | R, A | I |
| EPIC-3: Faithfulness/NLI check (Sprint 3 — cả 2 cùng làm) | R, A | R, A | C |
| EPIC-4: Report Suggestion | R, A | C | I |
| EPIC-5: Embedding + RAG Chatbot | C | R, A | I |
| EPIC-7: Dashboard & tích hợp end-to-end | R, A | R | I |
| EPIC-8: Đánh giá định lượng | R | R, A | C |
| EPIC-8: Viết báo cáo đồ án | R, A | R, A | C |
| Quyết định ngưỡng Faithfulness/tiêu chí nghiệm thu | C | C | **R, A** |
| Chuẩn bị & trình bày demo/bảo vệ | R, A | R, A | C |

> **Lưu ý:** Với EPIC-3 (phần Faithfulness) — mục quan trọng nhất của đồ án — cả 2 thành viên đều là R/A, nghĩa là **không ai được đứng ngoài phần này**, đúng theo nguyên tắc giảm rủi ro "chỉ 1 người hiểu phần lõi" đã nêu trong Risk Register của Tài liệu Kiến trúc.

---

## 4. PHÂN CÔNG CHI TIẾT THEO SPRINT

| Sprint | Tuần | TV1 — Track A | TV2 — Track B | Điểm đồng bộ (Sync point) |
|---|---|---|---|---|
| Sprint 0 | 1–2 | Thu thập văn bản GD&ĐT, thiết kế schema DocumentChunk | Tải & khảo sát dataset VietNews/VNDS, khảo sát mô hình BARTpho/ViT5 | Thống nhất schema dữ liệu trung gian trước khi tách việc (bắt buộc — theo Risk Register) |
| Sprint 1 | 3–4 | Xây Ingestion Service, chia đoạn Điều/Khoản | Chuẩn bị pipeline fine-tune, chạy baseline TextRank | Kiểm tra output của TV1 (chunk có ID) tương thích với input mà TV2 cần |
| Sprint 2 | 5–6 | Classification + NER cơ bản | Fine-tune BARTpho/ViT5 (bản đầu) trên dữ liệu công khai | Demo nội bộ giữa 2 người: dữ liệu đã trích xuất từ TV1 chạy thử qua model của TV2 |
| Sprint 3 | 7–8 | **Cùng làm:** tích hợp NLI + citation mapping | **Cùng làm:** tích hợp NLI + citation mapping | Cả 2 cùng ngồi code chung phần này — không tách việc |
| Sprint 4 | 9–10 | Report Suggestion template + trích xuất yêu cầu báo cáo | Embedding + RAG chatbot | Chạy thử độc lập 2 module, chuẩn bị ghép ở Sprint 5 |
| Sprint 5 | 11 | Hoàn thiện Dashboard, ghép nối toàn bộ pipeline | Hỗ trợ ghép nối phần AI vào Dashboard, kiểm thử end-to-end | Test toàn bộ luồng cùng nhau, danh sách lỗi cần sửa gấp |
| Sprint 6 | 12 | Chạy đánh giá phần dữ liệu/NER, viết phần kiến trúc-triển khai trong báo cáo | Chạy đánh giá ROUGE/BERTScore/Faithfulness, viết phần mô hình-kết quả trong báo cáo | Ghép báo cáo hoàn chỉnh, tổng duyệt trước khi nộp/demo |

---

## 5. QUY TẮC PHỐI HỢP GIỮA 2 TRACK

1. **Thống nhất "hợp đồng dữ liệu" (data contract) sớm nhất có thể** — cấu trúc `DocumentChunk` (mục 5 trong Tài liệu Kiến trúc) phải chốt xong trong Sprint 0, vì cả 2 track đều phụ thuộc vào nó. Thay đổi schema giữa chừng là rủi ro lớn nhất gây nghẽn tiến độ.
2. **Check-in ngắn hàng tuần** (15-20 phút): mỗi người báo cáo đã làm gì, đang vướng gì, có cần track kia hỗ trợ không — không cần họp dài, nhưng phải đều đặn để phát hiện sớm khi 2 track lệch nhau.
3. **Code review chéo bắt buộc**: mọi merge vào nhánh `develop` cần người còn lại xem qua, kể cả khi không hiểu sâu phần chuyên môn của track kia — mục đích chính là để cả 2 đều nắm được toàn cảnh hệ thống, không chỉ phần mình phụ trách.
4. **Ưu tiên demo nội bộ sớm và thường xuyên** (cuối mỗi sprint) thay vì để đến cuối kỳ mới ghép nối lần đầu — giảm rủi ro phát hiện lỗi tích hợp quá muộn.

---

## 6. ƯỚC LƯỢNG KHỐI LƯỢNG CÔNG VIỆC (EFFORT ESTIMATION)

| Hạng mục | Ước lượng giờ/người | Ghi chú |
|---|---|---|
| Sprint 0 (thu thập, thiết kế) | ~15-20 giờ/người | Bao gồm thời gian đọc tài liệu, thử nghiệm công cụ |
| Sprint 1-2 (xây nền tảng) | ~20-25 giờ/người/sprint | Phần code nhiều nhất |
| Sprint 3 (faithfulness — cả 2 cùng làm) | ~25-30 giờ/người | Phần khó nhất kỹ thuật, cần thời gian thử-sai |
| Sprint 4-5 (mở rộng, ghép nối) | ~20-25 giờ/người/sprint | |
| Sprint 6 (đánh giá, báo cáo) | ~15-20 giờ/người | Bao gồm thời gian viết báo cáo |
| **Tổng ước tính** | **~130-165 giờ/người trong 12 tuần** | Tương đương ~11-14 giờ/tuần/người — cần cân đối với lịch học các môn khác |

> Đây là ước lượng để 2 bạn tự đối chiếu với thời gian thực tế có thể dành cho đồ án mỗi tuần — nếu thấy không khả thi, nên trao đổi sớm với GVHD để điều chỉnh phạm vi (mục 3.2 trong Đề cương) thay vì cố gắng quá sức ở các tuần cuối.

---

## 7. XỬ LÝ KHI MẤT CÂN BẰNG CÔNG VIỆC

| Tình huống | Cách xử lý |
|---|---|
| Một track xong sớm hơn track kia | Người xong sớm hỗ trợ track chậm hơn ở phần không đòi hỏi chuyên môn sâu (viết test, chuẩn bị dữ liệu demo, viết tài liệu) |
| Một người không thể tham gia 1 tuần (ốm/bận việc khác) | Nhờ cả 2 đã cùng nắm phần lõi (Sprint 3) và code review chéo thường xuyên, người còn lại vẫn có thể duy trì tiến độ cơ bản; dồn việc bù ở tuần buffer (không có sprint nào 100% kín lịch, nên chừa dư ra ít nhất 1-2 ngày/sprint) |
| 2 người bất đồng về cách triển khai kỹ thuật | Đưa ra GVHD làm người quyết định cuối (đúng vai trò A trong hạng mục "Quyết định ngưỡng/tiêu chí" ở mục 3), tránh để tranh luận kéo dài làm chậm tiến độ |

---

*Bảng này nên được xem lại và cập nhật vào cuối mỗi Sprint Retrospective (theo Tài liệu Kiến trúc, mục 3.6) — phân công là kế hoạch ban đầu, có thể điều chỉnh khi thực tế phát sinh khác dự kiến.*
