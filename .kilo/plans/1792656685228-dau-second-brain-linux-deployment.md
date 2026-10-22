# Kế hoạch: Chạy thử giao diện AI Town (không cần AI chạy thật)

## Mục tiêu

- Clone và chạy AI Town ở mức tối thiểu để xem giao diện (bản đồ 2D + nhân vật pixel).
- Không cài Docker, không tải model local, không cấu hình LLM (nhân vật không trò chuyện).
- Không làm ảnh hưởng ứng dụng ĐAU Second Brain đang chạy (RAM máy đang chật, ~6,6 GB available).

## Quyết định đã chốt

- Backend Convex: dùng **Convex Cloud** (tài khoản miễn phí), không self-host bằng Docker.
- Không đặt key LLM; kết quả mong đợi là giao diện hiển thị, nhân vật đứng im không nói.
- Repo AI Town: `https://github.com/a16z-infra/ai-town.git`, nhánh `main`.
- Clone vào thư mục riêng **ngoài** repo ĐAU, ví dụ `~/ai-town`.

## Tiền đề và rủi ro

- **Xung đột cổng 5173:** AI Town frontend mặc định dùng cổng **5173**, đang bị chiếm bởi frontend Vite của ĐAU. Phải tạm dừng frontend ĐAU hoặc chạy AI Town trên cổng khác (Vite hỗ trợ `--port`/`--strictPort=false`; xem `vite.config.ts` của AI Town).
- **Phiên bản Node:** máy chỉ có Node 24 (cục bộ `~/.local/opt/node-v24.22.1-linux-x64`), không có `nvm` và không có node hệ thống. AI Town khuyên Node 18; Convex CLI có thể lỗi với Node 24. Phương án dự phòng: cài Node 18 bằng `nvm` vào `~/.nvm` (không cần sudo).
- **Đăng nhập Convex:** cần mở trình duyệt đăng nhập GitHub/Google — là bước thủ công của người dùng, không tự động hoá được.
- **Không cần sudo** cho các bước chạy app (chỉ nếu phải cài nvm thì nvm tự cài vào home, không root).

## Các bước thực hiện

### 1. Chuẩn bị Node

- Đảm bảo `node` trong PATH (local Node 24): `export PATH="$HOME/.local/opt/node-v24.22.1-linux-x64/bin:$PATH"`.
- Thử với Node 24 trước. Nếu `npx convex` báo lỗi phiên bản Node, cài nvm rồi dùng Node 18:
  `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.2/install.sh | bash`
  `nvm install 18` rồi `nvm use 18`.

### 2. Tạo thư mục trống và clone

- `mkdir -p ~/ai-town`
- `git clone https://github.com/a16z-infra/ai-town.git ~/ai-town`
- `cd ~/ai-town`

### 3. Cài dependencies

- `npm install`

### 4. Chạy

- `npm run dev`
- Lần đầu lệnh sẽ mở trình duyệt yêu cầu đăng nhập Convex và tạo/attach một deployment (project) mới. Chọn tài khoản, đặt tên tuỳ ý, chấp nhận cấu hình mặc định.
- Sau khi backend sync xong, mở `http://localhost:5173` (hoặc cổng đã đổi).

### 5. Xác nhận kết quả

- Trình duyệt hiển thị thế giới 2D với các nhân vật pixel.
- Nhân vật không nói chuyện (chưa cấu hình LLM) — đây là kết quả mong đợi của mục tiêu "chỉ xem giao diện".
- Kiểm tra cổng 5173 của ĐAU: nếu cần, tạm dừng frontend ĐAU trước khi chạy AI Town để tránh xung đột.

### 6. Dừng

- `Ctrl+C` ở terminal chạy `npm run dev`.

## Validation plan

- `http://localhost:5173` (AI Town) hiển thị bản đồ + nhân vật; không có lỗi màn hình trống do thiếu backend.
- Ứng dụng ĐAU vẫn dùng được sau khi test (đặc biệt nếu đã đổi/tạm dừng frontend ĐAU).
- Không có model nào được tải (không có Ollama), không cài Docker.

## Ngoài phạm vi (out of scope)

- Cấu hình LLM (Ollama local hoặc OpenAI-compatible) để nhân vật trò chuyện.
- Cá nhân hoá nhân vật/bản đồ.
- Deploy AI Town ra production.
- Tích hợp AI Town vào repo ĐAU.

## Mở / cần người dùng thao tác

- Đăng nhập Convex Cloud (bước duy nhất cần tài khoản và trình duyệt).
- Quyết định xử lý xung đột cổng 5173: tạm dừng frontend ĐAU hay đổi cổng AI Town (khuyến nghị đổi cổng AI Town để không gián đoạn demo ĐAU đang công khai qua Tailscale).
