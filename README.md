# DAU Second Brain

**Hệ thống tóm tắt & tra cứu văn bản tiếng Việt có trích dẫn — chống bịa đặt thông tin — dành cho Trường Đại học Kiến trúc Đà Nẵng.**

Đồ án môn Trí tuệ Nhân tạo | Nhóm 2 sinh viên | 12 tuần

---

## Giới thiệu

DAU Second Brain là hệ thống hỗ trợ Phòng Đào tạo và giảng viên xử lý khối lượng lớn thông tư, quyết định, công văn của Bộ GD&ĐT cùng tài liệu giảng dạy nội bộ. Điểm khác biệt cốt lõi: **mọi nội dung do AI sinh ra đều được kiểm tra độ trung thực và gắn trích dẫn kiểm chứng được về nguồn gốc** — không có ngoại lệ.

## Vấn đề giải quyết

- Cán bộ/giảng viên tốn nhiều thời gian đọc và tra cứu thủ công văn bản pháp quy.
- Các công cụ tóm tắt AI phổ biến có nguy cơ "bịa" thông tin (hallucination) — không thể chấp nhận với văn bản hành chính.
- Chưa có công cụ tóm tắt tiếng Việt nào tối ưu riêng cho domain văn bản giáo dục, có cơ chế trích dẫn kiểm chứng.

*(Chi tiết đầy đủ tại [Đề cương chi tiết đồ án](docs/DAU_Second_Brain_De_Cuong_Chi_Tiet.md))*

## Tính năng chính

| Tính năng | Mô tả |
|---|---|
| 📄 Tóm tắt có trích dẫn | Mỗi câu tóm tắt gắn ID đoạn nguồn, đã qua kiểm tra NLI **3 nhãn** (entailment/contradiction/neutral) trước khi hiển thị |
| ✅ Rà soát & Duyệt (Review Service) | Câu bị NLI gắn cờ `contradiction` chặn toàn bộ văn bản — cán bộ rà soát, sửa, duyệt; có audit trail đầy đủ (Publish Gate) |
| 🔍 Tra cứu & Chatbot (RAG) | Hỏi-đáp tự nhiên trên kho văn bản đã `published`, luôn kèm trích dẫn, từ chối trả lời nếu không đủ căn cứ |
| 📝 Gợi ý khung báo cáo | Tự động chọn **template riêng** từ Thư viện Template phù hợp từng loại văn bản — không tự sinh số liệu/nội dung thực tế |
| 🌳 Cây văn bản | Hiển thị văn bản liên quan (quan hệ tường minh + ngữ nghĩa) và mức độ áp dụng đối với trường — tái sử dụng hạ tầng embedding RAG |
| 🗂️ Dashboard theo chủ đề | Cán bộ duyệt văn bản theo nhóm chủ đề (Đào tạo, Tuyển sinh, Tài chính...) thay vì danh sách hàng đợi phẳng |
| 🔎 Đối chiếu trích dẫn | Xem từng câu tóm tắt/trả lời được lấy từ đoạn nào, kèm điểm độ tin cậy và nhãn NLI |

## Kiến trúc tổng quan

```
Văn bản (PDF/scan, từ chinhphu.vn + tài liệu trường)
      → Ingestion → Extraction (OCR, NER, phân loại loại + chủ đề)
      → Summarization (tóm tắt + NLI 3 nhãn + trích dẫn)
      → Review Service (Publish Gate — human-in-the-loop, audit trail)
      → Report Suggestion (theo Thư viện Template)  /  Retrieval-QA (RAG)
      → Cây văn bản (tái sử dụng embedding)  /  Dashboard theo chủ đề
```

Chi tiết đầy đủ (sơ đồ phân lớp, luồng dữ liệu, danh mục dịch vụ) tại [Tài liệu Đặc tả Nghiệp vụ & Kiến trúc](docs/DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md).

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend / API | Python, FastAPI |
| Mô hình tóm tắt | BARTpho / ViT5 (fine-tuned) |
| Trích xuất thông tin | PhoBERT-CRF (NER), TextRank (baseline) |
| Kiểm tra độ trung thực | Mô hình NLI (fine-tune PhoBERT/XLM-R) |
| Tra cứu ngữ nghĩa | Embedding tiếng Việt + FAISS / Chroma |
| OCR | PaddleOCR / Tesseract |
| Cơ sở dữ liệu | PostgreSQL / SQLite (demo) |
| Giao diện | Streamlit (demo) hoặc React/Next.js |
| Đóng gói & triển khai | Docker, docker-compose |
| CI/CD | GitHub Actions |

## Cấu trúc thư mục

```
dau-second-brain/
├── docs/                        # Toàn bộ tài liệu đồ án (xem bên dưới)
├── data/
│   ├── raw/                     # Văn bản gốc thu thập được
│   └── processed/                # Văn bản đã chia đoạn, làm sạch
├── services/
│   ├── ingestion/                # SVC-01
│   ├── extraction/                # SVC-02 — OCR, NER, phân loại loại + chủ đề
│   ├── summarization/            # SVC-03 — tóm tắt + NLI 3 nhãn (lõi)
│   ├── review_service/           # SVC-07 — Publish Gate, audit trail
│   ├── report_suggestion/        # SVC-04 — Thư viện Template
│   ├── retrieval_qa/             # SVC-05 — embedding + RAG
│   └── related_docs/             # SVC-06 — Cây văn bản (tái sử dụng embedding)
├── dashboard/                    # Giao diện web (kể cả Dashboard theo chủ đề)
├── evaluation/                   # Script đánh giá ROUGE/BERTScore/Faithfulness
├── docker-compose.yml
├── .env.example
└── README.md
```

## Bắt đầu nhanh

**Yêu cầu:** Docker, Docker Compose, Python 3.10+

```bash
# 1. Clone repository
git clone <repository-url>
cd dau-second-brain

# 2. Cấu hình biến môi trường
cp .env.example .env

# 3. Khởi động toàn bộ hệ thống
docker-compose up --build

# 4. Mở dashboard
# http://localhost:8501 (hoặc cổng đã cấu hình trong .env)
```

## Tài liệu dự án

| # | Tài liệu | Nội dung |
|---|---|---|
| 1 | [Đề cương chi tiết đồ án](docs/DAU_Second_Brain_De_Cuong_Chi_Tiet.md) | Đặt vấn đề, mục tiêu, phạm vi, kế hoạch tổng quát |
| 2 | [Đặc tả Nghiệp vụ & Kiến trúc](docs/DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md) | Kiến trúc hệ thống, quy trình nghiệp vụ, Scrum, DevOps, rủi ro |
| 3 | [Đặc tả Yêu cầu Chức năng (SRS)](docs/DAU_Second_Brain_Dac_Ta_Yeu_Cau_Chuc_Nang.md) | Use case chi tiết, yêu cầu chức năng/phi chức năng |
| 4 | [Thiết kế Giao diện (UI/UX Spec)](docs/DAU_Second_Brain_UIUX_Spec.md) | Đặc tả màn hình chính, luồng điều hướng, design system |
| 5 | [Kế hoạch Thu thập & Xử lý Dữ liệu](docs/DAU_Second_Brain_Ke_Hoach_Du_Lieu.md) | Nguồn dữ liệu (chinhphu.vn + tài liệu trường), quy trình gán nhãn |
| 6 | [Kế hoạch Đánh giá & Tiêu chí Nghiệm thu](docs/DAU_Second_Brain_Ke_Hoach_Danh_Gia.md) | Metric đánh giá, ngưỡng đạt, quy trình đánh giá con người |
| 7 | [Bảng Phân công Công việc (RACI)](docs/DAU_Second_Brain_Phan_Cong_RACI.md) | Phân công theo sprint, ma trận trách nhiệm |
| 8 | [Các Thuật toán Sử dụng](docs/CÁC%20THUẬT%20TOÁN%20SỬ%20DỤNG.md) | Mô tả kỹ thuật và hình dung thực tế của từng thuật toán |

> Đặt cả 8 file trên vào thư mục `docs/` của repo để các liên kết trong README hoạt động đúng.

## Kế hoạch triển khai (12 tuần)

| Sprint | Tuần | Trọng tâm |
|---|---|---|
| Sprint 0 | 1–2 | Thu thập dữ liệu (**chinhphu.vn + tài liệu trường**), thiết kế kiến trúc & data model |
| Sprint 1–2 | 3–6 | Ingestion, Extraction/phân loại **loại + chủ đề**/NER, chuẩn bị checkpoint BARTpho/ViT5 |
| Sprint 3 | 7–8 | **NLI 3 nhãn + Review Service (Publish Gate, audit trail)** — trọng tâm kỹ thuật; cả 2 cùng làm |
| Sprint 4 | 9–10 | Thư viện Template + Report Suggestion; Embedding + RAG Chatbot; **Cây văn bản** |
| Sprint 5 | 11 | Ghép nối end-to-end, hoàn thiện Dashboard (**kể cả Dashboard theo chủ đề + Cây văn bản**) |
| Sprint 6 | 12 | Đánh giá, viết báo cáo, chuẩn bị demo |

## Nhóm thực hiện

| Vai trò | Phụ trách |
|---|---|
| Thành viên 1 | Track A — Data & Pipeline (Ingestion, Extraction/phân loại chủ đề, Thư viện Template/Report Suggestion, Dashboard theo chủ đề, DevOps) |
| Thành viên 2 | Track B — AI Core (BARTpho/ViT5, NLI 3 nhãn, Review Service, Embedding + RAG, Cây văn bản) |
| GVHD | Định hướng, duyệt tiêu chí nghiệm thu |

## Phạm vi

**Trong phạm vi:** tóm tắt có trích dẫn (NLI 3 nhãn), Review Service (Publish Gate + audit trail), gợi ý khung báo cáo (Thư viện Template), tra cứu/hỏi-đáp RAG, Cây văn bản, Dashboard theo chủ đề.

**Định hướng phát triển tương lai:** quản lý vòng đời văn bản đầy đủ (cảnh báo tự động hết hiệu lực), speech-to-text, ứng dụng di động, tích hợp LMS/SIS.

## Quy ước đóng góp

- Nhánh: `main` (ổn định) ← `dev` (tích hợp) ← `feature/<ten-tinh-nang>`
- Commit theo chuẩn Conventional Commits: `feat: ...`, `fix: ...`, `docs: ...`
- Mọi merge vào `develop`/`main` cần người còn lại trong nhóm review

## Giấy phép

Đồ án học thuật — thực hiện cho mục đích giáo dục tại Trường Đại học Kiến trúc.

