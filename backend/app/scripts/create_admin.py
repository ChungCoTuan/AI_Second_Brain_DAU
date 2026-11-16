"""Đặt lại / tạo tài khoản cố định duy nhất của hệ thống DAU Second Brain.

Hệ thống chỉ dùng MỘT tài khoản:
    admin@dau.edu.vn / Dau@Second2026

Cách dùng (chạy trong backend/ với venv đã kích hoạt):
    python -m app.scripts.create_admin

Script tự đồng bộ bảng `users`:
    - tạo tài khoản nếu chưa có,
    - đặt lại mật khẩu + vai trò `admin` nếu đã tồn tại,
    - xoá mọi tài khoản khác.
"""

from __future__ import annotations

import sys

from app.core.fixed_account import (
    FIXED_ACCOUNT_EMAIL,
    FIXED_ACCOUNT_PASSWORD,
    FIXED_ACCOUNT_ROLE,
    sync_fixed_account,
)
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
        print(f"Đã đồng bộ tài khoản cố định: {FIXED_ACCOUNT_EMAIL} (vai trò {FIXED_ACCOUNT_ROLE}).")
    else:
        print(f"Tài khoản {FIXED_ACCOUNT_EMAIL} đã đúng chuẩn, không thay đổi gì.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
