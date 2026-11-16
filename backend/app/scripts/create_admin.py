"""Đặt lại / tạo các tài khoản cố định của hệ thống DAU Second Brain.

Hệ thống dùng 2 tài khoản cố định:
    admin@dau.edu.vn     / Dau@Second2026  -> vai trò `admin`
    lecturer@dau.edu.vn  / Dau@Second2026  -> vai trò `lecturer`

Cách dùng (chạy trong backend/ với venv đã kích hoạt):
    python -m app.scripts.create_admin

Script tự đồng bộ bảng `users`:
    - tạo tài khoản nếu chưa có,
    - đặt lại mật khẩu + vai trò nếu đã tồn tại,
    - xoá mọi tài khoản khác.
"""

from __future__ import annotations

from app.core.fixed_account import FIXED_ACCOUNTS, sync_fixed_account
from app.db.models import Base
from app.db.session import SessionLocal, engine


def main() -> int:
    # Cho phép chạy CLI trước lần khởi động app đầu tiên.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        changed = sync_fixed_account(db)
    finally:
        db.close()

    if changed:
        print("Đã đồng bộ các tài khoản cố định:")
    else:
        print("Các tài khoản cố định đã đúng chuẩn, không thay đổi gì:")
    for email, password, role in FIXED_ACCOUNTS:
        print(f"  - {email} / {password} (vai trò: {role})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
