"""Tạo tài khoản quản trị/giảng viên một lần, không dùng mật khẩu mặc định.

Cách dùng (chạy trong backend/ với venv đã kích hoạt):
    python -m app.scripts.create_admin --email admin@example.com --role admin

Mật khẩu được hỏi bằng getpass, không truyền qua tham số dòng lệnh và không ghi log.
"""

from __future__ import annotations

import argparse
import getpass
import sys

from app.core.security import get_password_hash
from app.db.models import Base, User
from app.db.session import SessionLocal, engine


def create_user(email: str, role: str, password: str) -> bool:
    # Cho phép chạy CLI trước lần khởi động app đầu tiên.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print(f"Tài khoản {email} đã tồn tại, không thay đổi gì.")
            return False

        db.add(User(email=email, hashed_password=get_password_hash(password), role=role))
        db.commit()
        print(f"Đã tạo tài khoản {email} với vai trò {role}.")
        return True
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Tạo tài khoản DAU Second Brain")
    parser.add_argument("--email", required=True, help="Email đăng nhập")
    parser.add_argument(
        "--role", choices=["admin", "lecturer"], default="lecturer", help="Vai trò tài khoản"
    )
    args = parser.parse_args()

    password = getpass.getpass("Mật khẩu: ")
    confirm = getpass.getpass("Nhập lại mật khẩu: ")
    if password != confirm:
        print("Mật khẩu nhập lại không khớp.", file=sys.stderr)
        return 1
    if len(password) < 10:
        print("Mật khẩu phải có ít nhất 10 ký tự.", file=sys.stderr)
        return 1

    return 0 if create_user(args.email, args.role, password) else 0


if __name__ == "__main__":
    raise SystemExit(main())
