"""Authentication dependencies for Bearer JWT validation."""

from typing import cast
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    auth_header: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    """
    Validate Bearer token from Authorization header.
    """
    token = None
    if auth_header and auth_header.credentials:
        token = auth_header.credentials

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = AuthService.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    username: str = cast(str, payload.get("sub"))
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return username
