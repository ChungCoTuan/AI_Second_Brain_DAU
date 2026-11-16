from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.api.schemas.user import UserResponse, Token
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.core.fixed_account import (
    FIXED_ACCOUNT_EMAIL,
    LECTURER_ACCOUNT_EMAIL,
    normalize_email,
    get_role_for_email,
    verify_fixed_account,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Đăng nhập bằng các tài khoản cố định của hệ thống.

    - Quản trị viên: `admin@dau.edu.vn` / `Dau@Second2026`  -> role `admin`
    - Giảng viên   : `lecturer@dau.edu.vn` / `Dau@Second2026` -> role `lecturer`
    """
    email = normalize_email(form_data.username)

    if not verify_fixed_account(email, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác. Vui lòng kiểm tra lại.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Lấy user trong DB để trả về /auth/me đúng thông tin (id, role, is_active).
    # Nếu chưa có (app chưa từng khởi động) thì tự tạo, tránh lỗi 500.
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        from app.core.security import get_password_hash

        user = User(
            email=email,
            hashed_password=get_password_hash(form_data.password),
            role=get_role_for_email(email),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị vô hiệu hoá. Vui lòng liên hệ quản trị viên.",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
