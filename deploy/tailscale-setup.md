# Truy cập DAU Second Brain qua Tailscale (không cần domain)

Mục tiêu: 2–3 người test ở xa vẫn vào được app qua HTTPS, miễn phí, không cần
mua domain, không mở cổng router.

Kiến trúc: `tailscale serve` phát HTTPS cho máy này và chuyển tiếp vào
`http://127.0.0.1:5173`. Frontend (Vite) tự proxy `/api` sang backend
`127.0.0.1:8000`, nên backend và PostgreSQL không lộ ra ngoài.

## 1. Cài Tailscale trên máy chạy app

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

Kiểm tra:

```bash
tailscale version
```

## 2. Đăng nhập vào tailnet

```bash
sudo tailscale up
```

Lệnh in ra một URL `https://login.tailscale.com/...`. Mở URL đó bằng trình duyệt,
đăng nhập (Google/GitHub/Microsoft). Đây là tài khoản quản trị nhóm test.

Kiểm tra:

```bash
tailscale status
tailscale ip -4
```

Kết quả mong đợi: trạng thái `... linux  active`, có một IP `100.x.y.z`.

## 3. Cho phép tài khoản hiện tại điều khiển tailscale (không cần sudo mỗi lần)

```bash
sudo tailscale set --operator=$USER
tailscale serve status
```

## 4. Bật HTTPS certificate cho tailnet

Trong admin console: https://login.tailscale.com/admin/dns

- Bật **MagicDNS**.
- Bật **HTTPS Certificates**.

Không bật hai mục này thì `tailscale serve` không cấp được chứng chỉ HTTPS.

Kiểm tra nhanh bằng CLI (không cần sudo):

```bash
tailscale status --json | python3 -c "import json,sys; print('CertDomains:', json.load(sys.stdin).get('CertDomains'))"
```

Kết quả phải có tên miền, không phải `None`. Nếu vẫn `None` thì HTTPS chưa bật
và lệnh `tailscale serve --bg 5173` sẽ treo chờ chứng chỉ.

### Phương án không cần admin console

Tailscale luôn mã hoá traffic bằng WireGuard, nên HTTP trong tailnet vẫn an toàn
với nhóm 2–3 người tin cậy. Dùng cổng 80 thay vì HTTPS:

```bash
sudo tailscale serve --bg --http=80 5173
```

Link sẽ là `http://<ten-may>.<tailnet>.ts.net` (không có `s`). Dùng tạm khi chưa
bật được HTTPS; nên bật HTTPS trước khi demo chính thức.

## 5. Phát frontend qua Tailscale

Đảm bảo frontend đang chạy ở cổng 5173 (dev hoặc preview):

```bash
cd frontend
VITE_API_URL=/api/v1 npm run dev -- --host 127.0.0.1 --port 5173
```

Quan trọng: `vite.config.ts` phải khai báo `allowedHosts: ['.ts.net']`, nếu không
Vite trả `403 Blocked request. This host ... is not allowed` khi mở qua Tailscale.

Terminal khác (cần `sudo`, hoặc chạy `sudo tailscale set --operator=$USER` một lần):

```bash
sudo tailscale serve --bg 5173
tailscale serve status
```

Kết quả mong đợi có dạng:

```
https://<ten-may>.<tailnet>.ts.net
|-- / proxy http://127.0.0.1:5173
```

Link đó là địa chỉ gửi cho người test.

## 6. Mời người test

https://login.tailscale.com/admin/users → **Invite external users** (hoặc Invite people).

- Gửi link mời cho từng người.
- Họ cài Tailscale trên máy/điện thoại, đăng nhập, bấm chấp nhận.
- Sau đó họ mở link `https://<ten-may>.<tailnet>.ts.net`.

Người không nằm trong tailnet không mở được link, kể cả khi biết địa chỉ.

## 7. Kiểm tra

```bash
tailscale serve status
tailscale status
```

Từ máy đã join tailnet:

```bash
curl -I https://<ten-may>.<tailnet>.ts.net
```

Mong đợi: `HTTP/2 200`.

Trong app: đăng nhập, upload PDF scan có tick xác nhận, hỏi chatbot.

## 8. Tắt / bật lại

```bash
tailscale serve --bg off      # ngừng phát web
tailscale serve --bg 5173     # bật lại
sudo tailscale down           # ngắt khỏi tailnet
sudo tailscale up             # nối lại
```

## 9. Ghi chú bảo mật

- Chỉ chia sẻ link cho đúng 2–3 người test; không đăng công khai.
- Tailscale mặc định cho mọi thành viên tailnet truy cập mọi máy. Với nhóm nhỏ
  tin cậy thì chấp nhận được; nếu cần chặt hơn, tạo ACL/tag trong admin console.
- Khi Tailscale đã chạy ổn, có thể đổi frontend sang `--host 127.0.0.1` để đóng
  truy cập LAN (cổng 5173) mà vẫn dùng được qua Tailscale.
- Không commit file cấu hình/credential của Tailscale vào repo.
