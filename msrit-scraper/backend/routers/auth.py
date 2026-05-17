import logging
import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import RegisterRequest, LoginRequest, TokenResponse
from backend.config import JWT_EXPIRE_MINUTES, FERNET_KEY
from backend import crud
from backend.auth import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


@router.post("/register", status_code=201, summary="Register a new teacher account")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if not FERNET_KEY:
        raise HTTPException(status_code=500, detail="Server encryption key not configured")

    existing = crud.get_teacher_by_email(db, body.email)

    from cryptography.fernet import Fernet
    app_hash = _hash_password(body.app_password)
    portal_enc = Fernet(FERNET_KEY.encode()).encrypt(body.portal_password.encode()).decode()

    # Teacher added via CLI (no app_password_hash) — set password AND re-encrypt portal creds
    if existing and not existing.app_password_hash:
        crud.set_teacher_app_password(
            db, existing.id, app_hash,
            portal_username=body.portal_username,
            portal_password_encrypted=portal_enc,
        )
        logger.info(f"Existing teacher set app password + re-encrypted portal creds: {existing.email} (id={existing.id})")
        return {"id": existing.id, "email": existing.email, "name": existing.name}

    # Already fully registered
    if existing and existing.app_password_hash:
        raise HTTPException(status_code=400, detail="Email already registered")

    teacher = crud.register_teacher(
        db,
        name=body.name,
        email=body.email,
        portal_username=body.portal_username,
        portal_password_encrypted=portal_enc,
        app_password_hash=app_hash,
    )
    logger.info(f"New teacher registered: {teacher.email} (id={teacher.id})")
    return {"id": teacher.id, "email": teacher.email, "name": teacher.name}


@router.post("/login", response_model=TokenResponse, summary="Login and receive JWT token")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    teacher = crud.get_teacher_by_email(db, body.email)
    if not teacher or not teacher.app_password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not _verify_password(body.password, teacher.app_password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(teacher.id, JWT_EXPIRE_MINUTES)
    logger.info(f"Teacher logged in: {teacher.email} (id={teacher.id})")
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        teacher_id=teacher.id,
        teacher_name=teacher.name,
        teacher_email=teacher.email,
    )
