"""Các tài khoản cố định của hệ thống DAU Second Brain.

Hệ thống dùng 2 tài khoản cố định, khai báo tập trung tại đây:

    1. Quản trị viên (admin)
       - Email    : admin@dau.edu.vn
       - Mật khẩu : Dau@Second2026
       - Vai trò  : admin
    2. Giảng viên (lecturer)
       - Email    : lecturer@dau.edu.vn
       - Mật khẩu : Dau@Second2026
       - Vai trò  : lecturer

Các thông tin trên được dùng ở 3 nơi:
    1. `POST /auth/login`  -> so khớp thẳng với tài khoản cố định.
    2. `app/main.py`      -> tự đồng bộ bảng `users` mỗi lần khởi động
                            (tạo nếu chưa có, đặt lại mật khẩu + role nếu có).
    3. `app/scripts/create_admin.py` -> CLI đặt lại mật khẩu nhanh.

Ghi chú: mật khẩu nằm trong mã nguồn theo yêu cầu "cố định tài khoản" của hệ
thống demo/đồ án. Nếu triển khai thật, hãy chuyển sang biến môi trường
(`DAU_FIXED_ACCOUNT_EMAIL` / `DAU_FIXED_ACCOUNT_PASSWORD`).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Thông tin tài khoản cố định
# ---------------------------------------------------------------------------
FIXED_ACCOUNT_EMAIL = "admin@dau.edu.vn"
FIXED_ACCOUNT_PASSWORD = "Dau@Second2026"
FIXED_ACCOUNT_ROLE = "admin"

LECTURER_ACCOUNT_EMAIL = "lecturer@dau.edu.vn"
LECTURER_ACCOUNT_PASSWORD = "Dau@Second2026"
LECTURER_ACCOUNT_ROLE = "lecturer"

# Danh sách email được phép đăng nhập.
ALLOWED_LOGIN_EMAILS = {
    FIXED_ACCOUNT_EMAIL.lower(),
    LECTURER_ACCOUNT_EMAIL.lower(),
}

# Danh sách tài khoản cố định: (email, password, role)
FIXED_ACCOUNTS = (
    (FIXED_ACCOUNT_EMAIL, FIXED_ACCOUNT_PASSWORD, FIXED_ACCOUNT_ROLE),
    (LECTURER_ACCOUNT_EMAIL, LECTURER_ACCOUNT_PASSWORD, LECTURER_ACCOUNT_ROLE),
)


def normalize_email(email: str) -> str:
    """Chuẩn hoá email để so sánh không phân biệt hoa/thường + bỏ khoảng trắng."""
    return (email or "").strip().lower()


def is_fixed_account_email(email: str) -> bool:
    """True nếu `email` là một trong các tài khoản cố định của hệ thống."""
    return normalize_email(email) in ALLOWED_LOGIN_EMAILS


def verify_fixed_account(email: str, password: str) -> bool:
    """Kiểm tra thông tin đăng nhập có khớp tài khoản cố định nào hay không.

    Trả về False nếu email lạ, hoặc mật khẩu không khớp tài khoản tương ứng.
    """
    normalized = normalize_email(email)
    for acc_email, acc_password, _role in FIXED_ACCOUNTS:
        if normalized == acc_email.lower():
            return (password or "") == acc_password
    return False


def get_role_for_email(email: str) -> str:
    """Trả về vai trò ứng với email cố định (mặc định `lecturer`)."""
    normalized = normalize_email(email)
    for acc_email, _password, role in FIXED_ACCOUNTS:
        if normalized == acc_email.lower():
            return role
    return LECTURER_ACCOUNT_ROLE


def sync_fixed_account(db) -> bool:
    """Đồng bộ bảng `users` với các tài khoản cố định.

    - Nếu tài khoản chưa tồn tại: tạo mới (hash mật khẩu cố định, đúng vai trò).
    - Nếu đã tồn tại: đặt lại `hashed_password`, `role`, `is_active` cho khớp.
    - Xoá mọi tài khoản khác để hệ thống chỉ còn đúng các tài khoản cố định.

    Trả về True nếu có thay đổi (đã tạo/đặt lại/xoá), False nếu DB đã đúng.
    """
    from app.core.security import get_password_hash
    from app.db.models import User

    changed = False
    fixed_emails = {email for email, _pw, _role in FIXED_ACCOUNTS}

    for acc_email, acc_password, acc_role in FIXED_ACCOUNTS:
        user = db.query(User).filter(User.email == acc_email).first()

        if user is None:
            db.add(
                User(
                    email=acc_email,
                    hashed_password=get_password_hash(acc_password),
                    role=acc_role,
                    is_active=True,
                )
            )
            changed = True
            continue

        if not _password_matches(user.hashed_password, acc_password):
            user.hashed_password = get_password_hash(acc_password)
            changed = True
        if user.role != acc_role:
            user.role = acc_role
            changed = True
        if not user.is_active:
            user.is_active = True
            changed = True

    # Xoá các tài khoản khác (hệ thống chỉ dùng các tài khoản cố định).
    others = db.query(User).filter(~User.email.in_(fixed_emails)).all()
    for other in others:
        db.delete(other)
        changed = True

    if changed:
        db.commit()
    return changed


def _password_matches(hashed_password: str, plain_password: str) -> bool:
    """So khớp mật khẩu với hash đã lưu, trả về False nếu hash không hợp lệ."""
    from app.core.security import verify_password

    try:
        return verify_password(plain_password, hashed_password)
    except Exception:  # noqa: BLE001 - hash hỏng thì coi như không khớp
        return False
