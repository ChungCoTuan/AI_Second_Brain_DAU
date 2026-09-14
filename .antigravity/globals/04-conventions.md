# Quy Ước Phát Triển (Conventions)

## 1. Công nghệ Frontend
- **Framework**: React 18 + Vite.
- **Ngôn ngữ**: TypeScript (`.tsx`, `.ts`). Không dùng `.jsx` hoặc `.js` thường.
- **Styling**: Sử dụng Vanilla CSS (trong `index.css`) được port từ template của GVHD. Ưu tiên dùng các class CSS có sẵn (như `.card`, `.badge`, `.dr-h`, v.v.) thay vì tự viết CSS inline hay dùng Tailwind (trừ khi có yêu cầu đặc biệt).
- **Icons**: Sử dụng thư viện `lucide-react`.

## 2. Quản lý trạng thái (State Management)
- Tận dụng tối đa `useState`, `useMemo` của React để thay thế cho thao tác DOM trực tiếp (tránh dùng `document.getElementById` hoặc `innerHTML` như bản HTML tĩnh).

## 3. Cấu trúc thư mục Frontend
- `src/pages/`: Chứa các component tương đương với một màn hình (route) riêng biệt (VD: `PriorityList.tsx`, `Analytics.tsx`).
- `src/components/shared/`: Các UI Component dùng chung (VD: `DocumentDetailDrawer.tsx`).
- `src/components/layout/`: Cấu trúc khung giao diện (Sidebar, Header, Layout).
- `src/context/`: Các context provider (VD: `DetailContext.tsx`).

## 4. Format dữ liệu Mock
- Toàn bộ dữ liệu tạm (demo data) đang nằm trong `src/data.ts`.
- Mọi thay đổi về cấu trúc JSON phải đồng bộ giữa `02-data-models.md` và `data.ts`.
- Không tự ý sinh fake data mà không có sự đồng ý. Toàn bộ dữ liệu hiển thị phải khớp với `data.ts` hoặc kết quả API thực tế.
