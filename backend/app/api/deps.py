from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import decode_access_token
from app.models.user import User

bearer_scheme = HTTPBearer()
bearer_scheme_optional = HTTPBearer(auto_error=False)

SessionDep = Annotated[Session, Depends(get_session)]
BearerDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]


def _resolve_user(raw_token: str, session: Session) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(raw_token)
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


def get_current_user(creds: BearerDep, session: SessionDep) -> User:
    return _resolve_user(creds.credentials, session)


def get_current_user_sse(
    session: SessionDep,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme_optional)] = None,
    token: Annotated[str | None, Query()] = None,
) -> User:
    """Like get_current_user but also accepts ?token= for EventSource clients."""
    raw = (creds.credentials if creds else None) or token
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _resolve_user(raw, session)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
StreamUserDep = Annotated[User, Depends(get_current_user_sse)]
