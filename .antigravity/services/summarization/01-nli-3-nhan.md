# Quy tắc 3 Nhãn NLI (Natural Language Inference)

Mô đun NLI được sử dụng để kiểm tra độ tin cậy của các câu tóm tắt (hypothesis) so với nguyên bản (premise).

## Các Nhãn Bắt Buộc:
1. **Entailment (Suy ra đúng)**
   - Câu tóm tắt hoàn toàn được hỗ trợ bởi đoạn nguồn.
   - Không thêm thắt bất kỳ ý nào ngoài nguồn.
   - **Action**: Câu này được coi là an toàn.

2. **Contradiction (Mâu thuẫn / Sai lệch)**
   - Câu tóm tắt có chứa thông tin không có trong nguồn, tự bịa ra con số, hoặc làm sai lệch ý nghĩa (ví dụ: Nguồn nói "tháng 5", tóm tắt nói "tháng 6").
   - **Action**: Đánh dấu màu ĐỎ, đưa toàn bộ văn bản vào trạng thái `pending_review` (chặn xuất bản).

3. **Neutral (Không đủ căn cứ)**
   - Câu tóm tắt không sai, nhưng chứa thông tin quá chung chung hoặc thiếu bối cảnh để khẳng định đúng/sai 100%.
   - **Action**: Cảnh báo nhẹ (màu CAM), yêu cầu cán bộ xem lại nhưng không chặn cứng (tùy cài đặt).

## Ràng buộc Triển khai
- Không bao giờ được phép tin tưởng hoàn toàn 100% vào LLM tóm tắt mà không qua màng lọc NLI.
- Nếu NLI chạy lỗi, văn bản tự động đưa về trạng thái `pending_review`.
