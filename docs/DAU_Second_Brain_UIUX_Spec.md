# Giao diện và điều hướng hiện tại

**Cập nhật:** 10/11/2026
Đây là bản kiểm kê UI trong code, không phải mockup hay cam kết hành vi chưa được triển khai.

## 1. Điều hướng

Frontend dùng React Router; sau đăng nhập, `/` điều hướng tới `/priority`.

| Route | Trang | Quyền theo route frontend |
|---|---|---|
| `/login` | Đăng nhập | Công khai |
| `/priority` | Ưu tiên xử lý | Admin |
| `/dead-docs` | Văn bản khai tử | Admin |
| `/deadlines` | Hạn chót & mốc | Admin |
| `/analytics` | Phân tích | Admin và lecturer |
| `/events` | Sự kiện luật | Admin |
| `/review` | Hàng đợi rà soát | Admin |
| `/topics` | Chủ đề văn bản | Admin |
| `/admin` | Tải tài liệu/quản trị | Admin |
| `/audit` | Nhật ký thao tác | Admin |
| `/rejected` | Văn bản loại bỏ | Admin |
| `/search` | Tra cứu thủ công | Admin và lecturer |
| `/chat` | Tra cứu AI | Admin và lecturer |
| `/obligations` | Việc phải làm | Admin và lecturer |
| `/thresholds` | Sổ ngưỡng & định mức | Admin và lecturer |
| `/graph` | Đồ thị ảnh hưởng | Admin và lecturer |

Các route frontend không thay thế kiểm tra quyền backend. Một số API có dependency xác thực riêng; kiểm tra router tương ứng trước khi công bố API.

## 2. Tính năng giao diện đã kết nối

- Sidebar hiển thị nhóm cảnh báo/rà soát, tra cứu/dữ liệu và hệ thống; một số badge/unread state lưu trong `localStorage`.
- Trang đăng nhập, tìm kiếm SQL có phân trang, chat với lịch sử phiên, admin upload/crawl, review obligation/threshold và audit logs.
- Tìm kiếm PDF/chi tiết văn bản mở qua API backend; dữ liệu tổng hợp được chia sẻ qua `DataContext`.
- Cập nhật tiến trình xử lý có thể nhận qua Server-Sent Events.
- `DocumentDetailDrawer` là component chia sẻ cho chi tiết tài liệu.

## 3. Các điểm cần hiểu đúng

- Search UI không phải tìm kiếm ngữ nghĩa; endpoint lọc tên file, topic và tags trong PostgreSQL.
- Chat có citations từ các đoạn FAISS được truy xuất; không có UI đối chiếu từng câu với NLI.
- Review UI thao tác trên nghĩa vụ/ngưỡng, không review từng câu trong toàn văn tóm tắt.
- Topic page hiển thị nhãn được phân loại heuristic; không phải dashboard có độ chính xác đã đo.
- Report DOCX là template code theo nhóm tên file, không có màn hình quản trị template library.
- UI/route có thể hiện diện nhưng dữ liệu hiển thị phụ thuộc API, DB và file runtime; không có fixture bảo đảm số liệu cố định.

## 4. Mã nguồn giao diện

- Điều hướng/role gate: [`frontend/src/App.tsx`](../frontend/src/App.tsx)
- Sidebar: [`frontend/src/components/layout/Sidebar.tsx`](../frontend/src/components/layout/Sidebar.tsx)
- API client: [`frontend/src/api/axiosClient.ts`](../frontend/src/api/axiosClient.ts)
- Trang: [`frontend/src/pages/`](../frontend/src/pages/)
- Chi tiết drawer: [`frontend/src/components/shared/DocumentDetailDrawer.tsx`](../frontend/src/components/shared/DocumentDetailDrawer.tsx)

Đề xuất nâng cấp trạng thái loading/error/empty và accessibility cần được ghi nhận như backlog cho đến khi có implementation/test.
