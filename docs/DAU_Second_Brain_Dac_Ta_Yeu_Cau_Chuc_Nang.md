# Đặc tả chức năng và trạng thái triển khai

**Cập nhật:** 10/11/2026
Tài liệu này tách rõ chức năng đang có trong code và mục tiêu chưa hoàn thành. “Có endpoint” không đồng nghĩa đã đạt chất lượng pháp lý hay tiêu chí benchmark.

## 1. Vai trò

- **Admin:** upload/xử lý tài liệu, quản trị review, crawl và xem một số báo cáo/audit.
- **Lecturer:** đăng nhập, tra cứu, chat, xem nghĩa vụ/ngưỡng/đồ thị.
- **Hệ thống:** xử lý PDF, NLP, crawler theo lịch và SSE.

## 2. Ma trận yêu cầu

| ID | Yêu cầu | Hiện trạng trong code |
|---|---|---|
| FR-01 | Upload PDF và ingest file crawler | **Có một phần:** admin upload PDF; crawler Chính phủ và endpoint xử lý file đã crawl. Không hỗ trợ upload ảnh/JPG/PNG. |
| FR-02 | Chia cấu trúc để dẫn nguồn | **Có một phần:** adaptive chunking nội bộ; không lưu chunk thành entity riêng, không đảm bảo citation mapping điều/khoản ổn định. |
| FR-03 | Phân loại loại văn bản và chủ đề | **Có một phần:** topic keyword scoring; không có classifier huấn luyện. Loại văn bản không được lưu thành trường riêng. |
| FR-04 | Metadata văn bản | **Có một phần:** regex cho cơ quan, ngày ký, người ký, ngày hiệu lực và tags; phụ thuộc định dạng đầu vào. |
| FR-04b | Bóc nghĩa vụ và con số | **Có một phần:** rule-based lấy một đoạn ứng viên và tạo tối đa một record mỗi loại trong một lần ingest. |
| FR-05 | Báo cáo, trách nhiệm, hạn nộp | **Có một phần:** regex trả về nghĩa vụ/hạn chót; chưa có đánh giá độ chính xác hoặc workflow riêng cho báo cáo. |
| FR-06 | Tóm tắt từng câu gắn citation | **Chưa có đầy đủ:** có summary văn bản/đoạn; không có ánh xạ từng câu tóm tắt sang chunk ID. |
| FR-07 | NLI từng câu tóm tắt | **Có một phần:** NLI 3 nhãn cho summary của obligation/threshold và khi sửa; không kiểm tra mọi câu trong summary/chat. |
| FR-08 | Chặn toàn văn khi có contradiction | **Chưa đáp ứng theo đặc tả:** review/publish là theo từng mục extraction; không có gate đồng bộ cho tất cả câu của văn bản. |
| FR-09/09b/09c | Review, sửa, reject, audit | **Có một phần:** queue pending theo obligation/threshold, revalidate khi sửa, audit trail. Không phải queue từng câu tóm tắt. |
| FR-10/11 | Template báo cáo theo loại, không sinh nội dung | **Có một phần:** endpoint tạo DOCX theo nhóm nhận diện tên file; chưa có template library hoặc template theo chủ đề. |
| FR-12/13 | RAG có citations, từ chối khi thiếu bằng chứng | **Có một phần:** FAISS top-k + Gemini + citations. Không có ngưỡng từ chối rõ ràng bảo đảm và không lọc theo published status. |
| FR-14 | Đối chiếu từng câu summary | **Chưa có đầy đủ:** không có citation map từng câu. |
| FR-15 | Ghi log mọi câu hỏi và faithfulness score | **Có một phần:** lưu lịch sử chat/citations; không có faithfulness score và query log riêng. |
| FR-16 | Văn bản liên quan | **Có một phần:** regex lưu quan hệ tường minh và API impact; không có semantic relation đầy đủ. |
| FR-16b | Theo dõi sự kiện hiệu lực | **Có một phần:** derive một số sự kiện từ relation/document metadata; không có bộ quản lý hiệu lực pháp lý toàn diện. |
| FR-17 | Dashboard chủ đề | **Có một phần:** endpoint/topics và route `/topics`; phân loại topic là heuristic. |
| FR-18 | Cảnh báo quy chế viện dẫn căn cứ hết hiệu lực | **Có một phần:** endpoint auditing đối chiếu các relation `căn cứ` với relation thay thế/bãi bỏ hoặc document status. Kết quả phụ thuộc dữ liệu đã nạp. |

## 3. API chính

`/api/v1` là prefix mặc định. Danh sách đầy đủ và schema request/response có thể xem tại `/docs` khi backend chạy.

| Nhóm | Endpoint tiêu biểu |
|---|---|
| Auth | `POST /auth/login`, `GET /auth/me` |
| Ingestion/admin | `POST /documents/upload`, `POST /documents/process_crawled`, `POST /system/crawl`, `GET /system/crawled_files` |
| Dữ liệu | `GET /search`, `GET /legal-data`, `GET /topics`, `GET /documents/detail/{so_hieu}` |
| Review | `GET /review/pending`, `POST /review/revalidate`, `PUT /review/{item_type}/{item_id}/publish`, `/reject` |
| Chat | `POST /chat`, `GET /chat/sessions`, `GET /chat/sessions/{session_id}` |
| Audit/graph | `GET /auditing/warnings`, `GET /audit/logs`, `GET /impact` |
| Report | `GET /reports/template/{document_id}` |

## 4. Tiêu chí nghiệm thu

Không ghi các ngưỡng F1, accuracy, detection rate hay latency như kết quả đã đạt khi chưa có bộ test và báo cáo đo lường. Các chỉ số trong kế hoạch nghiên cứu phải được tính trên dataset gán nhãn riêng; xem [`DAU_Second_Brain_Ke_Hoach_Danh_Gia.md`](DAU_Second_Brain_Ke_Hoach_Danh_Gia.md).
