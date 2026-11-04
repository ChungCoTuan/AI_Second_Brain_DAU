# Kế hoạch: Xây lại toàn bộ giao diện DAU Second Brain theo bộ nhận diện "Hành chính – Pháp lý"

## Mục tiêu
Lột xác UI: chuyên nghiệp, đúng nghiệp vụ quản lý văn bản pháp quy của Trường. Giữ maroon #990000 làm màu thương hiệu (header/sidebar), nội dung chuyển nền xám nhạt + card trắng + màu trạng thái ngữ nghĩa (đỏ=nguy cơ/quá hạn, cam=cảnh báo, lục=đã duyệt/hoàn tất, lam=thông tin). Kiểu chữ phân cấp rõ, spacing/badge/bảng đồng bộ.

## Chiến lược: Proof-first
Giai đoạn A: design system + Login + Layout (Sidebar/Header) + 1 trang đại diện (PriorityList) → user duyệt trực quan. Giai đoạn B: áp dụng cho 16 trang còn lại + drawer + modal.

## Ràng buộc
- Frontend thuần: React 19 + Vite + CSS classes (KHÔNG thêm Tailwind/CSS-in-JS/lib mới). Giữ lucide-react.
- Giữ nguyên 100% logic: routes, contexts (Auth/Data/Detail), API calls, SSE, localStorage read-state, phân trang, bộ lọc.
- Không sửa backend.
- Dev server đang chạy `VITE_API_URL=/api/v1 npm run dev -- --host 0.0.0.0 --port 5173`.
- Validate: `npm run lint` (oxlint) + `npm run build` (tsc -b && vite build) + soi bằng trình duyệt tại 172.16.48.51:5173.

## Phát hiện quan trọng (rủi ro phải xử lý)
- `--blue` thực chất là maroon #990000 (tên misleading). Chat.tsx dùng var không tồn tại: `--card-bg`, `--border`, `--text`, `--green-bg` → phải định nghĩa token tương thích hoặc đổi hết.
- Sidebar/Header/Login/ConfirmModal/Drawer = hàng trăm dòng inline style → refactor sang class.
- Class cũ (`navtabs`, `navtabs-a`, `gate`, `gcard`...) trùng tên nhưng khác ý → đổi mới toàn bộ, giữ class dùng chung (`inp`, `wrap`, `sub`, `rlist`, `prow`, `tl`, `tile`, `lv`, `badge`, `chip`, `ev-q`...) với style mới.

## Design tokens (index.css :root)
```
Brand:   --brand:#990000  --brand-d:#7a0000  --brand-50:#fdf3f3  --brand-100:#f7d9d9
Neutral: --bg:#f1f5f9  --surface:#fff  --line:#e2e8f0  --line-strong:#cbd5e1
Ink:     --ink:#0f172a  --ink-2:#334155  --muted:#64748b
Status:  --danger:#b91c1c/--danger-bg:#fef2f2/--danger-line:#fecaca
         --warn:#b45309/--warn-bg:#fffbeb/--warn-line:#fde68a
         --ok:#15803d/--ok-bg:#f0fdf4/--ok-line:#bbf7d0
         --info:#0369a1/--info-bg:#f0f9ff/--info-line:#bae6fd
Alias tương thích (khử dần): --blue:var(--brand) --border:var(--line) --text:var(--ink-2)
   --card-bg:var(--surface) --green-bg:var(--ok-bg) --soft:#f8fafc
Shape:   --r-sm:8px --r-md:10px --r-lg:14px  |  shadow-sm/md/lg thống nhất
Font:    giữ Be Vietnam Pro/system-ui; scale: h1 26/800, h2 21/800, body 14.5, sub 13.5, caption 12
```

## Giai đoạn A (proof)
1. **`src/index.css`**: viết lại toàn bộ — tokens trên, base (reset, typography, scroll), layout (app-shell), rồi các lớp component: `card`, `page-head` (h2+sub), `panel-filters` (thay filter-card inline), `field`, `inp`, `sel`, `btn` (btn-primary/ghost/danger/sm), `badge` (danger/warn/ok/info/neutral), `tile` (stat), `table-list` + `row-*`, `pager`, `empty-state`, `chip`, `drawer`, `modal`, `timeline`, `auth-*` (login). Responsive giữ breakpoint 768/680px.
2. **`src/components/ui.tsx`** (mới, nhỏ): `PageHead`, `Badge`, `StatTile`, `Pager`, `EmptyState`, `Card`, `FilterPanel` — mỗi cái chỉ là wrapper className, không state.
3. **`Login.tsx`**: giữ cấu trúc 2 cột + brand; chuyển inline sang `auth-*`; hero nền maroon gradient + pattern; form card trắng, focus ring brand; thêm dòng vai trò/điểm nhấn nghiệp vụ.
4. **`Header.tsx`**: nền maroon, chiều cao 60px; brand trái; bell dropdown + avatar phải → chuyển sang class `hdr-*`, dropdown dùng `card` + `badge`; giữ logic notification/điều hướng y nguyên.
5. **`Sidebar.tsx`**: nền trắng trên nền app xám, header logo + "Second Brain"; nav item `snav` (active: nền brand-50 + viền trái 3px brand); section label nhỏ uppercase; user block + nút đăng xuất `btn-ghost-danger`. Giữ badge counts + ConfirmModal.
6. **`Layout.tsx`**: app-container nền `--bg`.
7. **`PriorityList.tsx`**: refactor inline → `panel-filters`, `field`, `btn`, `table-list`, `pager`, `empty-state`, `Badge`; giữ nguyên filter/pagination/resolve logic.
8. Chạy lint + build, chạy dev server, kiểm tra các trạng thái: rỗng, lọc, badge MỚI (unread), mobile 768px. → Chụp/để user duyệt.

## Giai đoạn B (mở rộng)
9. Refactor theo thứ tự: Search, Chat (sửa các var sai thành token mới), ReviewQueue, DeadDocs, Deadlines, LawEvents, Obligations, Thresholds, ImpactGraph, Topics, Analytics, Admin, AuditLogs, RejectedDocs.
10. `DocumentDetailDrawer.tsx`: drawer header maroon→`dr-h` class mới (thanh trắng, tiêu đề ink, viền đáy; giữ khối alert OCR màu danger); modal preview báo cáo → `modal` + `btn`; badge replace/repeal giữ lớp.
11. `ConfirmModal.tsx`: sang class `modal*` + `btn`; giữ animation keyframes chuyển vào index.css.
12. `utils.tsx`: `hl()` dùng class `mark-hl` thay style inline; giữ conLaiNode (`dleft` đã có class).
13. Dọn alias token còn sót; lint + build + test thủ công từng trang (login → cả 16 route, role admin + lecturer, mobile).

## Nguy cơ & cách tránh
- Class CSS cũ còn tham chiếu tại trang chưa refactor → giữ nguyên định nghĩa class cũ trong index.css giai đoạn A, xóa dần ở cuối giai đoạn B (tìm `grep -rn "navtabs\|prow\|rlist"` còn dùng trước khi xóa).
- Tên var `--blue` dùng rải rác → giữ alias, chỉ đổi nghĩa token gốc.
- Kiểm tra `npm run build` bắt lỗi TS sau mỗi trang.

## Ngoài phạm vi
- Backend, API, dữ liệu, auth logic, SSE, crawler, Archify HTML.

## Kiểm chứng
- `cd frontend && npm run lint && npm run build` sạch lỗi.
- Trình duyệt 172.16.48.51:5173: login (staff@dau.edu.vn / Staff_Dau@2026), duyệt từng trang, drawer chi tiết, modal xác nhận, thông báo bell, mobile resize, cả role lecturer (chỉ thấy nhóm Tra cứu & Dữ liệu).
