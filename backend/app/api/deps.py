from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import decode_access_token
from app.models.user import User

bearer_scheme = HTTPBearer()

SessionDep = Annotated[Session, Depends(get_session)]
BearerDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]


def get_current_user(creds: BearerDep, session: SessionDep) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(creds.credentials)
        sub = payload.get("sub")
        if not sub:
            raise credentials_exc
        user_id = UUID(sub)
    except (JWTError, ValueError) as exc:
        raise credentials_exc from exc

    user = session.get(User, user_id)
    if user is None:
        raise credentials_exc
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
