from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import get_db
from .models import AdminUser
from .schemas import TokenResponse
from .auth_utils import verify_password, hash_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def _get_admin_by_username(db: Session, username: str) -> Optional[AdminUser]:
    return db.query(AdminUser).filter(AdminUser.username == username).first()


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Admin login",
    description="Authenticate admin user and return a JWT access token.",
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint compatible with OAuth2PasswordRequestForm.

    Parameters:
      - form_data: Form body containing 'username' and 'password'
    Returns:
      - TokenResponse with access_token and token_type
    """
    user = _get_admin_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token, token_type="bearer")


def get_current_admin(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> AdminUser:
    """Dependency to get the current authenticated admin user."""
    from .auth_utils import decode_access_token

    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = _get_admin_by_username(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# PUBLIC_INTERFACE
@router.post(
    "/seed-admin",
    summary="Seed a default admin user",
    description="Utility endpoint to create a default admin if none exists. Not protected to enable first-time setup.",
)
def seed_admin(db: Session = Depends(get_db)):
    """Creates default admin 'admin'/'admin123' if not present. For development convenience."""
    existing = _get_admin_by_username(db, "admin")
    if existing:
        return {"status": "exists"}
    user = AdminUser(username="admin", password_hash=hash_password("admin123"))
    db.add(user)
    db.commit()
    return {"status": "created", "username": "admin", "password": "admin123"}
