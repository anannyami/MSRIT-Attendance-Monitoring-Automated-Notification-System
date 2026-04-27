from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.config import JWT_SECRET_KEY, JWT_ALGORITHM
from backend import crud

_bearer = HTTPBearer()


def create_access_token(teacher_id: int, expire_minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    return jwt.encode(
        {"sub": str(teacher_id), "exp": expire},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def get_current_teacher(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        teacher_id: Optional[str] = payload.get("sub")
        if not teacher_id:
            raise exc
    except JWTError:
        raise exc

    teacher = crud.get_teacher_by_id(db, int(teacher_id))
    if teacher is None:
        raise exc
    return teacher
