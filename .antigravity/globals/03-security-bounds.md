# Ràng Buộc An Toàn (Security Bounds)

Đây là các quy tắc MỨC ĐỘ ƯU TIÊN CAO NHẤT mà mọi module AI phải tuân thủ trong dự án này:

## 1. Zero Hallucination (Không bịa đặt thông tin)
- Vì đây là dự án xử lý văn bản quy phạm pháp luật (Pháp chế giáo dục), hệ thống KHÔNG ĐƯỢC PHÉP tự sáng tạo, suy diễn hay tổng hợp sai lệch các con số, hạn chót, hay nghĩa vụ.
- Bất kỳ kết quả trích xuất nào (Tóm tắt, Con số chốt, Nghĩa vụ, Hỏi đáp) đều phải đi kèm `nguon` (trích dẫn nguyên văn đoạn chứa thông tin).

## 2. Document Publish Gate (Cơ chế Duyệt)
- Mọi văn bản sau khi AI xử lý (Tóm tắt, NLI) KHÔNG được hiển thị ngay cho người dùng cuối.
- Trạng thái mặc định luôn là `pending_review`.
- Chỉ cán bộ có thẩm quyền mới được duyệt chuyển sang `published`.
- Chatbot RAG và Tính năng Search CHỈ ĐƯỢC PHÉP truy xuất các văn bản ở trạng thái `published`.

## 3. NLI 3 Nhãn (Entailment / Contradiction / Neutral)
- Các câu tóm tắt sinh ra phải chạy qua mô hình NLI.
- Bất kỳ văn bản nào có chứa ít nhất 1 câu bị gán nhãn `contradiction` đều bị gắn cờ "ĐỎ" và buộc phải giữ nguyên trạng thái `pending_review` cho đến khi cán bộ con người can thiệp.

## 4. Cross-Auditing (Rà soát chéo)
- Các văn bản nội bộ (Quy chế trường) không được phép ghi đè luật của Bộ.
- Nếu phát hiện Quy chế trường đang tham chiếu đến một văn bản Bộ đã hết hiệu lực, hệ thống phải phát Cảnh báo (Warning) lập tức.
