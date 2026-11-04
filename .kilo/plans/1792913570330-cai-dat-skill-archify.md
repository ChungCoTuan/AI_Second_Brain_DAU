# Kế hoạch: Cài đặt skill Archify (toàn cục cho Kilo)

## Mục tiêu

Cài skill **Archify** (`tt-a1i/archify`, v3.2) — công cụ tạo sơ đồ HTML tương tác
(architecture, ERD, workflow, sequence, dataflow, lifecycle, class, tree, timeline,
waterfall) — vào Kilo **toàn cục** để agent dùng khi vẽ sơ đồ cho báo cáo đồ án
(vd: ERD cho `db/models.py`, sơ đồ kiến trúc backend/frontend).

## Quyết định đã chốt

- **Vị trí**: toàn cục `~/.config/kilo/skills/archify/` (user đã chọn).
- **Phương thức**: tải gói skill chính thức `archify.zip` rồi giải nén + copy
  (KHÔNG dùng `git clone` vì bị deny trong permission; KHÔNG dùng `npx skills add`
  vì lệnh đó cài vào `~/.claude`/`~/.agents`, không đăng ký với Kilo).
- **Node**: SKILL.md yêu cầu Node. Máy đã có Node v22.23.4 tại `~/.local/node/bin`
  nhưng chưa nằm trên `PATH` → phải thêm vào `PATH` để lệnh `node bin/archify.mjs`
  chạy được.

## Tham chiếu quan trọng

- Skill frontmatter đã xác minh **Kilo-compatible**: `name: archify`, `description: ...`
  (kèm `license`, `metadata` vô hại). Kilo quét `skills/<name>/SKILL.md` trong các
  config dir (`.kilo`, `~/.config/kilo`, ...) → sẽ tự phát hiện khi khởi động lại.
- Gói `archify/` gồm: `SKILL.md`, `bin/archify.mjs` (CLI zero-dep), `schemas/`,
  `renderers/`, `references/`, `examples/`, `assets/`, `locales/`, `explainer/`,
  `recipes/`, `migrations/`, `scripts/`, `delta/`, `brand-marks/`, `package.json`,
  `package-lock.json`, `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `skill-release.json`.
- Setup check theo SKILL.md: `node bin/archify.mjs doctor`.

## Các bước thực thi (ordered)

1. Tạo thư mục tạm: `mkdir -p /tmp/kilo/archify-install`.
2. Tải gói skill:
   `curl -fL https://github.com/tt-a1i/archify/raw/refs/heads/main/archify.zip -o /tmp/kilo/archify-install/archify.zip`
3. Giải nén: `unzip -q /tmp/kilo/archify-install/archify.zip -d /tmp/kilo/archify-install/pkg`
4. Xác định thư mục chứa `SKILL.md` sau giải nén (zip có thể lồng thêm một cấp).
   Đích cuối cùng PHẢI là `~/.config/kilo/skills/archify/SKILL.md`.
5. `mkdir -p ~/.config/kilo/skills/archify` và copy **toàn bộ nội dung thư mục chứa
   `SKILL.md`** (gồm cả `bin/`, `schemas/`, `references/`, ...) vào đó:
   `cp -r <dir-chứa-SKILL.md>/. ~/.config/kilo/skills/archify/`
6. Đảm bảo Node trên PATH (chỉ thêm 1 lần, không trùng lặp):
   - Kiểm tra `grep -F 'local/node/bin' ~/.bashrc` đã có chưa.
   - Nếu chưa: thêm `export PATH="$HOME/.local/node/bin:$PATH"` vào `~/.bashrc`.
   - Trong session hiện tại dùng `export PATH="$HOME/.local/node/bin:$PATH"`.
7. Kiểm tra cài đặt:
   `node ~/.config/kilo/skills/archify/bin/archify.mjs doctor`
8. (Tùy chọn, smoke test) `node ~/.config/kilo/skills/archify/bin/archify.mjs demo /tmp/kilo/archify-demo`

## Kiểm chứng (validation)

- [ ] `~/.config/kilo/skills/archify/SKILL.md` tồn tại, frontmatter có `name: archify` + `description` (không chỉnh sửa tay).
- [ ] `~/.config/kilo/skills/archify/bin/archify.mjs` tồn tại.
- [ ] `node -v` in ra `v22.23.4` (hoặc >=18) sau khi thêm PATH.
- [ ] `doctor` chạy không lỗi (exit 0).
- [ ] Ghi rõ cho user: skill chỉ xuất hiện trong `available_skills` của Kilo ở **lần khởi động lại** (session mới) — trong session hiện tại KHÔNG tự thêm được.

## Rủi ro & lưu ý

- **Cấu trúc zip**: `archify.zip` có thể lồng folder; bước 4 phải kiểm tra để copy đúng
  vị trí của `SKILL.md` (không copy folder bao ngoài thừa).
- **Trình duyệt headless**: gate `browser-check` trong lệnh `finalize` của Archify cần
  Chromium/thuật toán real-browser. Nếu máy chưa có, việc **vẽ** sơ đồ có thể fail ở
  gate này (vấn đề runtime khi dùng, không phải cài đặt). Không cài trình duyệt trong
  phạm vi kế hoạch này; chỉ ghi chú để user biết.
- **Quyền (permission)**: các lệnh `curl`, `unzip`, ghi vào `~/.config/kilo/` nằm ngoài
  workspace → sẽ cần user phê duyệt (`external_directory` = ask, `bash` = ask).
- **Không** enable chế độ `archify explainer` (SKILL.md nhắc tới) trừ khi user yêu cầu thêm.
- Chỉ tạo file ngoài repo trong `~/.config/kilo/skills/archify/`; không sửa code project.