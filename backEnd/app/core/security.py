from typing import Annotated, Any, Optional

from fastapi import Depends, Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings

_bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    id: str
    email: Optional[str] = None
    display_name: str
    club_id: str = "arsenal"
    role: str = "supporter"


def _unauthorized(detail: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decode_supabase_jwt(token: str) -> AuthenticatedUser:
    secret = (settings.SUPABASE_JWT_SECRET or "").strip()
    if not secret:
        raise _unauthorized("Authentication is not configured on this server")

    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise _unauthorized("Invalid token header") from exc

    if not isinstance(header, dict) or header.get("alg") != "HS256":
        raise _unauthorized("Unsupported token algorithm")

    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_sub": True,
                "require_aud": True,
                "require_exp": True,
                "require_sub": True,
            },
        )
    except JWTError as exc:
        raise _unauthorized("Invalid or expired token") from exc

    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub.strip():
        raise _unauthorized("Token missing valid subject")

    email_raw = payload.get("email")
    email = email_raw.strip() if isinstance(email_raw, str) and email_raw.strip() else None

    user_meta = payload.get("user_metadata")
    if not isinstance(user_meta, dict):
        user_meta = {}

    app_meta = payload.get("app_metadata")
    if not isinstance(app_meta, dict):
        app_meta = {}

    email_prefix = email.split("@", 1)[0] if email and "@" in email else None
    raw_name = (
        user_meta.get("display_name")
        or user_meta.get("full_name")
        or user_meta.get("name")
        or email_prefix
        or "Supporter"
    )
    display_name = str(raw_name).strip()[:100] or "Supporter"

    raw_club = user_meta.get("favorite_club_id")
    club_id = (
        str(raw_club).strip()[:50]
        if isinstance(raw_club, str) and raw_club.strip()
        else "arsenal"
    )

    # Never trust user_metadata or top-level claims for privilege elevation
    role = "admin" if app_meta.get("role") == "admin" else "supporter"

    return AuthenticatedUser(
        id=sub.strip(),
        email=email,
        display_name=display_name,
        club_id=club_id,
        role=role,
    )


def _extract_bearer_token(
    authorization: Optional[str],
    credentials: Optional[HTTPAuthorizationCredentials],
) -> Optional[str]:
    if authorization is None:
        if credentials is not None and credentials.credentials:
            return credentials.credentials
        return None

    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise _unauthorized("Invalid Authorization header format")
    return parts[1].strip()


async def optional_current_user(
    authorization: Annotated[Optional[str], Header(include_in_schema=False)] = None,
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Security(_bearer_scheme)] = None,
) -> Optional[AuthenticatedUser]:
    token = _extract_bearer_token(authorization, credentials)
    if token is None:
        return None
    return _decode_supabase_jwt(token)


async def get_current_user(
    user: Annotated[Optional[AuthenticatedUser], Depends(optional_current_user)],
) -> AuthenticatedUser:
    if user is None:
        raise _unauthorized("Authentication required")
    return user


CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]
OptionalUserDep = Annotated[Optional[AuthenticatedUser], Depends(optional_current_user)]
