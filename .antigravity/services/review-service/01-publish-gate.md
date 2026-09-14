# Cơ chế Publish Gate (Cổng Duyệt)

Review Service (Hàng đợi rà soát) là chốt chặn cuối cùng trước khi bất kỳ dữ liệu nào được đưa vào sử dụng trong hệ thống. (Human-in-the-loop).

## 1. Trạng thái (Status)
Văn bản có 2 trạng thái chính:
- `pending_review`: Đang chờ con người duyệt (chỉ admin/cán bộ xem được).
- `published`: Đã duyệt xong, công khai cho Chatbot RAG và Search.

## 2. Trigger (Khi nào bị chặn?)
Văn bản tự động rơi vào `pending_review` nếu:
- Thuật toán NLI phát hiện ít nhất 1 câu tóm tắt bị gán nhãn `contradiction`.
- Có sự thay đổi lớn trong bóc tách Sự kiện hiệu lực (VD: phát hiện Luật mới thay thế nhưng cấu trúc phức tạp).

## 3. UI/UX cho màn hình ReviewQueue
- Phải hiển thị song song: Câu tóm tắt/trích xuất (bên trái) vs Câu nguyên bản gốc (bên phải).
- Làm nổi bật (highlight) chính xác từ ngữ gây mâu thuẫn để cán bộ dễ nhìn thấy.
- Nút Action: "Duyệt", "Sửa", "Xóa bỏ".
