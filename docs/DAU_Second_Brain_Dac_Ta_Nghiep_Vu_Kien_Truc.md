# TÀI LIỆU ĐẶC TẢ NGHIỆP VỤ & KIẾN TRÚC
## Hệ Sinh Thái "DAU Second Brain"

| | |
|---|---|
| **Phiên bản** | 1.0 |
| **Ngày ban hành** | 19/08/2026 |
| **Loại tài liệu** | Business Requirements & Architecture Specification |
| **Đối tượng sử dụng** | Nhóm phát triển đồ án, GVHD, Phòng Đào tạo |
| **Trạng thái** | Draft — dùng làm cơ sở triển khai đồ án |
| **Quy mô nhóm** | 2 sinh viên |
| **Thời hạn** | 12 tuần |

---

## MỤC LỤC

0. Giới thiệu chung
1. Tổng quan Kiến trúc Hệ thống (Enterprise Architecture)
2. Các Quy trình Nghiệp vụ Cốt lõi (Core Business Workflows)
3. Quản lý Dự án & Phân rã Công việc (Agile/Scrum Framework)
4. Tiêu chuẩn Vận hành & CI/CD (DevOps Standards)
5. Mô hình Dữ liệu (Data Model)
6. Yêu cầu Phi chức năng & Bảo mật
7. Quản lý Rủi ro (Risk Register)
8. Tiêu chí Nghiệm thu (Acceptance Criteria)
9. Phụ lục: Thuật ngữ

> **Ghi chú:** Mục 5–9 được bổ sung ngoài 4 mục ban đầu vì một tài liệu đặc tả kiến trúc đầy đủ cần có mô hình dữ liệu, yêu cầu phi chức năng, quản lý rủi ro và tiêu chí nghiệm thu để hội đồng đánh giá được tính khả thi và mức độ hoàn chỉnh của đồ án.

---

## 0. GIỚI THIỆU CHUNG

### 0.1 Mục đích tài liệu
Tài liệu này đặc tả kiến trúc hệ thống, quy trình nghiệp vụ, kế hoạch triển khai và tiêu chuẩn vận hành cho **DAU Second Brain** — hệ sinh thái quản lý tri thức tự động cho Trường Đại học Kiến trúc, tập trung vào việc số hóa, tóm tắt có trích dẫn (chống bịa đặt thông tin), và hỗ trợ gợi ý báo cáo từ các thông tư/quyết định/công văn của Bộ GD&ĐT cùng tài liệu giảng dạy nội bộ.

### 0.2 Phạm vi hệ thống

**Trong phạm vi (In scope):**
- Thu thập, số hóa văn bản pháp quy từ **chinhphu.vn** và **tài liệu liên quan trực tiếp tới trường**, cùng tài liệu giảng dạy (giáo trình, slide, đề cương).
- Tóm tắt tự động có trích dẫn nguồn theo điều/khoản, đảm bảo tính trung thực (faithfulness) — **văn bản có câu bị NLI chấm "contradiction" không được tự động xuất bản, phải qua rà soát con người (human-in-the-loop) trước khi phục vụ tra cứu.**
- Trích xuất thông tin có cấu trúc: số hiệu, ngày ban hành, cơ quan ban hành, yêu cầu báo cáo, hạn nộp, **chủ đề/lĩnh vực, mức độ liên quan tới trường.**
- Gợi ý dàn ý/khung báo cáo cho giảng viên dựa trên yêu cầu trong văn bản — **mỗi loại báo cáo có template riêng phù hợp, không dùng chung 1 khuôn cho mọi văn bản.**
- Tra cứu ngữ nghĩa (semantic search) và hỏi-đáp (chatbot RAG) có trích dẫn, **chỉ trên các văn bản đã hoàn tất rà soát.**
- **Hiển thị "Cây văn bản" — văn bản liên quan (quan hệ căn cứ/dẫn chiếu, cùng chủ đề) và mức độ áp dụng đối với trường**, ở phạm vi rút gọn (xem ghi chú bên dưới).
- **Dashboard duyệt văn bản theo chủ đề** cho Cán bộ Phòng Đào tạo, thay cho màn hình quản trị thuần túy dạng hàng đợi.

**Ngoài phạm vi (Out of scope, giai đoạn 1):**
- Tự động ký số / phát hành văn bản chính thức.
- Speech-to-text cho bài giảng ghi âm (đưa vào roadmap giai đoạn 2).
- Ứng dụng di động (chỉ làm web trước).
- Tích hợp trực tiếp với hệ thống quản lý đào tạo (LMS/SIS) hiện có của trường.
- **Theo dõi đầy đủ vòng đời văn bản** (cảnh báo tự động khi văn bản hết hiệu lực, quy trình xác nhận thay thế có kiểm duyệt) — đây là phần **nặng hơn** "Cây văn bản" (chỉ hiển thị quan hệ, không tự động quản lý trạng thái hiệu lực); do khối lượng công việc đã tăng đáng kể sau các yêu cầu bổ sung, phần quản lý vòng đời đầy đủ vẫn giữ ở roadmap tương lai.

> **Lưu ý về áp lực phạm vi:** so với bản trước, 12 tuần/2 người giờ phải gánh thêm: cổng rà soát contradiction (đáng kể), Cây văn bản (đáng kể), Dashboard theo chủ đề (vừa phải), đa dạng hóa template báo cáo (vừa phải). Đây là khối lượng không nhỏ — xem Risk Register (mục 7) đã cập nhật rủi ro tương ứng. Đề xuất: nếu tiến độ Sprint 3-4 chậm, ưu tiên cắt giảm trước ở "Cây văn bản" (làm ở mức tối thiểu — chỉ quan hệ "Căn cứ" trích xuất tự động, bỏ qua phần tính điểm liên quan bằng embedding) thay vì cắt giảm cơ chế rà soát contradiction, vì đây là yêu cầu an toàn cốt lõi không thể bỏ.

### 0.3 Đối tượng người dùng (Personas)

| Persona | Vai trò | Nhu cầu chính |
|---|---|---|
| Cán bộ Phòng Đào tạo | Người quản trị nội dung | Tra cứu nhanh văn bản hiện hành, không bỏ sót công văn mới |
| Giảng viên | Người dùng cuối | Nhận gợi ý khung báo cáo đúng yêu cầu, tiết kiệm thời gian soạn thảo |
| Sinh viên (giai đoạn sau) | Người dùng tra cứu | Tìm nhanh quy định liên quan đến học tập |
| Quản trị viên hệ thống (nhóm đồ án) | Vận hành hệ thống | Nạp dữ liệu, giám sát chất lượng mô hình, cập nhật hệ thống |

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG (ENTERPRISE ARCHITECTURE)

### 1.1 Nguyên tắc thiết kế

1. **Traceability trước tiên (Citation-first):** mọi nội dung do AI sinh ra phải truy vết được về đoạn văn bản gốc — không có ngoại lệ.
2. **Modularity:** mỗi bước xử lý (OCR, tóm tắt, NER, RAG...) là một service độc lập, dễ thay thế/nâng cấp riêng lẻ.
3. **Human-in-the-loop:** hệ thống chỉ **gợi ý**, con người (giảng viên/cán bộ) luôn là người xác nhận cuối cùng — đặc biệt với phần gợi ý báo cáo.
4. **Fail-safe:** khi mô hình không chắc chắn (điểm faithfulness thấp), hệ thống phải từ chối trả lời hoặc cảnh báo, thay vì đưa ra thông tin sai.
5. **Khả năng mở rộng dần (Incremental scalability):** kiến trúc phải chạy tốt ở quy mô demo (vài chục văn bản) và có đường mở rộng rõ ràng lên quy mô toàn trường.

### 1.2 Kiến trúc phân lớp (Layered Architecture)

```
┌──────────────────────────────────────────────────────────────┐
│  LỚP GIAO DIỆN (Presentation Layer)                           │
│  Web Dashboard (tra cứu, quản trị)  |  Chatbot UI (hỏi-đáp)    │
└───────────────────────────────┬────────────────────────────────┘
                                 │ REST/GraphQL API
┌───────────────────────────────▼────────────────────────────────┐
│  LỚP ỨNG DỤNG (Application / Service Layer)                    │
│  API Gateway                                                   │
│  ├─ Ingestion Service      (nạp & tiền xử lý văn bản)           │
│  ├─ Extraction Service     (OCR, phân loại, NER)                │
│  ├─ Summarization Service  (tóm tắt có trích dẫn)               │
│  ├─ Report Suggestion Svc  (gợi ý khung báo cáo)                │
│  ├─ Retrieval/QA Service   (semantic search, RAG)               │
│  └─ Document Lifecycle Svc (theo dõi hiệu lực văn bản)          │
└───────────────────────────────┬────────────────────────────────┘
                                 │
┌───────────────────────────────▼────────────────────────────────┐
│  LỚP AI/ML (Model Layer)                                       │
│  TextRank | BARTpho/ViT5 (fine-tuned) | PhoBERT-CRF (NER)       │
│  Classification model | NLI (faithfulness check)                │
│  Embedding model (semantic search)                               │
└───────────────────────────────┬────────────────────────────────┘
                                 │
┌───────────────────────────────▼────────────────────────────────┐
│  LỚP DỮ LIỆU (Data Layer)                                       │
│  Relational DB (metadata, quan hệ văn bản)                      │
│  Vector DB — FAISS/Chroma (embedding phục vụ RAG)                │
│  Object Storage (file PDF gốc)                                  │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 Chi tiết từng lớp & công nghệ đề xuất

| Lớp | Thành phần | Công nghệ đề xuất | Ghi chú |
|---|---|---|---|
| Presentation | Dashboard | React/Next.js hoặc Streamlit (demo nhanh) | Streamlit phù hợp hơn cho quy mô đồ án |
| Presentation | Chatbot UI | Widget chat tích hợp trong dashboard | Hiển thị kèm link trích dẫn |
| Application | API Gateway | FastAPI | Định tuyến, xác thực, rate limit cơ bản |
| Application | Ingestion Service | Python + Celery/queue đơn giản | Xử lý bất đồng bộ khi nạp nhiều file |
| Application | Extraction Service | PaddleOCR/Tesseract, PhoBERT-CRF | OCR chỉ cần khi văn bản là ảnh scan |
| Application | Summarization Service | BARTpho/ViT5 (fine-tuned) + NLI check | Module lõi của đồ án |
| Application | Report Suggestion Service | Rule-based template + LLM điền trường | Ưu tiên an toàn, giảm hallucination |
| Application | Retrieval/QA Service | Embedding tiếng Việt + FAISS/Chroma | RAG có trích dẫn bắt buộc |
| Data | Relational DB | PostgreSQL/SQLite (demo) | Lưu metadata, quan hệ văn bản |
| Data | Vector DB | FAISS (nhẹ) hoặc Chroma | Phục vụ semantic search |
| Data | Object Storage | Thư mục local hoặc MinIO | Lưu file PDF gốc để đối chiếu |
| Hạ tầng | Container hóa | Docker, docker-compose | Đóng gói toàn bộ service cho demo |

### 1.4 Sơ đồ luồng dữ liệu tổng thể

```
Văn bản (PDF/scan, từ chinhphu.vn hoặc tài liệu của trường)
      │
      ▼
[Ingestion] ── lưu file gốc + metadata cơ bản
      │
      ▼
[Extraction] ── OCR (nếu cần) → chia đoạn theo Điều/Khoản (mỗi đoạn có ID + trang)
      │                        → NER: số hiệu, ngày, cơ quan, yêu cầu báo cáo
      │                        → Classification: loại văn bản, CHỦ ĐỀ/LĨNH VỰC
      │                        → trích xuất quan hệ "Căn cứ" (phục vụ Cây văn bản)
      ▼
[Summarization] ── tóm tắt từng phần, mỗi câu gắn ID đoạn nguồn
      │           → NLI phân loại từng câu: Entailment / Contradiction / Neutral
      ▼
   ┌──────────────────────────────────────────────────────┐
   │  Toàn bộ câu = Entailment?                              │
   └──────────────────────────────────────────────────────┘
      │ Có                                    │ Không (có câu Contradiction/Neutral)
      ▼                                        ▼
[Xuất bản tự động]                    [Review Service] ── trạng thái "Cần rà soát"
      │                                        │  (KHÔNG index, KHÔNG hiển thị tra cứu)
      │                                        ▼
      │                              Cán bộ sửa câu lỗi → NLI chạy lại (re-validate)
      │                                        │
      │                                        ▼ (đạt)
      │                              Cán bộ bấm "Duyệt" → văn bản chuyển "Đã hoàn thiện"
      │                                        │
      ▼                                        ▼
[Indexing] ── sinh embedding, lưu Vector DB, cập nhật Cây văn bản (DocumentRelation)
      │
      ├──► [Report Suggestion] ── chọn đúng template theo loại báo cáo → sinh khung báo cáo
      │
      ├──► [Retrieval/QA] ── phục vụ tra cứu & chatbot, chỉ trên văn bản "Đã hoàn thiện"
      │
      └──► [Related Documents] ── hiển thị Cây văn bản khi mở 1 văn bản
```

> **Thay đổi quan trọng so với bản trước:** Indexing (đưa vào Vector DB, cho phép tra cứu) giờ diễn ra **sau** bước rà soát, không còn diễn ra ngay sau Summarization. Văn bản có câu Contradiction bị chặn toàn bộ, không phải chỉ ẩn riêng câu lỗi — đúng theo ví dụ GVHD đưa ra (10 câu tóm tắt, 2 câu lỗi → cả văn bản chưa publish, không riêng 2 câu).

### 1.5 Danh mục dịch vụ (Service Catalog)

| Mã dịch vụ | Tên | Đầu vào | Đầu ra | Độ ưu tiên |
|---|---|---|---|---|
| SVC-01 | Ingestion Service | File PDF/ảnh | Văn bản đã lưu trữ + metadata | Bắt buộc |
| SVC-02 | Extraction Service | Văn bản thô | Đoạn có cấu trúc + trường trích xuất + chủ đề + quan hệ "Căn cứ" | Bắt buộc |
| SVC-03 | Summarization Service | Đoạn văn bản | Tóm tắt kèm citation + nhãn NLI (3 lớp) | Bắt buộc — lõi đồ án |
| SVC-04 | Report Suggestion Service | Yêu cầu trích xuất + loại báo cáo | Khung báo cáo đúng template tương ứng | Bắt buộc — theo yêu cầu GVHD |
| SVC-05 | Retrieval/QA Service | Câu hỏi người dùng | Câu trả lời + trích dẫn (chỉ trên văn bản đã duyệt) | Bắt buộc |
| SVC-06 | Related Documents Service ("Cây văn bản") | Quan hệ "Căn cứ" + độ tương đồng chủ đề | Danh sách văn bản liên quan + mức độ áp dụng cho trường | **Bắt buộc, phạm vi rút gọn** *(đưa lại vào scope theo yêu cầu GVHD — mục 3.2)* |
| SVC-07 | Review Service (mới) | Câu bị gắn cờ Contradiction/Neutral | Trạng thái duyệt, audit trail | Bắt buộc — cơ chế an toàn cốt lõi |

---

## 2. CÁC QUY TRÌNH NGHIỆP VỤ CỐT LÕI (CORE BUSINESS WORKFLOWS)

### WF-01 — Thu thập & Nhập liệu văn bản
- **Actor:** Quản trị viên hệ thống (nhóm đồ án đóng vai trò này trong giai đoạn demo)
- **Trigger:** Có văn bản mới từ Bộ GD&ĐT hoặc tài liệu giảng dạy cần nạp vào hệ thống
- **Input:** File PDF/ảnh scan
- **Các bước:**
  1. Upload file qua dashboard hoặc thư mục theo dõi tự động (watch folder).
  2. Hệ thống kiểm tra định dạng, gán mã văn bản tạm thời.
  3. Lưu file gốc vào Object Storage, tạo bản ghi metadata (nguồn, ngày nạp).
  4. Đẩy vào hàng đợi xử lý cho WF-02.
- **Output:** Văn bản đã được lưu trữ, sẵn sàng xử lý
- **Ngoại lệ:** File lỗi định dạng/không đọc được → gắn cờ "cần xử lý thủ công"

### WF-02 — Trích xuất & Phân loại
- **Actor:** Hệ thống (tự động)
- **Trigger:** Văn bản mới hoàn tất WF-01
- **Input:** Văn bản thô
- **Các bước:**
  1. OCR nếu là ảnh scan (PaddleOCR/Tesseract).
  2. Chia văn bản thành các đoạn theo cấu trúc Điều/Khoản/Mục, mỗi đoạn có ID + số trang.
  3. Chạy Classification model để xác định **loại văn bản** (thông tư/quyết định/công văn/giáo trình...) **và chủ đề/lĩnh vực** (Đào tạo, Tuyển sinh, Tài chính — Học phí, Nhân sự, Cơ sở vật chất, Khác — theo danh mục chủ đề cố định đã định nghĩa trước, xem mục 5) — phục vụ Dashboard theo chủ đề (WF-08).
  4. Chạy NER để trích số hiệu, ngày ban hành, cơ quan ban hành, và **yêu cầu báo cáo** nếu có (nội dung, hạn nộp, đơn vị chịu trách nhiệm).
- **Output:** Văn bản có cấu trúc + các trường metadata đã trích xuất (bao gồm loại văn bản và chủ đề)
- **Ngoại lệ:** Độ tin cậy NER hoặc phân loại chủ đề thấp → gắn cờ để cán bộ xác nhận thủ công thay vì tự động lưu

### WF-03 — Tóm tắt có trích dẫn (Grounded Summarization) — *quy trình lõi*
- **Actor:** Hệ thống (tự động), Cán bộ Phòng Đào tạo (rà soát — xem WF-07)
- **Trigger:** Văn bản đã hoàn tất WF-02
- **Input:** Các đoạn văn bản có cấu trúc
- **Các bước:**
  1. TextRank chọn ra các đoạn quan trọng nhất (extractive) làm ngữ cảnh giới hạn.
  2. BARTpho/ViT5 sinh câu tóm tắt **chỉ dựa trên** các đoạn đã chọn (extractive-guided abstractive), mỗi câu gắn kèm ID đoạn nguồn.
  3. Mô hình NLI phân loại **từng câu** thành 1 trong 3 nhãn: `entailment` (suy ra được từ nguồn), `contradiction` (mâu thuẫn với nguồn), `neutral` (không đủ căn cứ để khẳng định đúng/sai).
  4. Định tuyến theo nhãn:
     - **`entailment`** → giữ nguyên, gắn link trích dẫn, không cần con người can thiệp.
     - **`contradiction`** → gắn cờ mức độ ưu tiên **cao nhất**, đẩy vào hàng đợi rà soát (WF-07). **Toàn bộ văn bản chuyển trạng thái `pending_review`, KHÔNG được publish để phục vụ tra cứu (WF-05) cho tới khi mọi câu `contradiction` được cán bộ xử lý xong** — kể cả khi các câu còn lại đều đạt `entailment`.
     - **`neutral`** → gắn cờ mức độ ưu tiên thấp hơn, cũng đẩy vào hàng đợi rà soát, nhưng không nhất thiết chặn publish toàn văn bản nếu không có câu nào `contradiction` (tùy cấu hình — mặc định: `neutral` chỉ cảnh báo, không chặn).
  5. Nếu không có câu nào `contradiction` (và không còn `neutral` nào đang chờ) → văn bản tự động chuyển trạng thái `published`.
  6. Lưu bản tóm tắt kèm bảng ánh xạ câu → nguồn trích dẫn → nhãn NLI.
- **Output:** Bản tóm tắt có trích dẫn đầy đủ; trạng thái văn bản là `published` (sẵn sàng tra cứu) hoặc `pending_review` (đang chờ cán bộ xử lý)
- **Ngoại lệ:** Toàn bộ câu đều bị `contradiction` → hệ thống báo "không thể tóm tắt tự động, cần xử lý thủ công toàn bộ văn bản" thay vì cố đẩy hàng loạt vào hàng đợi rà soát riêng lẻ

### WF-07 — Rà soát & Duyệt nội dung (Human-in-the-loop)
- **Actor:** Cán bộ Phòng Đào tạo
- **Trigger:** Văn bản ở trạng thái `pending_review` (có câu bị gắn nhãn `contradiction` hoặc `neutral`)
- **Input:** Danh sách câu bị gắn cờ, kèm đoạn nguồn tương ứng
- **Các bước (theo đúng kịch bản GVHD nêu — ví dụ: 10 câu tóm tắt, 2 câu dưới ngưỡng):**
  1. Cán bộ mở mục "Cần rà soát", danh sách hiển thị **sắp xếp theo mức độ ưu tiên** (`contradiction` lên đầu, `neutral` sau).
  2. Với mỗi văn bản, hệ thống hiển thị **chính xác các câu bị gắn cờ, đặt cạnh đoạn văn gốc tương ứng** (không phải toàn bộ 10 câu, chỉ 2 câu có vấn đề) để cán bộ đối chiếu nhanh.
  3. Cán bộ đọc, phát hiện lỗi (ví dụ AI diễn đạt sai một thuật ngữ pháp lý), chọn 1 trong 3 hành động:
     - **Duyệt giữ nguyên** — chấp nhận câu dù bị gắn cờ (hệ thống gắn nhãn hiển thị "Đã xác nhận thủ công" để minh bạch, không hiển thị giống hệt câu tự động đạt).
     - **Sửa & duyệt** — cán bộ chỉnh sửa lại câu cho chính xác. Hệ thống **chạy lại NLI trên câu đã sửa** trước khi lưu (không mặc định tin rằng con người sửa là luôn đúng).
     - **Loại bỏ** — câu bị xóa khỏi bản tóm tắt hiển thị.
  4. Hệ thống ghi lại **audit trail**: nội dung AI sinh ra ban đầu, nội dung sau chỉnh sửa (nếu có), người duyệt, thời điểm.
  5. Khi **toàn bộ câu bị gắn cờ của văn bản đó** đã được xử lý (không còn câu `contradiction`/`neutral` nào ở trạng thái chờ) → văn bản **tự động chuyển từ `pending_review` sang `published`**, chính thức phục vụ tra cứu (WF-05).
- **Output:** Văn bản ở trạng thái `published`, kèm audit trail đầy đủ cho các câu đã qua rà soát
- **Ngoại lệ:** Câu sau khi sửa vẫn không đạt ngưỡng entailment khi chạy lại NLI → hệ thống không tự lưu, yêu cầu cán bộ xác nhận thêm một lần rõ ràng (tương tự nhánh "Duyệt giữ nguyên") trước khi chấp nhận

### WF-04 — Sinh gợi ý khung báo cáo
- **Actor:** Hệ thống (tự động), Giảng viên (sử dụng & hoàn thiện)
- **Trigger:** Văn bản được xác định (ở WF-02) có chứa yêu cầu báo cáo
- **Input:** Các trường đã trích xuất (nội dung yêu cầu, hạn nộp, căn cứ pháp lý, loại văn bản/chủ đề)
- **Các bước (đã bỏ khung 4 mục cố định dùng chung — theo yêu cầu GVHD, mỗi văn bản có form riêng):**
  1. Xác định loại báo cáo được yêu cầu (ví dụ: báo cáo định kỳ, báo cáo đột xuất, báo cáo tổng kết chuyên đề...).
  2. Tra cứu **Thư viện Template** (`ReportTemplate`) để tìm mẫu khung phù hợp nhất với loại báo cáo + chủ đề văn bản đó.
     - **Tìm được template khớp** → dùng cấu trúc đề mục riêng của template đó (mỗi loại báo cáo có bộ đề mục khác nhau, không giống nhau giữa các văn bản).
     - **Không tìm được template khớp** → hệ thống **tự dựng khung trực tiếp từ chính các đề mục được liệt kê trong văn bản gốc** (không rơi về một khung mặc định chung chung), đồng thời đề xuất lưu lại làm template mới cho lần sau.
  3. Điền tự động phần "Căn cứ pháp lý" bằng trích dẫn văn bản gốc.
  4. Điền các đề mục nội dung theo đúng yêu cầu nêu trong văn bản (không tự sinh số liệu/nội dung thực tế) — đề mục này khác nhau tùy template đã chọn ở bước 2.
  5. Xuất file khung báo cáo (docx) cho giảng viên tải về và hoàn thiện.
- **Output:** File khung báo cáo có cấu trúc **riêng theo đúng loại văn bản**, kèm trích dẫn căn cứ
- **Ràng buộc quan trọng:** Hệ thống **không được tự sinh nội dung/số liệu báo cáo thực tế** — chỉ gợi ý cấu trúc và căn cứ, đúng theo yêu cầu chống bịa đặt của GVHD. Việc "mỗi văn bản có form riêng" chỉ áp dụng cho **cấu trúc đề mục**, không mở rộng ràng buộc an toàn này.

### WF-05 — Tra cứu & Hỏi đáp (Semantic Search / RAG)
- **Actor:** Giảng viên, cán bộ, sinh viên
- **Trigger:** Người dùng đặt câu hỏi trên chatbot hoặc tìm kiếm trên dashboard
- **Input:** Câu hỏi/từ khóa tự nhiên
- **Các bước:**
  1. Sinh embedding cho câu hỏi, truy vấn Vector DB — **chỉ tìm trong các văn bản ở trạng thái `published`** (đã qua WF-07 nếu từng bị gắn cờ).
  2. Đưa các đoạn này làm ngữ cảnh cho mô hình sinh câu trả lời (retrieval-augmented generation).
  3. Kiểm tra NLI cho câu trả lời như WF-03 (bước 3); nếu câu trả lời bị phân loại `contradiction`/`neutral` → không hiển thị, coi như không đủ căn cứ.
  4. Trả lời kèm link trích dẫn tới văn bản/điều khoản gốc.
- **Output:** Câu trả lời có trích dẫn, hoặc thông báo "không tìm thấy thông tin liên quan" nếu không đủ căn cứ
- **Ngoại lệ:** Không tìm được đoạn liên quan đủ tin cậy, hoặc văn bản liên quan nhất vẫn đang `pending_review` → từ chối trả lời thay vì suy đoán hoặc dùng nội dung chưa được duyệt

### WF-06 — "Cây văn bản": Văn bản liên quan & Mức độ áp dụng cho trường
- **Actor:** Giảng viên, Cán bộ Phòng Đào tạo (xem), Hệ thống (đề xuất tự động)
- **Trigger:** Người dùng mở chi tiết một văn bản bất kỳ
- **Input:** Văn bản đang xem, toàn bộ kho văn bản đã `published`
- **Các bước (phạm vi rút gọn — tận dụng hạ tầng đã có ở WF-05, không xây thêm mô hình mới):**
  1. **Quan hệ tường minh (rule-based, chi phí thấp):** NER/regex phát hiện cụm từ chỉ quan hệ ("thay thế", "sửa đổi", "bãi bỏ", "căn cứ") kèm số hiệu văn bản được nhắc tới → tạo quan hệ `can_cu`/`thay_the`/`sua_doi` giữa 2 văn bản.
  2. **Quan hệ ngữ nghĩa (tái sử dụng Embedding + Vector DB đã xây cho WF-05):** dùng chính vector của văn bản đang xem để truy vấn top-k văn bản gần nghĩa nhất trong kho — không cần huấn luyện thêm mô hình nào, chỉ đổi "câu hỏi" đầu vào của Retrieval Service (SVC-05) từ câu hỏi người dùng thành nội dung văn bản hiện tại.
  3. **Mức độ áp dụng cho trường:** mỗi văn bản được gắn 1 trong các nhãn `pham_vi_ap_dung` (ví dụ: "Áp dụng trực tiếp — có quy chế nội bộ trường cụ thể hóa", "Áp dụng chung, chưa có văn bản nội bộ tương ứng", "Chỉ mang tính tham khảo"). Gán ban đầu bán tự động: nếu quan hệ ngữ nghĩa ở bước 2 tìm thấy một văn bản nội bộ trường đủ gần nghĩa → đề xuất nhãn "Áp dụng trực tiếp", cán bộ xác nhận lại (human-in-the-loop, tương tự WF-07 nhưng không bắt buộc gắn cờ contradiction).
  4. Hiển thị kết quả dạng danh sách/cây: văn bản liên quan trực tiếp (thay thế/căn cứ) tách riêng khỏi văn bản liên quan về chủ đề (ngữ nghĩa).
- **Output:** Danh sách văn bản liên quan phân theo loại quan hệ, kèm nhãn mức độ áp dụng cho trường
- **Ngoại lệ:** Không tìm được văn bản liên quan nào đủ gần nghĩa (dưới ngưỡng similarity) → hiển thị "Chưa phát hiện văn bản liên quan", không ép hiển thị kết quả không đủ liên quan
- **Ghi chú phạm vi:** Đây là **bản rút gọn** của việc quản lý vòng đời văn bản đầy đủ — chỉ hiển thị quan hệ, **không tự động cập nhật trạng thái hiệu lực** (việc này vẫn đòi hỏi cán bộ tự xác nhận thủ công trong `Document.trang_thai_hieu_luc`, xem mục 5). Quản lý vòng đời tự động đầy đủ (cảnh báo hết hiệu lực, quy trình phê duyệt thay thế) vẫn nằm ngoài phạm vi 12 tuần (xem mục 0.2).

---

### WF-08 — Duyệt văn bản theo Chủ đề (Topic Dashboard)
- **Actor:** Cán bộ Phòng Đào tạo
- **Trigger:** Cán bộ mở màn hình quản trị nội dung
- **Các bước:**
  1. Hệ thống nhóm toàn bộ văn bản đã nạp theo chủ đề đã phân loại ở WF-02, hiển thị dạng thẻ chủ đề (mỗi thẻ = 1 chủ đề, kèm số lượng văn bản).
  2. Cán bộ bấm vào 1 chủ đề → xem danh sách thông tư/quyết định/công văn thuộc chủ đề đó, kèm trạng thái (`published`/`pending_review`).
  3. Khu vực nạp văn bản mới (WF-01) và hàng đợi xử lý vẫn hiển thị như một khu vực riêng trong cùng màn hình, không thay thế — Dashboard theo chủ đề là **cách tổ chức lại phần duyệt/xem**, không phải bỏ đi phần vận hành.
- **Output:** Cán bộ tìm đúng nhóm văn bản cần theo chủ đề, thay vì lướt một danh sách phẳng
- **Ngoại lệ:** Văn bản chưa được phân loại chủ đề (độ tin cậy classification thấp) → xếp vào nhóm "Chưa phân loại", không tự ý gán bừa vào 1 chủ đề

---

## 3. QUẢN LÝ DỰ ÁN & PHÂN RÃ CÔNG VIỆC (AGILE/SCRUM FRAMEWORK)

### 3.1 Giả định về nhóm
Kế hoạch dưới đây áp dụng cho **nhóm 2 sinh viên, thời hạn 12 tuần**. Vì quy mô và thời gian ngắn hơn mức chuẩn (1 học kỳ ~15 tuần, nhóm 2-3 người), kế hoạch được thiết kế lại theo 2 nguyên tắc:
1. **Cắt phần "nặng nhất" của mỗi hạng mục mở rộng, giữ lại phần lõi có giá trị** — quản lý vòng đời văn bản đầy đủ (cảnh báo tự động hết hiệu lực) vẫn ngoài phạm vi, nhưng "Cây văn bản" (hiển thị quan hệ, tận dụng hạ tầng RAG có sẵn) được đưa lại vào phạm vi theo yêu cầu GVHD vì chi phí triển khai thấp hơn nhiều so với giá trị mang lại.
2. **Làm việc theo 2 track song song** thay vì tuần tự, vì chỉ có 2 người và không đủ thời gian để làm lần lượt từng module.

> **Lưu ý:** Sau khi GVHD bổ sung 5 yêu cầu (nguồn dữ liệu mở rộng, cơ chế rà soát contradiction, Cây văn bản, Dashboard theo chủ đề, đa dạng hóa template báo cáo), khối lượng công việc đã tăng đáng kể so với kế hoạch gốc. Sprint plan ở mục 3.3 đã được thiết kế lại để hấp thụ phần lớn khối lượng này bằng cách **tái sử dụng hạ tầng đã có** (Embedding/Vector DB dùng chung cho cả RAG lẫn Cây văn bản) thay vì xây thêm hệ thống riêng — nhưng đây vẫn là lịch trình khá chặt, xem Risk Register (mục 7) để biết phương án cắt giảm nếu trễ tiến độ.

| Vai trò Scrum | Người đảm nhận |
|---|---|
| Product Owner | Giảng viên hướng dẫn (định hướng yêu cầu, nghiệm thu) |
| Scrum Master kiêm Dev | Luân phiên giữa 2 thành viên theo từng sprint |
| Development Team | Cả 2 thành viên, chia theo 2 track song song (xem 3.1.1) |

### 3.1.1 Phân chia Track công việc

Vì chỉ có 2 người, cần chia việc theo track rõ ràng để làm song song thay vì chờ nhau:

| Track | Người phụ trách | Phạm vi |
|---|---|---|
| **Track A — Data & Pipeline** | Thành viên 1 | Ingestion (EPIC-1), Extraction/OCR/Classification (bao gồm phân loại chủ đề) /NER (EPIC-2), Thư viện Template + Report Suggestion (EPIC-4), Dashboard theo chủ đề & DevOps (EPIC-7, EPIC-10) |
| **Track B — AI Core** | Thành viên 2 | Fine-tune tóm tắt (EPIC-3), NLI 3 nhãn + Review Service (EPIC-3, EPIC-9), Embedding + RAG chatbot + Cây văn bản (EPIC-5, EPIC-6 — dùng lại cùng hạ tầng embedding) |

Cả hai cùng tham gia Sprint đánh giá & viết báo cáo cuối kỳ (EPIC-8), và cùng làm phần **NLI 3 nhãn + cơ chế rà soát/publish** (Sprint 3) vì đây là phần lõi quan trọng nhất, cần cả 2 người tập trung thay vì chỉ 1 người làm.

### 3.2 Product Backlog (Epics)

| Epic | Mô tả | Liên kết Workflow |
|---|---|---|
| EPIC-1 | Hạ tầng nạp & lưu trữ văn bản | WF-01 |
| EPIC-2 | Trích xuất & phân loại văn bản (loại + chủ đề) | WF-02 |
| EPIC-3 | Tóm tắt có trích dẫn + phân loại NLI 3 nhãn (lõi) | WF-03 |
| EPIC-4 | Gợi ý khung báo cáo theo Thư viện Template | WF-04 |
| EPIC-5 | Tra cứu & Chatbot RAG (chỉ trên văn bản `published`) | WF-05 |
| EPIC-6 | "Cây văn bản" — quan hệ + mức độ áp dụng cho trường | WF-06 — **đưa lại vào phạm vi, bản rút gọn (tận dụng hạ tầng EPIC-5)** |
| EPIC-7 | Dashboard & trải nghiệm người dùng | Toàn bộ |
| EPIC-8 | Đánh giá hệ thống & viết báo cáo đồ án | Toàn bộ |
| EPIC-9 | Review Service — rà soát & duyệt (human-in-the-loop) | WF-07 |
| EPIC-10 | Dashboard theo chủ đề | WF-08 |

### 3.3 Kế hoạch Sprint (12 tuần, 2 người làm song song 2 track)

| Sprint | Tuần | Track A (Data & Pipeline) | Track B (AI Core) |
|---|---|---|---|
| Sprint 0 | 1–2 | Setup môi trường chung, thu thập ~20-30 văn bản từ **chinhphu.vn + tài liệu liên quan trường**, cùng thiết kế data model (đã mở rộng: ReviewItem, ReportTemplate, Topic — xem mục 5) | (làm chung với Track A) |
| Sprint 1 | 3–4 | EPIC-1: Ingestion service, lưu trữ file + metadata, chia đoạn theo Điều/Khoản | Chuẩn bị dữ liệu fine-tune, cài baseline TextRank |
| Sprint 2 | 5–6 | EPIC-2: OCR, Classification (loại văn bản **+ chủ đề**), NER cơ bản | EPIC-3 (phần 1): Fine-tune BARTpho/ViT5 cho tóm tắt |
| Sprint 3 | 7–8 | **Cả 2 người cùng làm:** EPIC-3 (phần 2) — NLI phân loại 3 nhãn (entailment/contradiction/neutral) + citation mapping; **EPIC-9** — Review Service (hàng đợi rà soát, audit trail, cơ chế publish theo văn bản) | |
| Sprint 4 | 9–10 | EPIC-4: Thư viện Template + Report Suggestion theo từng loại; bắt đầu UI Dashboard theo chủ đề (EPIC-10) | EPIC-5: Embedding + RAG chatbot (chỉ trên văn bản `published`); **EPIC-6** — Cây văn bản (tái sử dụng Vector DB của EPIC-5, không xây thêm mô hình) |
| Sprint 5 | 11 | **Cả 2 người:** Ghép nối toàn bộ pipeline end-to-end, hoàn thiện Dashboard theo chủ đề + hiển thị Cây văn bản, sửa lỗi | |
| Sprint 6 | 12 | **Cả 2 người:** EPIC-8 — Đánh giá (ROUGE/BERTScore/Faithfulness theo 3 nhãn, chất lượng gợi ý văn bản liên quan), viết báo cáo, chuẩn bị demo | |

> **Lưu ý về độ chặt của lịch:** So với bản gốc, Sprint 3 giờ gánh cả NLI 3 nhãn lẫn Review Service, Sprint 4 gánh cả Template Library lẫn Cây văn bản — đây là 2 sprint rủi ro cao nhất. Nếu tới giữa Sprint 3/4 vẫn chưa xong, **thứ tự cắt giảm ưu tiên** (theo mục 0.2): (1) cắt phần "mức độ áp dụng cho trường" trong Cây văn bản trước (giữ lại quan hệ tường minh + ngữ nghĩa cơ bản), (2) rút gọn Thư viện Template xuống còn 2-3 mẫu thay vì nhiều loại, (3) **không bao giờ cắt** cơ chế NLI 3 nhãn + Review Service vì đây là yêu cầu an toàn cốt lõi.

### 3.4 Ví dụ User Stories (Sprint 1–2)

- *"Là quản trị viên, tôi muốn upload file PDF văn bản để hệ thống tự động lưu trữ và gán mã, để không phải quản lý file thủ công."*
- *"Là hệ thống, tôi cần chia văn bản thành các đoạn theo Điều/Khoản kèm ID, để phục vụ trích dẫn chính xác sau này."*
- *"Là cán bộ đào tạo, tôi muốn biết văn bản vừa nạp thuộc loại nào (thông tư/quyết định/công văn), để phân loại nhanh."*

### 3.5 Definition of Done (DoD)
Một hạng mục được coi là "Done" khi:
1. Chức năng chạy được end-to-end trên dữ liệu mẫu thật (không phải dữ liệu giả lập).
2. Có test cơ bản (unit test cho logic, script đánh giá cho mô hình).
3. Với các bước liên quan đến sinh nội dung (tóm tắt, gợi ý báo cáo): **đã qua kiểm tra faithfulness**, không có câu nào thiếu trích dẫn.
4. Đã cập nhật tài liệu (README/mô tả API).
5. Được demo cho GVHD trong buổi review sprint.

### 3.6 Nghi thức Scrum (điều chỉnh cho bối cảnh đồ án)

| Nghi thức | Tần suất | Hình thức |
|---|---|---|
| Sprint Planning | Đầu mỗi sprint (2 tuần/lần) | Nhóm tự họp, chốt backlog cho sprint |
| Daily/Weekly Check-in | Hàng tuần | Nhóm tự cập nhật tiến độ (Kanban board) |
| Sprint Review | Cuối mỗi sprint | Demo tiến độ cho GVHD, nhận góp ý |
| Sprint Retrospective | Cuối mỗi sprint | Nhóm tự đánh giá điều làm tốt/chưa tốt |

**Công cụ đề xuất:** Trello/Jira/Notion cho backlog & Kanban board, GitHub Projects nếu muốn gắn liền với mã nguồn.

---

## 4. TIÊU CHUẨN VẬN HÀNH & CI/CD (DEVOPS STANDARDS)

### 4.1 Quản lý mã nguồn (Git Workflow)

- **Chiến lược nhánh:** `main` (ổn định, dùng để demo) ← `develop` (tích hợp) ← `feature/<ten-tinh-nang>` (phát triển từng phần)
- **Quy ước đặt tên nhánh:** `feature/ner-extraction`, `feature/summarization-citation`, `fix/ocr-encoding`
- **Quy ước commit message:** theo chuẩn Conventional Commits — `feat: thêm citation mapping cho summarization`, `fix: sửa lỗi encoding OCR tiếng Việt`
- **Code review:** mọi merge vào `develop`/`main` cần ít nhất 1 thành viên khác review (nếu nhóm ≥ 2 người)

### 4.2 Môi trường triển khai

| Môi trường | Mục đích | Ghi chú |
|---|---|---|
| Local Dev | Từng thành viên phát triển & test | Dùng `.env` riêng, dữ liệu mẫu nhỏ |
| Demo/Staging | Chạy thử end-to-end trước khi báo cáo | Dùng docker-compose, dữ liệu ~30-50 văn bản thật |
| Production | Ngoài phạm vi đồ án (giả định nếu trường triển khai thật) | Không bắt buộc triển khai thật trong học kỳ |

### 4.3 Pipeline CI/CD (đề xuất dùng GitHub Actions)

```
Push code lên branch
      │
      ▼
[CI] Lint & format check (flake8/black)
      │
      ▼
[CI] Unit test (pytest) — logic nghiệp vụ, API endpoints
      │
      ▼
[CI] Model evaluation script — chạy ROUGE/BERTScore/Faithfulness
      trên tập validation nhỏ, cảnh báo nếu điểm giảm so với baseline
      │
      ▼
[CD] Build Docker image (chỉ khi merge vào main)
      │
      ▼
[CD] Deploy lên môi trường Demo/Staging
```

### 4.4 Tiêu chuẩn kiểm thử (Testing Standards)

| Loại test | Phạm vi | Công cụ |
|---|---|---|
| Unit test | Từng hàm xử lý (extraction, chunking, API logic) | pytest |
| Integration test | Luồng end-to-end (upload → tóm tắt → trả kết quả) | pytest + test data mẫu |
| Model evaluation | Chất lượng tóm tắt (ROUGE, BERTScore) và độ trung thực (Faithfulness/NLI score) | Script đánh giá riêng, chạy định kỳ trong CI |
| Regression check | Đảm bảo thay đổi mới không làm giảm điểm faithfulness trung bình | So sánh với baseline đã lưu |

### 4.5 Đóng gói & Triển khai

- **Containerization:** mỗi service (Ingestion, Extraction, Summarization, Retrieval) đóng gói bằng Docker riêng, quản lý chung bằng `docker-compose.yml` để chạy toàn bộ hệ thống bằng một lệnh khi demo.
- **Quản lý cấu hình:** dùng file `.env` cho các thông số nhạy cảm (đường dẫn model, config DB), không hard-code trong source.
- **Quản lý phiên bản mô hình:** lưu rõ version của mô hình đã fine-tune (ví dụ `bartpho-summary-v1.2`) để dễ rollback nếu bản mới cho kết quả kém hơn.

### 4.6 Giám sát & Nhật ký (Logging & Monitoring)

- Log lại mọi câu hỏi/tóm tắt hệ thống sinh ra kèm điểm faithfulness — phục vụ việc rà soát chất lượng và làm minh chứng trong báo cáo đồ án.
- Ghi nhận các trường hợp hệ thống từ chối trả lời (do không đủ căn cứ) để phân tích tỷ lệ "an toàn" của hệ thống.
- Dashboard đơn giản hiển thị số liệu: số văn bản đã xử lý, điểm faithfulness trung bình, số câu hỏi đã trả lời.

---

## 5. MÔ HÌNH DỮ LIỆU (DATA MODEL — RÚT GỌN)

| Bảng/Entity | Trường chính | Mô tả |
|---|---|---|
| **Document** | id, ten_van_ban, so_hieu, loai_van_ban, **chu_de**, **pham_vi_ap_dung**, nguon_du_lieu (chinhphu.vn/moet.gov.vn/noi_bo_truong), ngay_ban_hanh, co_quan_ban_hanh, file_goc_url, trang_thai_hieu_luc, **trang_thai_xuat_ban** (`pending_review`/`published`) | Thông tin văn bản gốc |
| **DocumentChunk** | id, document_id, dieu_khoan, noi_dung, so_trang | Từng đoạn văn bản có thể trích dẫn |
| **Summary** | id, document_id, noi_dung_tom_tat, ngay_tao, phien_ban_model | Bản tóm tắt sinh ra |
| **Citation** | id, summary_id (hoặc query_log_id), chunk_id, cau_tom_tat, diem_faithfulness, **nhan_nli** (`entailment`/`contradiction`/`neutral`) | Ánh xạ câu tóm tắt/trả lời ↔ đoạn nguồn, kèm nhãn phân loại NLI |
| **ReviewItem** *(mới — EPIC-9)* | id, citation_id, document_id, nhan_nli, do_uu_tien, trang_thai (`pending`/`approved`/`edited`/`rejected`) | Hàng đợi rà soát cho các câu bị gắn cờ `contradiction`/`neutral` |
| **ReviewLog** *(mới — EPIC-9)* | id, review_item_id, cau_ai_sinh, cau_sau_sua (nullable), reviewer_id, hanh_dong, diem_nli_sau_sua (nullable), thoi_gian | Audit trail — lưu vết mọi quyết định rà soát |
| **ReportTemplate** *(mới — EPIC-4)* | id, loai_bao_cao, chu_de_ap_dung, danh_sach_de_muc (JSON) | Thư viện mẫu khung báo cáo — mỗi loại báo cáo một cấu trúc đề mục riêng |
| **ReportSuggestion** | id, document_id, template_id (nullable — null nếu tự dựng khung từ văn bản gốc), loai_bao_cao, khung_noi_dung, han_nop | Khung báo cáo được gợi ý cho 1 văn bản cụ thể |
| **QueryLog** | id, cau_hoi, cau_tra_loi, danh_sach_citation, diem_faithfulness, thoi_gian | Nhật ký hỏi-đáp phục vụ giám sát chất lượng |
| **DocumentRelation** *(mở rộng — EPIC-6)* | id, document_id_a, document_id_b, loai_quan_he (`can_cu`/`thay_the`/`sua_doi`/`bai_bo`/**`lien_quan_ngu_nghia`**), diem_tuong_dong (nullable, chỉ dùng cho quan hệ ngữ nghĩa) | Quan hệ giữa các văn bản — cả tường minh (rule-based) lẫn ngữ nghĩa (embedding) |
| **Topic** *(mới — EPIC-10)* | id, ten_chu_de | Danh mục chủ đề cố định (Đào tạo, Tuyển sinh, Tài chính...) phục vụ Dashboard theo chủ đề |
| **User** | id, ho_ten, vai_tro (giang_vien/can_bo/admin) | Người dùng hệ thống |

---

## 6. YÊU CẦU PHI CHỨC NĂNG & BẢO MẬT

| Hạng mục | Yêu cầu |
|---|---|
| **Độ trung thực (Faithfulness)** | ≥ ngưỡng đặt ra (ví dụ 90% câu tóm tắt phải qua được kiểm tra NLI) — đây là chỉ số quan trọng nhất của hệ thống |
| **Hiệu năng** | Thời gian tóm tắt 1 văn bản trung bình (≤ 5 trang) không quá 30-60 giây trên phần cứng demo |
| **Bảo mật dữ liệu** | Văn bản nội bộ (nếu có tính nhạy cảm) chỉ truy cập được bởi tài khoản được phân quyền |
| **Toàn vẹn trích dẫn** | Không cho phép hiển thị bất kỳ câu tóm tắt/trả lời nào thiếu link trích dẫn nguồn |
| **Khả năng mở rộng** | Kiến trúc phải cho phép thêm loại văn bản mới (ví dụ tài liệu giảng dạy) mà không cần đổi toàn bộ pipeline |
| **Khả năng kiểm chứng** | Mọi kết quả AI sinh ra phải lưu vết (model version, thời gian, điểm tin cậy) để phục vụ audit |

---

## 7. QUẢN LÝ RỦI RO (RISK REGISTER)

| Rủi ro | Khả năng | Ảnh hưởng | Biện pháp giảm thiểu |
|---|---|---|---|
| Mô hình vẫn "bịa" thông tin dù đã qua NLI check | Trung bình | Cao | Đặt ngưỡng faithfulness nghiêm ngặt; khi nghi ngờ, ưu tiên từ chối trả lời hơn là trả lời sai |
| Dữ liệu huấn luyện tóm tắt tiếng Việt hạn chế | Cao | Trung bình | Kết hợp fine-tune trên dataset công khai (VietNews) + dữ liệu tự thu thập từ văn bản pháp quy |
| OCR sai với văn bản scan chất lượng thấp | Trung bình | Trung bình | Ưu tiên thu thập văn bản dạng PDF gốc (không phải scan) khi có thể; báo lỗi rõ ràng khi OCR không đạt |
| Khối lượng công việc vượt quá 12 tuần **(rủi ro tăng sau khi bổ sung 5 yêu cầu)** | **Cao** | Cao | Đã có thứ tự cắt giảm ưu tiên rõ ràng (mục 3.3): Cây văn bản → Thư viện Template → không bao giờ cắt NLI 3 nhãn/Review Service; giảm số văn bản thử nghiệm xuống 20-30 nếu cần |
| Một trong 2 thành viên nghỉ/giảm tiến độ giữa kỳ | Trung bình | **Cao** (nhóm chỉ có 2 người nên mất 1 người ảnh hưởng ~50% năng lực) | Cả 2 người cùng nắm được phần lõi (Sprint 3 — NLI 3 nhãn + Review Service) thay vì chỉ 1 người biết; code/tài liệu cập nhật thường xuyên lên Git để người còn lại có thể tiếp tục |
| 2 track (Data & AI Core) lệch tiến độ, gây nghẽn khi ghép nối ở Sprint 4–5 | Trung bình | Trung bình | Thống nhất sớm định dạng dữ liệu trung gian (schema DocumentChunk, ReviewItem) ngay từ Sprint 0, để 2 track có thể phát triển độc lập mà vẫn tương thích khi ghép |
| **(Mới)** Cơ chế "chặn publish toàn văn bản khi có câu contradiction" (WF-03/WF-07) làm nghẽn hàng đợi rà soát nếu mô hình NLI ban đầu còn nhiều lỗi | Trung bình-Cao | Trung bình | Ưu tiên xử lý theo mức độ nghiêm trọng (contradiction trước neutral); nếu tỷ lệ contradiction quá cao trong tuần đầu Sprint 3, xem lại ngưỡng phân loại của NLI trước khi đổ lỗi cho quy trình rà soát |
| **(Mới)** Phân loại "chủ đề" và "mức độ áp dụng cho trường" không đủ chính xác do danh mục chủ đề tự định nghĩa, thiếu dữ liệu huấn luyện riêng | Trung bình | Thấp-Trung bình | Dùng danh mục chủ đề **cố định, số lượng nhỏ** (5-6 chủ đề) thay vì phân loại mở, dễ đạt độ chính xác chấp nhận được hơn; luôn cho cán bộ xác nhận lại (human-in-the-loop) trước khi công bố |

---

## 8. TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA)

Hệ thống được coi là đạt mục tiêu đồ án khi:

1. Xử lý thành công end-to-end tối thiểu 20-25 văn bản thật, lấy từ **chinhphu.vn và tài liệu liên quan trực tiếp tới trường** — con số giảm so với mức chuẩn 30+ để phù hợp với thời hạn 12 tuần/2 người.
2. Bản tóm tắt đạt điểm ROUGE-L và BERTScore trong khoảng chấp nhận được so với baseline TextRank (chứng minh mô hình fine-tune có cải thiện).
3. Điểm Faithfulness trung bình đạt ngưỡng đề ra (ví dụ ≥ 90%), **không có trường hợp nào bản tóm tắt thiếu trích dẫn**.
4. **100% văn bản có câu bị NLI gắn nhãn `contradiction` không được xuất hiện ở trạng thái `published` cho tới khi qua rà soát (WF-07)** — kiểm tra bằng cách rà soát trực tiếp trạng thái trong database, không chỉ tin vào giao diện.
5. Chatbot RAG trả lời đúng và có trích dẫn cho tối thiểu 80% câu hỏi thử nghiệm trong tập test, và không bao giờ trả lời dựa trên văn bản đang `pending_review`.
6. Chức năng gợi ý khung báo cáo tạo ra được khung đúng cấu trúc cho tối thiểu 3 loại văn bản yêu cầu báo cáo khác nhau, **với ít nhất 2 template khác nhau rõ rệt về cấu trúc đề mục** (chứng minh không dùng chung 1 khung).
7. Chức năng "Cây văn bản" hiển thị được văn bản liên quan (tối thiểu quan hệ ngữ nghĩa) cho tối thiểu 80% văn bản trong tập test có văn bản liên quan thực sự tồn tại trong kho.
8. Dashboard theo chủ đề nhóm đúng văn bản vào chủ đề tương ứng cho tối thiểu 85% văn bản trong tập test (đối chiếu với gán nhãn tay).
9. Demo chạy được toàn bộ luồng qua Docker (một lệnh khởi động).

---

## 9. PHỤ LỤC: THUẬT NGỮ

| Thuật ngữ | Giải thích |
|---|---|
| **Grounded Summarization** | Tóm tắt có căn cứ — mỗi câu tóm tắt được gắn với nguồn cụ thể trong văn bản gốc |
| **Faithfulness** | Độ trung thực — mức độ nội dung sinh ra đúng với/được suy ra từ nguồn, không bịa thêm |
| **Hallucination** | Hiện tượng mô hình AI sinh ra thông tin không có căn cứ trong dữ liệu nguồn |
| **RAG (Retrieval-Augmented Generation)** | Kỹ thuật kết hợp tìm kiếm thông tin liên quan rồi mới sinh câu trả lời, giúp giảm hallucination |
| **NLI (Natural Language Inference)** | Bài toán suy luận ngôn ngữ: xác định một câu có được suy ra (entailment) từ một câu/đoạn khác không |
| **Chunk** | Đoạn văn bản nhỏ (thường theo Điều/Khoản) được đánh ID để phục vụ trích dẫn |
| **Entailment / Contradiction / Neutral** | 3 nhãn đầu ra của mô hình NLI: câu suy ra được từ nguồn / câu mâu thuẫn với nguồn / không đủ căn cứ để khẳng định |
| **Human-in-the-loop** | Nguyên tắc thiết kế: hệ thống AI chỉ đề xuất, con người luôn xác nhận trước khi nội dung được công bố chính thức |
| **Publish Gate** | Cơ chế chặn không cho một văn bản chuyển sang trạng thái `published` (phục vụ tra cứu) nếu còn câu chưa qua rà soát |
| **Cây văn bản** | Cách gọi của GVHD cho tính năng hiển thị các văn bản liên quan (quan hệ tường minh và ngữ nghĩa) tới văn bản đang xem |
| **Audit Trail** | Nhật ký lưu vết mọi thay đổi thủ công (ai sửa, sửa gì, khi nào) phục vụ truy vết và minh bạch |

---

*Tài liệu này là bản đặc tả sống (living document) — cần cập nhật khi phạm vi hoặc kiến trúc thay đổi trong quá trình triển khai đồ án.*
