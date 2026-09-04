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
| Thành viên 1 (TV1) | *(điền tên)* | Track A — Data & Pipeline (Ingestion, Extraction/Classification/NER, **Thư viện Template & Report Suggestion, Dashboard theo chủ đề**, DevOps) |
| Thành viên 2 (TV2) | *(điền tên)* | Track B — AI Core (Đánh giá & lựa chọn mô hình tóm tắt pretrained — **không fine-tune, xem Kế hoạch Dữ liệu mục 3**, NLI 3 nhãn, **Review Service**, Embedding & RAG, **Cây văn bản**) |
| Giảng viên hướng dẫn (GVHD) | *(điền tên)* | Product Owner — định hướng, duyệt tiêu chí nghiệm thu, tham vấn kỹ thuật |

> Cách chia Track này giữ nguyên theo Tài liệu Kiến trúc (mục 3.1.1) — tài liệu này chỉ cụ thể hóa thêm mức độ trách nhiệm và lịch làm việc. Đã cập nhật theo 5 yêu cầu bổ sung của GVHD và Phương án A (dùng mô hình pretrained, không tự fine-tune — Kế hoạch Dữ liệu mục 3).

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
| EPIC-2: Extraction, Classification (loại + **chủ đề**), NER | R, A | C | I |
| EPIC-3: Đánh giá & lựa chọn mô hình tóm tắt pretrained *(không fine-tune)* | C | R, A | I |
| EPIC-3: NLI 3 nhãn + citation mapping (Sprint 3 — cả 2 cùng làm) | R, A | R, A | C |
| **EPIC-9: Review Service (Sprint 3 — cả 2 cùng làm)** | R, A | R, A | C |
| EPIC-4: Thư viện Template + Report Suggestion | R, A | C | I |
| EPIC-5: Embedding + RAG Chatbot | C | R, A | I |
| **EPIC-6: Cây văn bản** | C | R, A | I |
| **EPIC-10: Dashboard theo chủ đề** | R, A | C | I |
| EPIC-7: Tích hợp end-to-end | R, A | R | I |
| EPIC-8: Đánh giá định lượng | R | R, A | C |
| EPIC-8: Viết báo cáo đồ án | R, A | R, A | C |
| Quyết định ngưỡng Faithfulness/tiêu chí nghiệm thu | C | C | **R, A** |
| Chuẩn bị & trình bày demo/bảo vệ | R, A | R, A | C |

> **Lưu ý:** Với EPIC-3 phần NLI 3 nhãn và EPIC-9 (Review Service) — 2 mục quan trọng nhất của đồ án — cả 2 thành viên đều là R/A, nghĩa là **không ai được đứng ngoài phần này**, đúng theo nguyên tắc giảm rủi ro "chỉ 1 người hiểu phần lõi" đã nêu trong Risk Register của Tài liệu Kiến trúc.

---

## 4. PHÂN CÔNG CHI TIẾT THEO SPRINT

| Sprint | Tuần | TV1 — Track A | TV2 — Track B | Điểm đồng bộ (Sync point) |
|---|---|---|---|---|
| Sprint 0 | 1–2 | Thu thập văn bản từ **chinhphu.vn + tài liệu trường**, thiết kế schema `DocumentChunk` và các bảng mới (`ReviewItem`, `ReportTemplate`, `Topic`) | Khảo sát và chọn checkpoint BARTpho/ViT5 **pretrained** phù hợp nhất (không tự huấn luyện) | Thống nhất schema dữ liệu trung gian trước khi tách việc (bắt buộc — theo Risk Register) |
| Sprint 1 | 3–4 | Xây Ingestion Service, chia đoạn Điều/Khoản | Chạy baseline TextRank; chạy thử nhanh checkpoint pretrained trên vài văn bản đầu để có cảm nhận sớm | Kiểm tra output của TV1 (chunk có ID) tương thích với input mà TV2 cần |
| Sprint 2 | 5–6 | Classification (loại + **chủ đề**) + NER cơ bản | Đánh giá sơ bộ mô hình pretrained trên tập đã có; cân nhắc LoRA nhẹ nếu kết quả kém (Kế hoạch Dữ liệu, Bước 3 — tùy chọn) | Demo nội bộ giữa 2 người: dữ liệu đã trích xuất từ TV1 chạy thử qua model của TV2 |
| Sprint 3 | 7–8 | **Cùng làm:** NLI 3 nhãn (entailment/contradiction/neutral) + citation mapping + **Review Service** (hàng đợi ưu tiên, audit trail, cơ chế publish theo văn bản) | **Cùng làm:** (như cột bên trái — không tách việc) | Cả 2 cùng ngồi code chung phần này — đây là sprint nặng nhất, không tách việc |
| Sprint 4 | 9–10 | **Thư viện Template** + Report Suggestion theo từng loại; bắt đầu UI **Dashboard theo chủ đề** | Embedding + RAG chatbot (chỉ trên văn bản `published`); **Cây văn bản** (tái sử dụng Vector DB của RAG, không xây thêm mô hình) | Chạy thử độc lập 2 module, chuẩn bị ghép ở Sprint 5 |
| Sprint 5 | 11 | Hoàn thiện Dashboard theo chủ đề, ghép nối toàn bộ pipeline | Hỗ trợ ghép nối phần AI vào Dashboard + hiển thị Cây văn bản, kiểm thử end-to-end | Test toàn bộ luồng cùng nhau, danh sách lỗi cần sửa gấp |
| Sprint 6 | 12 | Chạy đánh giá phần dữ liệu/NER/chủ đề, viết phần kiến trúc-triển khai trong báo cáo | Chạy đánh giá ROUGE/BERTScore/phân phối 3 nhãn NLI/Cây văn bản, viết phần mô hình-kết quả trong báo cáo | Ghép báo cáo hoàn chỉnh, tổng duyệt trước khi nộp/demo |

> **Thay đổi so với bản trước:** Sprint 3 giờ gánh thêm Review Service (trước đây tách biệt), Sprint 4 gánh thêm Cây văn bản và Dashboard theo chủ đề — đây là 2 sprint có khối lượng tăng nhiều nhất sau khi GVHD bổ sung yêu cầu. Xem mục 6 để biết ước lượng giờ đã điều chỉnh tương ứng.

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
| Sprint 0 (thu thập, thiết kế) | ~15-20 giờ/người | Bao gồm thời gian đọc tài liệu, thử nghiệm công cụ; schema đã mở rộng thêm 3 bảng mới nên thiết kế mất thêm thời gian so với bản trước |
| Sprint 1-2 (xây nền tảng) | ~20-25 giờ/người/sprint | Phần code nhiều nhất; Sprint 2 của TV1 nặng hơn trước vì thêm phân loại chủ đề |
| **Sprint 3 (NLI 3 nhãn + Review Service — cả 2 cùng làm)** | **~30-35 giờ/người** *(tăng so với bản trước ~25-30 giờ)* | Sprint nặng nhất — gánh cả cơ chế 3 nhãn lẫn Review Service mới; nếu quá tải, xem thứ tự cắt giảm ở Tài liệu Kiến trúc mục 3.3 |
| **Sprint 4 (mở rộng — Template/Chủ đề/Cây văn bản)** | **~25-30 giờ/người** *(tăng so với bản trước ~20-25 giờ)* | Gánh thêm Cây văn bản và Dashboard theo chủ đề so với kế hoạch gốc |
| Sprint 5 (ghép nối) | ~20-25 giờ/người | Nhiều module hơn cần ghép nối so với bản trước |
| Sprint 6 (đánh giá, báo cáo) | ~15-20 giờ/người | Bao gồm thời gian viết báo cáo; nhiều chỉ số đánh giá hơn (3 nhãn NLI, chủ đề, Cây văn bản) |
| **Tổng ước tính** | **~155-190 giờ/người trong 12 tuần** *(tăng so với bản trước 130-165 giờ)* | Tương đương ~13-16 giờ/tuần/người — **cao hơn đáng kể so với ước lượng ban đầu**, cần cân đối kỹ với lịch học các môn khác |

> **Cảnh báo:** khối lượng công việc đã tăng ~20% sau khi bổ sung 5 yêu cầu của GVHD. Nếu 13-16 giờ/tuần/người không khả thi với lịch học thực tế, nên chủ động trao đổi với GVHD **ngay từ Sprint 0-1** về việc cắt giảm phạm vi (theo thứ tự ưu tiên đã nêu ở Tài liệu Kiến trúc mục 3.3), thay vì cố gắng quá sức ở các tuần cuối rồi mới báo trễ hạn.

---

## 7. XỬ LÝ KHI MẤT CÂN BẰNG CÔNG VIỆC

| Tình huống | Cách xử lý |
|---|---|
| Một track xong sớm hơn track kia | Người xong sớm hỗ trợ track chậm hơn ở phần không đòi hỏi chuyên môn sâu (viết test, chuẩn bị dữ liệu demo, viết tài liệu) |
| Một người không thể tham gia 1 tuần (ốm/bận việc khác) | Nhờ cả 2 đã cùng nắm phần lõi (Sprint 3) và code review chéo thường xuyên, người còn lại vẫn có thể duy trì tiến độ cơ bản; dồn việc bù ở tuần buffer (không có sprint nào 100% kín lịch, nên chừa dư ra ít nhất 1-2 ngày/sprint) |
| 2 người bất đồng về cách triển khai kỹ thuật | Đưa ra GVHD làm người quyết định cuối (đúng vai trò A trong hạng mục "Quyết định ngưỡng/tiêu chí" ở mục 3), tránh để tranh luận kéo dài làm chậm tiến độ |

---

*Bảng này nên được xem lại và cập nhật vào cuối mỗi Sprint Retrospective (theo Tài liệu Kiến trúc, mục 3.6) — phân công là kế hoạch ban đầu, có thể điều chỉnh khi thực tế phát sinh khác dự kiến.*
