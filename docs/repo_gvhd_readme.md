# Tóm tắt repository gửi GVHD

**Cập nhật:** 10/11/2026

## Sản phẩm trong repository

Ứng dụng web DAU Second Brain gồm:

- `frontend/`: giao diện React/TypeScript dùng Vite.
- `backend/`: REST API FastAPI, PostgreSQL/SQLAlchemy, xử lý PDF/NLP, crawler và FAISS.
- `docs/`: tài liệu mô tả code hiện tại, phạm vi chưa hoàn thành và kế hoạch đánh giá.

Đây không phải gói demo tĩnh chỉ gồm `index.html`, `data.js` và `data.enc`. Hướng dẫn cũ về deploy một site tĩnh/Vercel và bộ số liệu “18 văn bản/417 điều...” không còn được xác minh bởi code của repository nên đã được bỏ khỏi hướng dẫn hiện trạng.

## Các chức năng có trong code

Đăng nhập theo role; upload và xử lý PDF; crawler Chính phủ; trích metadata/chủ đề/nghĩa vụ/ngưỡng; review và audit; tra cứu SQL; chat RAG có citation; báo cáo DOCX; đồ thị quan hệ và cảnh báo auditing.

Các chức năng trên có mức độ hoàn thiện khác nhau. Xem ma trận trong [`DAU_Second_Brain_Dac_Ta_Yeu_Cau_Chuc_Nang.md`](DAU_Second_Brain_Dac_Ta_Yeu_Cau_Chuc_Nang.md). Không có tuyên bố rằng hệ thống đạt độ chính xác pháp lý hoặc các ngưỡng KPI chưa đo.

## Chạy thử

Làm theo [`usage.md`](usage.md). Không dùng mật khẩu mặc định: tạo tài khoản admin qua `python -m app.scripts.create_admin`. Không commit `.env` hoặc API keys. Với PDF scan, OCR gửi ảnh tới Gemini nên cần cân nhắc quyền dữ liệu và xác nhận trong UI.

## Tài liệu khác

- [`DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md`](DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md): kiến trúc và giới hạn.
- [`workflow.md`](workflow.md): luồng chạy thực tế.
- [`CÁC THUẬT TOÁN SỬ DỤNG.md`](CÁC%20THUẬT%20TOÁN%20SỬ%20DỤNG.md): thuật toán/model IDs.
- [`DAU_Second_Brain_Ke_Hoach_Danh_Gia.md`](DAU_Second_Brain_Ke_Hoach_Danh_Gia.md): test hiện có và kế hoạch benchmark.
