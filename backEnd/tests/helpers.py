import datetime
from typing import Any, Dict, Optional

from jose import jwt

TEST_JWT_SECRET = "test-secret-key-at-least-32-chars-long-000"


def make_supabase_jwt(
    user_id: str = "usr_test_1",
    email: Optional[str] = "gooner@example.com",
    display_name: Optional[str] = None,
    club_id: str = "arsenal",
    audience: Optional[str] = "authenticated",
    exp_delta_seconds: int = 3600,
    secret: str = TEST_JWT_SECRET,
    algorithm: str = "HS256",
    user_metadata: Optional[Dict[str, Any]] = None,
    app_metadata: Optional[Dict[str, Any]] = None,
    include_exp: bool = True,
    include_sub: bool = True,
) -> str:
    """Mint a Supabase-shaped JWT for backend integration and security tests."""
    now = datetime.datetime.now(datetime.timezone.utc)
    meta: Dict[str, Any] = {"favorite_club_id": club_id}
    if display_name is not None:
        meta["display_name"] = display_name
    if user_metadata:
        meta.update(user_metadata)

    payload: Dict[str, Any] = {
        "iat": int(now.timestamp()),
        "user_metadata": meta,
        "app_metadata": app_metadata or {"provider": "email"},
    }
    if include_sub:
        payload["sub"] = user_id
    if email is not None:
        payload["email"] = email
    if audience is not None:
        payload["aud"] = audience
    if include_exp:
        payload["exp"] = int((now + datetime.timedelta(seconds=exp_delta_seconds)).timestamp())

    return jwt.encode(payload, secret, algorithm=algorithm)


def auth_headers(user_id: str = "usr_test_1", **kwargs: Any) -> Dict[str, str]:
    """Build Authorization: Bearer <jwt> headers for a test user."""
    token = make_supabase_jwt(user_id=user_id, **kwargs)
    return {"Authorization": f"Bearer {token}"}
