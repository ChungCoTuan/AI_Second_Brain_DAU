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
3. Chiến lược mô hình hóa khi không có dữ liệu huấn luyện quy mô lớn
4. Quy trình thu thập
5. Quy trình tiền xử lý
6. Quy trình gán nhãn (Annotation)
7. Phân chia tập dữ liệu
8. Kiểm soát chất lượng dữ liệu
9. Vấn đề pháp lý & đạo đức dữ liệu
10. Timeline thu thập dữ liệu

---

## 1. MỤC TIÊU & NGUYÊN TẮC

**Mục tiêu:** Có đủ dữ liệu để (a) đánh giá khả năng tóm tắt của mô hình trên đúng domain mục tiêu, và (b) xây được tập kiểm thử (test set) chất lượng để đo ROUGE, BERTScore, và đặc biệt là **Faithfulness** — chỉ số quan trọng nhất của đồ án.

**Nguyên tắc thực tế cho nhóm 2 người/12 tuần:**
- **Không tự gán nhãn tóm tắt chuẩn (gold summary) cho hàng trăm văn bản** — quá tốn thời gian, không khả thi.
- **Theo yêu cầu GVHD: toàn bộ dữ liệu chỉ cào từ chinhphu.vn và tài liệu liên quan tới trường** — không dùng dataset công khai ngoài ngành (VietNews/VNDS) như bản kế hoạch trước.
- **Vì không còn dữ liệu quy mô lớn để fine-tune, đổi chiến lược mô hình:** dùng thẳng checkpoint BARTpho/ViT5 đã pretrained sẵn cho tóm tắt tiếng Việt (không tự huấn luyện lại từ đầu) — xem chi tiết ở mục 3.
- **Tận dụng cấu trúc có sẵn của văn bản hành chính** (trích yếu, mục lục điều khoản) thay vì phải gán nhãn từ đầu.

---

## 2. NGUỒN DỮ LIỆU

### 2.1 Nguồn dữ liệu chính

> **Theo yêu cầu GVHD:** nguồn chính là **Cổng Thông tin điện tử Chính phủ (chinhphu.vn)** và **tài liệu văn bản liên quan trực tiếp tới trường** — không dùng thêm dataset công khai ngoài ngành (đã loại bỏ VietNews/VNDS khỏi kế hoạch).

| Nguồn | Nội dung | Cách lấy |
|---|---|---|
| **Cổng Thông tin điện tử Chính phủ** (chinhphu.vn) | Văn bản quy phạm pháp luật đầy đủ: luật, nghị định, thông tư, quyết định, công văn — phạm vi rộng hơn moet.gov.vn, là nguồn chính thức cao nhất | Tải trực tiếp bản PDF/HTML công khai; lọc theo lĩnh vực "Giáo dục - Đào tạo" |
| **Tài liệu văn bản liên quan tới trường** (quy chế nội bộ, quyết định riêng của Trường Đại học Kiến trúc, thông báo của Phòng Đào tạo) | Văn bản áp dụng trực tiếp cho trường — nguồn quan trọng nhất để hệ thống thực sự hữu ích cho đúng đơn vị sử dụng | Xin cung cấp trực tiếp từ GVHD/Phòng Đào tạo — **cần xác nhận bằng văn bản/email phạm vi được phép sử dụng trước khi đưa vào hệ thống** (xem mục 9) |
| **Cổng thông tin điện tử Bộ GD&ĐT** (moet.gov.vn) | Thông tư, quyết định, công văn chuyên ngành giáo dục | Giữ làm nguồn bổ sung — một số văn bản chuyên ngành có thể đăng trên moet.gov.vn sớm hơn hoặc đầy đủ hơn chinhphu.vn |
| **Cơ sở dữ liệu quốc gia về văn bản pháp luật** (vbpl.vn) | Đối chiếu, kiểm tra hiệu lực, tra cứu văn bản liên quan (căn cứ/dẫn chiếu) | Tra cứu bổ sung để xác nhận trạng thái hiệu lực và phục vụ tính năng "Cây văn bản" (mục 6.4) |

> **Vì sao chọn chinhphu.vn làm nguồn chính (thay vì chỉ moet.gov.vn):** chinhphu.vn là cổng thông tin chính thức cấp cao nhất, có đầy đủ văn bản liên ngành (không chỉ riêng Bộ GD&ĐT) — phù hợp hơn với tính năng "Cây văn bản" (yêu cầu #3), vì nhiều thông tư giáo dục có căn cứ dẫn chiếu tới luật/nghị định của các bộ ngành khác chỉ có đầy đủ trên chinhphu.vn.

### 2.2 Đối tượng người dùng thử nghiệm (cho việc đánh giá chatbot)
Nếu có thể, xin 3-5 câu hỏi thực tế từ cán bộ Phòng Đào tạo/giảng viên để xây tập câu hỏi test cho UC-06 (tra cứu/hỏi đáp), thay vì nhóm tự nghĩ ra câu hỏi — giúp tập test sát với nhu cầu thật hơn.

---

## 3. CHIẾN LƯỢC MÔ HÌNH HÓA KHI KHÔNG CÓ DỮ LIỆU HUẤN LUYỆN QUY MÔ LỚN

**Hệ quả kỹ thuật của việc bỏ VietNews/VNDS:** 20-30 văn bản cào từ chinhphu.vn + trường là **quá ít để fine-tune một mô hình sinh văn bản (BARTpho/ViT5) từ đầu** — fine-tune với vài chục cặp dữ liệu có nguy cơ cao bị overfitting (mô hình học thuộc lòng thay vì học tóm tắt), thậm chí làm mô hình *tệ hơn* so với dùng nguyên bản pretrained.

**Chiến lược điều chỉnh — không fine-tune từ đầu, dùng checkpoint pretrained + đánh giá nghiêm túc:**

```
BƯỚC 1 — Dùng thẳng mô hình đã pretrained sẵn cho tóm tắt tiếng Việt
   Mô hình: BARTpho/ViT5 — checkpoint đã được cộng đồng/VinAI huấn luyện
            sẵn cho tác vụ tóm tắt (không tự huấn luyện lại từ đầu)
   Lý do: mô hình đã học được cách tóm tắt tiếng Việt tự nhiên từ trước,
          không cần dữ liệu lớn để đạt được năng lực nền tảng này
                          │
                          ▼
BƯỚC 2 — Toàn bộ dữ liệu cào được (chinhphu.vn + trường) dồn hết cho ĐÁNH GIÁ
   Không chia train/test — vì không huấn luyện, không có rủi ro "học thuộc"
   tập test, nên có thể dùng 100% dữ liệu thu thập được để đánh giá
                          │
                          ▼
BƯỚC 3 (tùy chọn, nếu Sprint 2-3 vẫn dư thời gian) — Thích nghi nhẹ (LoRA/PEFT)
   Chỉ thực hiện nếu kết quả Bước 2 cho thấy mô hình pretrained hoạt động
   kém trên domain văn bản pháp quy. Dùng kỹ thuật LoRA (ít tham số, ít
   dữ liệu) trên một phần nhỏ tách ra, KHÔNG dùng để tự tin báo cáo số
   liệu đẹp mà chỉ để thử nghiệm — vẫn ưu tiên đánh giá trên phần dữ
   liệu chưa từng dùng để thích nghi.
```

**Đây là điểm cần trình bày rõ với GVHD:** khi không còn VietNews/VNDS, đóng góp chính của đồ án chuyển từ "huấn luyện mô hình tóm tắt" sang **"đánh giá và kiểm soát độ tin cậy của mô hình pretrained khi áp dụng vào domain văn bản pháp quy giáo dục tiếng Việt"** — trọng tâm vẫn là cơ chế Faithfulness (NLI 3 nhãn, human-in-the-loop), không đổi, chỉ đổi cách có được mô hình tóm tắt ban đầu. Đây vẫn là hướng đóng góp hợp lệ và thực tế hơn cho quy mô 12 tuần/2 người.

> **Khuyến nghị:** nếu muốn tăng độ tin cậy của kết quả đánh giá, nên cân nhắc thu thập nhiều hơn mức tối thiểu 20-25 văn bản (ví dụ 30-40 nếu thời gian cho phép) — vì giờ đây đây là **nguồn dữ liệu duy nhất** phục vụ toàn bộ việc đánh giá, không còn phần nào "dự phòng" từ dữ liệu công khai.

---

## 4. QUY TRÌNH THU THẬP

| Bước | Nội dung | Công cụ |
|---|---|---|
| 1 | Thu thập 20-30 (khuyến nghị 30-40 nếu có thời gian) văn bản GD&ĐT + tài liệu liên quan trường | Tải thủ công hoặc script đơn giản từ **chinhphu.vn** (lọc lĩnh vực Giáo dục - Đào tạo), bổ sung từ moet.gov.vn; xin trực tiếp tài liệu nội bộ trường từ GVHD/Phòng Đào tạo (chỉ crawl trang công khai, không yêu cầu đăng nhập) |
| 2 | Phân loại sơ bộ khi thu thập | Gắn nhãn thô: loại văn bản, năm ban hành, lĩnh vực (đào tạo/tài chính/nhân sự...) để đảm bảo tập dữ liệu đa dạng, không dồn vào 1 chủ đề |
| 3 | Lưu trữ có tổ chức | Thư mục theo cấu trúc `data/raw/<loai_van_ban>/<so_hieu>.pdf` kèm file `metadata.csv` ghi nguồn gốc |

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
Phần lớn thông tư/quyết định của Bộ GD&ĐT có sẵn mục **"Trích yếu"** hoặc phần mở đầu tóm lược nội dung — đây có thể dùng làm gold summary ban đầu, **giảm đáng kể khối lượng viết tay**. Với văn bản không có trích yếu rõ ràng, 2 thành viên tự viết tóm tắt tay cho một tập nhỏ (khuyến nghị bằng đúng số văn bản đã thu thập ở mục 2.1 — toàn bộ tập này giờ đóng vai trò tập đánh giá duy nhất, xem mục 3 và 7).

### 6.2 Gán nhãn NER — bán tự động
Số hiệu văn bản, ngày ban hành, cơ quan ban hành đều có **format khá cố định** trong văn bản hành chính Việt Nam (ví dụ: "Số: 08/2024/TT-BGDĐT", "Hà Nội, ngày ... tháng ... năm ..."). Đề xuất:
1. Viết rule/regex trích xuất tự động trước (độ chính xác kỳ vọng khá cao vì format chuẩn).
2. Người thu thập chỉ cần **kiểm tra và sửa lỗi** thay vì gán nhãn từ đầu — tiết kiệm thời gian đáng kể so với gán nhãn thủ công 100%.

### 6.3 Gán nhãn đánh giá Faithfulness
Với tập test (20-30 văn bản), sau khi mô hình sinh tóm tắt, 2 thành viên **cùng đọc và đánh giá thủ công** một mẫu ngẫu nhiên (ví dụ 10 văn bản) để đối chiếu với điểm mà mô hình NLI tự động đưa ra — nhằm kiểm tra mô hình NLI có đáng tin không, không chỉ tin tưởng hoàn toàn vào số liệu tự động.

### 6.4 Gán nhãn Chủ đề & Mức độ liên quan tới trường (mới — phục vụ "Cây văn bản" và Dashboard theo chủ đề)

**Gán nhãn Chủ đề/Lĩnh vực:** mỗi văn bản được gán 1 nhãn chủ đề trong danh sách cố định (ví dụ: Đào tạo, Tài chính - Ngân sách, Nhân sự, Tuyển sinh, Cơ sở vật chất, Khác). Quy trình bán tự động tương tự NER:
1. Rule/keyword-based gán nhãn sơ bộ (ví dụ văn bản chứa nhiều từ "tín chỉ", "học phần" → Đào tạo).
2. Cán bộ kiểm tra và sửa nhãn sai — không cần mô hình học máy riêng cho bước này trong 12 tuần, vì số lượng chủ đề cố định và từ khóa khá rõ ràng với văn bản hành chính.

**Gán nhãn Mức độ liên quan tới trường:** mỗi văn bản được gán 1 trong 3 mức: **Áp dụng trực tiếp** (văn bản riêng của trường), **Áp dụng chung** (văn bản của Bộ/Chính phủ, áp dụng cho mọi cơ sở giáo dục đại học), **Tham khảo** (liên quan gián tiếp, ví dụ văn bản chuyên ngành kiến trúc-xây dựng nhưng không bắt buộc áp dụng cho đào tạo). Nhãn này dùng làm dữ liệu huấn luyện/kiểm thử cho tính năng "Cây văn bản" (xem Tài liệu Kiến trúc, WF-06 cập nhật).

**Gán nhãn quan hệ "Căn cứ"** (phục vụ Cây văn bản): tận dụng phần mở đầu "Căn cứ ..." mà hầu hết văn bản hành chính đều có — đây liệt kê sẵn các văn bản làm cơ sở ban hành, gần như là "quan hệ liên kết có sẵn" không cần gán nhãn thủ công, chỉ cần trích xuất bằng rule/NER (xem Tài liệu Kiến trúc, mục Data Model — `DocumentRelation`).

---

## 7. PHÂN CHIA TẬP DỮ LIỆU

Vì không còn huấn luyện mô hình từ dữ liệu công khai (mục 3), cách phân chia dữ liệu đơn giản hơn bản trước — không cần tách Train/Validation:

| Tập | Nguồn | Quy mô | Mục đích |
|---|---|---|---|
| **Test/Đánh giá (toàn bộ)** | 20-30 (khuyến nghị 30-40) văn bản chinhphu.vn + trường tự thu thập | 100% dữ liệu đã thu thập | Đánh giá cuối: ROUGE, BERTScore, Faithfulness trên mô hình pretrained sẵn — **đây là kết quả chính báo cáo trong đồ án** |
| **Tập thích nghi (LoRA)** *(tùy chọn, chỉ dùng nếu Bước 3 ở mục 3 được kích hoạt)* | Trích một phần nhỏ (ví dụ 20-30%) từ chính tập trên | Tối đa ~30% tổng dữ liệu | Thích nghi nhẹ nếu mô hình pretrained hoạt động kém trên domain — phần còn lại (chưa dùng để thích nghi) vẫn phải giữ nguyên làm test để đánh giá không thiên lệch |

> **Lưu ý quan trọng:** nếu quyết định làm Bước 3 (LoRA), phần dữ liệu dùng để thích nghi **không được dùng lại để báo cáo kết quả đánh giá cuối** — nếu không, số liệu báo cáo sẽ bị lạc quan giả tạo (mô hình "học thuộc" đúng những gì nó vừa được thích nghi).

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
| Tuần 1 | Bắt đầu thu thập văn bản từ chinhphu.vn + tài liệu trường (Track A phụ trách); Track B khảo sát và chọn checkpoint BARTpho/ViT5 pretrained phù hợp nhất cho tóm tắt tiếng Việt |
| Tuần 2 | Hoàn tất thu thập 20-30 (hoặc 30-40) văn bản; xây xong pipeline tiền xử lý (chia đoạn, làm sạch); chạy thử nhanh mô hình pretrained trên vài văn bản đầu để có cảm nhận sớm về chất lượng (không chờ tới Sprint 2 mới biết) |
| Tuần 3-4 | Gán nhãn gold summary (tận dụng trích yếu + viết tay phần còn thiếu); kiểm tra NER bán tự động; **gán nhãn Chủ đề và Mức độ liên quan tới trường (mục 6.4), trích xuất quan hệ "Căn cứ" bằng rule** — làm song song vì đều dựa trên cùng tập văn bản đã thu thập |
| Tuần 7-8 (song song Sprint 3) | Đánh giá thủ công mẫu Faithfulness, đối chiếu với điểm NLI tự động |
| Tuần 9-10 (song song Sprint 4) | Đối chiếu thủ công một mẫu nhỏ kết quả gợi ý "văn bản liên quan" (quan hệ ngữ nghĩa) để đánh giá độ chính xác top-k, phục vụ Kế hoạch Đánh giá |

> Việc thu thập dữ liệu nằm trọn trong Sprint 0 (tuần 1-2) theo kế hoạch Scrum đã có trong Tài liệu Kiến trúc — không kéo dài sang các sprint sau để tránh ảnh hưởng tiến độ phát triển mô hình.

---

*Kế hoạch này ưu tiên tính khả thi trong 12 tuần hơn là quy mô dữ liệu lớn — chất lượng và tính đại diện của tập test 20-30 văn bản quan trọng hơn số lượng, vì đây là cơ sở duy nhất để chứng minh hệ thống hoạt động đúng như cam kết (không bịa đặt thông tin).*
