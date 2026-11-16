"""Tài khoản cố định duy nhất của hệ thống DAU Second Brain.

Hệ thống chỉ dùng MỘT tài khoản duy nhất, được khai báo tập trung tại đây:
    - Email    : admin@dau.edu.vn
    - Mật khẩu : Dau@Second2026
    - Vai trò  : admin

Các thông tin trên được dùng ở 3 nơi:
    1. `POST /auth/login`  -> so khớp thẳng với tài khoản cố định.
    2. `app/main.py`      -> tự đồng bộ bảng `users` mỗi lần khởi động
                            (tạo nếu chưa có, đặt lại mật khẩu + role nếu có).
    3. `app/scripts/create_admin.py` -> CLI đặt lại mật khẩu nhanh.

Ghi chú: mật khẩu nằm trong mã nguồn theo yêu cầu "cố định 1 tài khoản duy nhất"
của hệ thống demo/đồ án. Nếu triển khai thật, hãy chuyển sang biến môi trường
(`DAU_FIXED_ACCOUNT_EMAIL` / `DAU_FIXED_ACCOUNT_PASSWORD`).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Thông tin tài khoản cố định
# ---------------------------------------------------------------------------
FIXED_ACCOUNT_EMAIL = "admin@dau.edu.vn"
FIXED_ACCOUNT_PASSWORD = "Dau@Second2026"
FIXED_ACCOUNT_ROLE = "admin"

# Danh sách email được phép đăng nhập (chỉ tài khoản cố định).
ALLOWED_LOGIN_EMAILS = {FIXED_ACCOUNT_EMAIL.lower()}


def normalize_email(email: str) -> str:
    """Chuẩn hoá email để so sánh không phân biệt hoa/thường + bỏ khoảng trắng."""
    return (email or "").strip().lower()


def is_fixed_account_email(email: str) -> bool:
    """True nếu `email` là tài khoản cố định duy nhất của hệ thống."""
    return normalize_email(email) in ALLOWED_LOGIN_EMAILS


def verify_fixed_account(email: str, password: str) -> bool:
    """Kiểm tra thông tin đăng nhập có khớp tài khoản cố định hay không."""
    if not is_fixed_account_email(email):
        return False
    return (password or "") == FIXED_ACCOUNT_PASSWORD


def sync_fixed_account(db) -> bool:
    """Đồng bộ bảng `users` với tài khoản cố định.

    - Nếu tài khoản chưa tồn tại: tạo mới (hash mật khẩu cố định, role admin).
    - Nếu đã tồn tại: đặt lại `hashed_password`, `role`, `is_active` cho khớp.
    - Xoá mọi tài khoản khác để hệ thống chỉ còn đúng một tài khoản.

    Trả về True nếu có thay đổi (đã tạo/đặt lại/xoá), False nếu DB đã đúng.
    """
    from app.core.security import get_password_hash
    from app.db.models import User

    changed = False
    user = (
        db.query(User)
        .filter(User.email == FIXED_ACCOUNT_EMAIL)
        .first()
    )

    if user is None:
        user = User(
            email=FIXED_ACCOUNT_EMAIL,
            hashed_password=get_password_hash(FIXED_ACCOUNT_PASSWORD),
            role=FIXED_ACCOUNT_ROLE,
            is_active=True,
        )
        db.add(user)
        changed = True
    else:
        expected_hash = get_password_hash(FIXED_ACCOUNT_PASSWORD)
        if user.hashed_password != expected_hash:
            user.hashed_password = expected_hash
            changed = True
        if user.role != FIXED_ACCOUNT_ROLE:
            user.role = FIXED_ACCOUNT_ROLE
            changed = True
        if not user.is_active:
            user.is_active = True
            changed = True

    # Xoá các tài khoản khác (hệ thống chỉ dùng 1 tài khoản duy nhất).
    others = db.query(User).filter(User.email != FIXED_ACCOUNT_EMAIL).all()
    for other in others:
        db.delete(other)
        changed = True

    if changed:
        db.commit()
    return changed
