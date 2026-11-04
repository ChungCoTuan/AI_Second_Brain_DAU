# Kế hoạch: Sửa quy tắc duyệt lại NLI trên trang Cần rà soát (ReviewQueue)

## Bối cảnh & lỗi đã xác minh

Trang `/review` (ReviewQueue.tsx) có chế độ Human-in-the-loop: admin bấm "Sửa" → chỉnh textarea tóm tắt → bấm "Kiểm tra lại NLI" → nhãn mới chỉ hiện ở badge nhỏ góc phải. Hai lỗi đã xác minh bằng code:

1. **Không có phản hồi khi chạy NLI lại**: `handleRevalidate` (ReviewQueue.tsx:112-126) chỉ `setTempLabel()`, không toast; nếu API lỗi thì `catch` chỉ `console.error` → người dùng không thấy gì.
2. **Vi phạm quy tắc nghiệp vụ**: nút "Sửa & Duyệt" (dòng 252-259) gọi `handlePublish(..., editedText)` và publish ngay, bất kể đã chạy NLI chưa và nhãn NLI là gì (kể cả contradiction vẫn duyệt được).
3. **Backend mất dữ liệu chỉnh sửa**: `publish_item` (backend/app/api/routers/review.py:88) nhận body `{edited_summary}` nhưng bỏ qua — không lưu vào `item.tom_tat`, không cập nhật `item.nli_label`, AuditTrail ghi cứng `edited_summary=None`, `action="Duyệt giữ nguyên"` dù đang sửa.

## Quyết định đã chốt với user

1. **Quy tắc duyệt: chặn theo nhãn NLI** — entailment → được duyệt; contradiction → chặn, bắt buộc sửa tiếp; neutral → được duyệt kèm cảnh báo vàng.
2. **Sửa cả FE + BE** — lưu nội dung đã chỉnh + nhãn NLI mới vào DB, ghi đúng AuditTrail.

## Phát hiện hỗ trợ

- DB đã có sẵn cột: `Obligation.tom_tat`, `Obligation.nli_label`, `Threshold.tom_tat`, `Threshold.nli_label`, `AuditTrail.edited_summary` (models.py:60-61,78-79,114) → **không cần migration**.
- Frontend đã giữ `tempLabel` sau revalidate; cần thêm state theo dõi "đã revalidate chưa" và "đã sửa text sau lần revalidate đó chưa".

---

## Task 1 — Backend: `backend/app/api/routers/review.py`

Sửa `publish_item`:
1. Thêm model body: `class PublishRequest(BaseModel): edited_summary: str | None = None; nli_label: str | None = None`.
2. Nếu có `edited_summary` (khác rỗng và khác `item.tom_tat` gốc):
   - **Server-side verify lần nữa**: gọi `extractor.verify_nli(item.nguon, edited_summary)` → dùng kết quả này (không tin nhãn từ FE) làm điều kiện.
   - Nếu kết quả = `contradiction` → trả về `HTTPException(422, detail="NLI: contradiction — bản chỉnh sửa mâu thuẫn với nguyên văn, không thể duyệt.")` và KHÔNG publish.
   - Nếu hợp lệ: `item.tom_tat = edited_summary`, `item.nli_label = <nhãn server xác nhận>`.
3. Sửa AuditTrail: `edited_summary = edited_summary or None`, `action = "Sửa & Duyệt"` khi có chỉnh sửa, giữ `"Duyệt giữ nguyên"` khi không; `author = current_user.email` thay vì cứng "Admin" (làm tương tự cho reject).
4. Trả về response kèm `nli_label` đã ghi để FE hiển thị xác nhận.

> Giữ nguyên `check_and_update_document_status` và mọi logic khác. Không đụng endpoint khác.

## Task 2 — Frontend: `frontend/src/pages/ReviewQueue.tsx`

Sửa `handleRevalidate`:
- Khi thành công: `setTempLabel(label)` + `setRevalidatedAt(text tại lúc chạy)` (state mới) + toast thông báo kết quả: entailment "✅ NLI: An toàn — có thể duyệt", neutral "🟠 NLI: Chung chung", contradiction "🔴 NLI: Mâu thuẫn — cần chỉnh sửa lại".
- Khi lỗi: `showToast("❌ Không thể chạy NLI, thử lại sau")` (toast lỗi màu đỏ — thêm state `toastTone`).
- Toast dùng lại hệ thống `toastMessage` hiện có, thêm biến `toastTone: 'ok' | 'err'` đổi màu nền.

Sửa khối edit + nút "Sửa & Duyệt":
- State mới: `revalidatedText: string | null` — text mà nhãn `tempLabel` đang đại diện.
- Nút "Sửa & Duyệt" **disabled** khi: `tempLabel === null` (chưa chạy NLI) **hoặc** `editedText !== revalidatedText` (đã sửa thêm sau lần chạy NLI) — kèm dòng hướng dẫn nhỏ "Chạy 'Kiểm tra lại NLI' trước khi duyệt".
- Logic hiển thị theo nhãn (`tempLabel` đang hiển thị):
  - `entailment` → nút mở, nền xanh (giữ).
  - `neutral` → nút mở, nền amber, kèm badge cảnh báo nhỏ "🟠 Neutral — hãy rà kỹ".
  - `contradiction` → nút **disabled** + khối cảnh báo đỏ "Bản chỉnh sửa mâu thuẫn với nguyên văn. Hãy sửa lại nội dung rồi chạy NLI lại."
- Badge nhãn NLI khi đang edit: hiển thị to/rõ hơn trong khối "Chế độ Sửa" (không chỉ badge nhỏ góc phải) — thêm dòng trạng thái ngay dưới textarea: "Kết quả NLI: <badge>".
- `handlePublish` truyền thêm `nli_label: tempLabel` trong body; sau publish hiện toast + reset các state edit.

## Task 3 — Kiểm chứng

1. Backend: chạy lại uvicorn, thử `PUT /review/{type}/{id}/publish` với body chứa edited_summary → kiểm tra DB: `tom_tat` cập nhật, `nli_label` ghi nhãn server, AuditTrail có `edited_summary` + action "Sửa & Duyệt", author = email admin.
2. Backend: thử publish nội dung mâu thuẫn → nhận 422, item vẫn `pending_review`.
3. Frontend: `cd frontend && npm run lint && npm run build` sạch lỗi (chỉ warning cũ).
4. Thủ công trên `http://192.168.1.20:5173/review`:
   - Sửa → chạy NLI: thấy toast kết quả + badge trong khối sửa.
   - Chưa chạy NLI bấm Sửa & Duyệt → nút disabled, có hướng dẫn.
   - Sửa tiếp sau khi chạy NLI → nút disabled lại (nhãn đã cũ).
   - Contradiction → chặn + cảnh báo đỏ; neutral → cảnh báo vàng nhưng duyệt được.
   - Duyệt xong: item biến mất khỏi hàng đợi; xem lại trong Nhật ký thao tác (audit) có bản chỉnh sửa đúng.

## Rủi ro

- `extractor.verify_nli` chạy đồng bộ trong request publish → có thể chậm vài giây; chấp nhận (đã có nền tảng dùng ở /revalidate). Không thêm job async trong phạm vi này.
- Nhãn server-side có thể lệch với nhãn FE vừa hiển thị (mô hình không xác định) → FE luôn hiển thị nhãn trả về trong response publish nếu có khác biệt.
