# Kế hoạch: Biên soạn bộ tài liệu báo cáo DAU Second Brain (bám sát code thực tế)

## Mục tiêu

Biên soạn 8 tài liệu Markdown (tiếng Việt) trong `docs/`, phục vụ việc viết báo cáo đồ án.
Nội dung **bám sát mã nguồn thực tế** (đã được user xác nhận), không giữ nguyên đặc tả kế hoạch cũ.
Tài liệu cũ được giữ nguyên làm đối chiếu lịch sử; bản mới tạo riêng.

## Quyết định đã chốt (từ phỏng vấn)

1. **Hướng nội dung**: bám sát code thực tế; các hạng mục kế hoạch không triển khai ghi chú "điều chỉnh/rút gọn".
2. **Vị trí**: tạo bản mới riêng (giữ 4 file kế hoạch cũ).
3. **Tài liệu bổ sung**: cả 4 (CSDL, API, kết quả kiểm thử, hướng dẫn triển khai/vận hành).

## Ground truth (code thực tế — KHÔNG tin README.md gốc, nó mô tả kiến trúc cũ)

| File | Cung cấp cho tài liệu |
|---|---|
| `backend/app/services/nlp_pipeline.py` | Thuật toán thực: regex bóc tách obligation/threshold/metadata/relations; `classify_text` (keyword scoring); ViT5 summarize; mDeBERTa QA + NLI; MiniLM-L3 embedding; Gemini RAG (3 key luân phiên). |
| `backend/app/services/pdf_parser.py` | Đọc PDF (PyMuPDF), fallback OCR Gemini, `chunk_document` (adaptive chunking). |
| `backend/app/services/ocr_api.py` | OCR qua Gemini API, retry/backoff, giới hạn, không log key. |
| `backend/app/services/vector_db.py` | FAISS IndexFlatIP + normalize L2 (cosine), lưu `data/`. |
| `backend/app/services/ingestion/crawl_documents.py` | Crawler `vanban.chinhphu.vn`, phân domain/category, lọc năm >=2018. |
| `backend/app/services/notifier.py` | SSE push update (real-time). |
| `backend/app/db/models.py` | 9 bảng thực tế (xem Doc 5). |
| `backend/app/api/routers/*.py` (9 file) | API surface (xem Doc 6). |
| `backend/app/main.py` | Khởi tạo DB `create_all`, APScheduler cron 2:00 + ping 30ph. |
| `backend/app/core/config.py`, `security.py` | Cấu hình `.env`, JWT (HS256). |
| `backend/tests/test_ocr_api.py`, `test_pdf_parser_limits.py` | 12 test thực tế (xem Doc 7). |
| `frontend/src/App.tsx` | 17 trang + nhóm quyền admin/lecturer (xem Doc 2/6). |
| `deploy/HUONG_DAN_TRIEN_KHAI.md` + `README-local-test.md` + `tailscale-setup.md` | Nguồn Doc 8. |

## Bảng thực tế so kế hoạch (dùng làm "đối chiếu" trong Doc 1–3)

| Hạng mục | Kế hoạch (docs cũ) | Thực tế (code) |
|---|---|---|
| Bóc tách / NER | PhoBERT+CRF, ML classifier | **Regex/rule-based** trong `nlp_pipeline.py` |
| Phân loại chủ đề | Classification model | **Chấm điểm từ khóa** (`classify_text`, 6 chủ đề + "Khác") |
| Tóm tắt | BARTpho/ViT5 + TextRank + fine-tune | **ViT5 pretrained** (`vit5-base-vietnews-summarization`), lazy-load, giữ 1 model/RAM |
| NLI | 3 nhãn | **Có** — `mDeBERTa-v3-base-xnli-...`, áp cho tóm tắt nghĩa vụ/threshold (`nli_label`) |
| QA | — | `mdeberta-v3-base-squad2` (định nghĩa sẵn trong code, dùng lazy) |
| Embedding | MiniLM-L12 | **MiniLM-L3-v2** (384-dim) |
| Vector search | pgvector/Chroma | **FAISS local** (+ `DocumentEmbedding` JSONB trong PG; comment ghi máy user chưa cài pgvector — ghi đúng sự thật: deploy cài pgvector nhưng code lưu JSONB) |
| OCR | Tesseract/PaddleOCR | **Gemini API** (key riêng, có cờ `allow_external_ocr`) |
| Chatbot RAG | NLI kiểm tra câu trả lời | **Gemini** (3 key luân phiên, fallback model, chống bịa bằng prompt, không NLI) |
| Review Service | Bảng ReviewItem/ReviewLog | Rút gọn: `Obligation/Threshold.status` pending_review→published/rejected + bảng `AuditTrail` + `POST /review/revalidate` |
| Khung báo cáo | Thư viện Template (bảng) | **Có** — `reports.py` tạo `.docx` theo loại văn bản (python-docx, if/elif theo QD/TB/TT_ND/KH_HD/CT/CV/NQ) |
| Kiểm định chéo | Bảng Warning/ValidityEvent | **Có** — suy từ `DocumentRelation` (`/auditing/warnings`, `/analytics`, `/documents/impact`) |
| Đánh giá định lượng | ROUGE/BERTScore script trong CI | **Không có** script (chỉ 12 unit test) — ghi là "chưa tự động hoá" |

## Danh sách 8 file đầu ra (trong `docs/`)

1. `DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc_BAOCAO.md`
2. `DAU_Second_Brain_Dac_Ta_Yeu_Cau_Chuc_Nang_BAOCAO.md`
3. `DAU_Second_Brain_De_Cuong_Chi_Tiet_BAOCAO.md`
4. `CÁC THUẬT TOÁN SỬ DỤNG_BAOCAO.md`
5. `DAU_Second_Brain_Thiet_Ke_CSDL.md`
6. `DAU_Second_Brain_Mo_Ta_API.md`
7. `DAU_Second_Brain_Ket_Qua_Kiem_Thu_Danh_Gia.md`
8. `DAU_Second_Brain_Huong_Dan_Trien_Khai_Van_Hanh.md`

## Nội dung từng tài liệu

### Doc 1 — Đặc tả Nghiệp vụ & Kiến trúc (BAOCAO)
Cấu trúc bám theo bản cũ nhưng nội dung thực tế:
- Metadata (phiên bản 2.0, trạng thái "Báo cáo — thực tế triển khai").
- **Kiến trúc 3 tầng thực tế**: Frontend (React 19 + Vite 8 + Axios, 17 trang, 2 role admin/lecturer) → Backend (FastAPI, 9 router, SQLAlchemy, APScheduler) → Data (PostgreSQL 9 bảng, FAISS index + JSONB, file system `data/uploads` + `data/vanban_caotudong`). AI layer: ViT5, mDeBERTa (QA+NLI), MiniLM-L3, Gemini (OCR+RAG).
- **Sơ đồ luồng dữ liệu thực tế**: upload/crawl → PyMuPDF (fallback Gemini OCR) → chunking → regex extraction (metadata/obligation/threshold/relations) + keyword classification → ViT5 summary → NLI → status `pending_review` → human review (`/review/*`) → `published` + FAISS index → chatbot RAG / search / khung báo cáo / kiểm định chéo.
- **Danh mục service thực tế** (theo file: `nlp_pipeline`, `pdf_parser`, `ocr_api`, `vector_db`, `crawl_documents`, `notifier`) — thay cho SVC-01..07 giả định.
- **Bảng đối chiếu kế hoạch vs thực tế** (copy bảng ở trên).
- Workflow nghiệp vụ thực tế (WF): ingest, extract, summarize+NLI, review, report template .docx, chatbot RAG, cây văn bản/hiệu lực, kiểm định chéo, topic dashboard, analytics.
- Data model (tóm tắt, trỏ sang Doc 5), NFR/bảo mật (bám `.env`, JWT, OCR consent), rủi ro, nghiệm thu.

### Doc 2 — SRS Yêu cầu chức năng (BAOCAO)
- Actor: **Admin** (cán bộ PĐT/quản trị nội dung), **Lecturer** (giảng viên), **Hệ thống** (APScheduler + background task).
- Use cases thực tế (map tới route/pages):
  1. UC-01 Đăng nhập (`/auth/login`, `/auth/me`)
  2. UC-02 Nạp văn bản (upload + `process_crawled` + crawl/ping/manual crawl; OCR consent tick)
  3. UC-03 Trích xuất & phân loại (`_run_extraction`, regex + keyword)
  4. UC-04 Tóm tắt + NLI (`summarize_text`, `verify_nli`)
  5. UC-05 Rà soát & duyệt (`/review/pending`, `publish`, `reject`, `revalidate`; AuditTrail; `check_and_update_document_status`)
  6. UC-06 Khung báo cáo .docx (`/reports/template/{id}`)
  7. UC-07 Tra cứu (SQL ILIKE `search`) + Chatbot RAG (`/chat`, FAISS top-5 + Gemini)
  8. UC-08 Nghĩa vụ & Sổ tra ngưỡng (`/documents/legal-data`, pages Obligations/Thresholds/Deadlines)
  9. UC-09 Cây văn bản & hiệu lực & sự kiện luật (`/legal-data`, `/documents/impact`, `/documents/detail`, pages DeadDocs/LawEvents/ImpactGraph)
  10. UC-10 Kiểm định chéo (`/auditing/warnings`, `/resolve`)
  11. UC-11 Dashboard chủ đề + Analytics (`/topics`, `/analytics`)
  12. UC-12 Admin quản lý (RejectedDocs, AuditLogs, Admin)
- Ma trận Actor×UC, bảng FR, đặc tả chi tiết từng UC (luồng chính/ngoại lệ/điều kiện từ code), NFR (giới hạn OCR từ `.env`: 20 trang/20MB/4MB, timeout...).

### Doc 3 — Đề cương chi tiết (BAOCAO)
- Giữ cấu trúc đề cương (lý do chọn đề tài, mục tiêu, đối tượng/phạm vi) nhưng cập nhật:
  - Mục "Phương pháp thực hiện" → thay danh sách mô hình cũ bằng mô hình **thực tế** (regex extraction, keyword scoring, ViT5, mDeBERTa NLI, MiniLM-L3 + FAISS, Gemini OCR/RAG).
  - Mục "Kết quả dự kiến" → đổi thành "Kết quả đạt được" (mô tả 17 trang web, 9 bảng, pipeline end-to-end, khung báo cáo .docx, kiểm định chéo...).
  - Thêm mục "Hiện trạng so với đề cương" (bảng đối chiếu rút gọn).

### Doc 4 — Các thuật toán sử dụng (BAOCAO) — VIẾT LẠI HOÀN TOÀN
Chỉ giữ các thuật toán **thực sự có trong code**:
- **Regex/pattern matching** (rule-based): `extract_obligation`, `extract_threshold`, `extract_document_metadata`, `extract_document_relations`, `parse_agency_and_type`, `detect_doc_type` (kèm ví dụ pattern thật từ code).
- **Keyword scoring classification**: `classify_text` (6 topic + threshold>=3, default "Khác").
- **Adaptive chunking**: `chunk_document` (Điều → Chương/Phần → La Mã → Số → Trang).
- **ViT5 (Transformer Seq2Seq)**: tóm tắt trừu tượng, greedy decode (`do_sample=False`).
- **mDeBERTa**: (a) NLI 3 nhãn qua softmax-argmax; (b) QA extractive (start/end span).
- **Embedding + FAISS cosine**: MiniLM-L3 → 384-dim, IndexFlatIP + L2 normalize; threshold 0.2 (chat) / 0.5 (search default).
- **Gemini API (LLM ngoài)**: OCR (temperature 0, vision) + RAG generation (prompt anti-hallucination, luân phiên key, fallback model, timeout/retry).
- **Quản lý bộ nhớ**: chỉ giữ 1 model lớn trong RAM (`_manage_memory`), tránh OOM WinError 1455.
- **Loại bỏ** khỏi tài liệu: TextRank, PhoBERT+CRF, fine-tune, LoRA, ROUGE/BERTScore (vì không có trong code) — hoặc ghi mục "kỹ thuật dự kiến nhưng không triển khai".

### Doc 5 — Thiết kế CSDL
Từ `backend/app/db/models.py` (9 bảng):
`users`, `documents`, `obligations`, `thresholds`, `document_embeddings`, `document_relations`, `audit_trails`, `chat_sessions`, `chat_messages`.
- Với mỗi bảng: cột, kiểu, ràng buộc (FK, unique), enum status (`draft/in_review/published/rejected`, `pending_review`, `published/resolved`...), JSONB dùng cho `embedding`, `citations`, `muc_luc_dieu_khoan`.
- Quan hệ (relationship/cascade delete-orphan Document→Obligation/Threshold).
- Ghi chú quyết định: `DocumentEmbedding.embedding` dùng JSONB (không phải cột pgvector) + FAISS index file; giải thích lý do.
- Sơ đồ ER dạng ASCII + bảng mô tả.

### Doc 6 — Mô tả API endpoints
Catalog 9 router theo nhóm quyền (admin / lecturer / public):
- `auth` (POST /login, GET /me), `documents` (upload, pdf, topics, legal-data, impact, detail, process_crawled, rejected, reprocess, hard_delete), `review` (pending, publish, reject, revalidate), `chat` (sessions, POST /chat), `search`, `analytics`, `audit` (warnings, resolve, logs), `reports` (GET /template/{id}), `system` (status, ping, crawl, crawled_files, stream SSE).
- Mỗi endpoint: method, path, auth, mô tả, input/output chính (từ code). Prefix chung `/api/v1`.

### Doc 7 — Kết quả kiểm thử & đánh giá
- **Chạy thực tế** (task thực thi phải chạy để lấy số liệu): `cd backend && .venv/bin/python -m pytest -q` → ghi số passed/failed.
- Mô tả 12 test: `test_ocr_api.py` (6: success, thiếu config, retry 429, auth không retry, timeout retry, output bị cắt), `test_pdf_parser_limits.py` (6: consent scan, quá trang, quá dung lượng, quá ảnh, giữ định dạng trang, lỗi OCR không nuốt).
- Ghi rõ: **không có** `loadtest/locustfile.py` (README cũ nhắc tới nhưng repo không có) → đánh dấu "chưa có load test".
- **Đánh giá định lượng (ROUGE/BERTScore/Faithfulness)**: không có script tự động trong code → ghi là "định hướng/đề xuất", kèm hướng dẫn thủ công tối thiểu (so NLI label, conf, số văn bản published). KHÔNG bịa số liệu.

### Doc 8 — Hướng dẫn triển khai & vận hành
Tổng hợp từ `deploy/HUONG_DAN_TRIEN_KHAI.md` + `README-local-test.md` + `tailscale-setup.md` thành một tài liệu phụ lục:
- Yêu cầu môi trường, cài Ubuntu/Windows, tạo DB + extension, `.env`, tải mô hình, tạo admin (`create_admin`).
- Chạy backend/frontend, mở website, truy cập xa (WiFi/Tailscale/Cloudflare Tunnel).
- Vận hành (log, nohup), backup, bảng lỗi phổ biến.

## Trình tự thực thi (ordered tasks)

1. Đọc lại các file ground truth ở trên (nếu cần đối chiếu chính xác câu chữ).
2. Tạo Doc 4 (thuật toán) trước — là nền cho Doc 1/3.
3. Tạo Doc 5 (CSDL) và Doc 6 (API) — nền cho Doc 1/2.
4. Tạo Doc 1 (kiến trúc) và Doc 2 (SRS).
5. Tạo Doc 3 (đề cương báo cáo).
6. Chạy `cd backend && .venv/bin/python -m pytest -q`, ghi kết quả, tạo Doc 7.
7. Tạo Doc 8 từ các file deploy.
8. Rà soát đồng bộ: mọi claim trong Doc 1–4 phải có đối chứng trong code; không dùng chi tiết từ README.md gốc (kiến trúc cũ).

## Kiểm chứng (validation)

- [ ] 8 file tồn tại trong `docs/`, tên đúng quy ước; 4 file kế hoạch cũ KHÔNG bị sửa.
- [ ] Không còn cụm từ sai lệch: "PhoBERT+CRF", "TextRank", "fine-tune", "pgvector (cột Vector)", "PaddleOCR", "ReportTemplate (bảng)", "ReviewItem/ReviewLog", "ROUGE/BERTScore (đã chạy)" — trừ khi đặt trong mục "dự kiến/không triển khai".
- [ ] Doc 1–4 dùng đúng tên hàm/tên model từ code (ViT5 `vit5-base-vietnews-summarization`, mDeBERTa, MiniLM-L3-v2, Gemini, FAISS).
- [ ] Doc 7 ghi số liệu pytest thật (đã chạy), không bịa; ghi rõ loadtest/đánh giá định lượng chưa có.
- [ ] Doc 6 liệt kê đúng endpoint/method (đối chiếu 9 router file).

## Rủi ro & lưu ý

- Không sửa code; chỉ tạo/sửa file `.md` → không cần GitNexus impact.
- Doc 7 phụ thuộc việc chạy pytest (có thể chậm nếu model nặng; test ở đây chỉ mock, không tải model nặng nên nhanh).
- Docker: kế hoạch cũ hứa "đóng gói Docker" nhưng repo không có Dockerfile/compose → ghi trong Doc 1 là "chưa đóng gói, chạy trực tiếp" (đúng sự thật).