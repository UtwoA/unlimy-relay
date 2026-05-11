from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.infra.security import decode_jwt

security = HTTPBearer()
_auth_attempts: dict[str, list[datetime]] = {}


def check_ip_allowlist(request: Request) -> None:
    raw = settings.ip_allowlist.strip()
    if not raw:
        return
    allowed = {item.strip() for item in raw.split(",") if item.strip()}
    client = request.client.host if request.client else ""
    if client not in allowed:
        raise HTTPException(status_code=403, detail="IP is not allowlisted")


def rate_limit_auth(identity: str, max_attempts: int = 10, window_seconds: int = 60) -> None:
    now = datetime.now(tz=timezone.utc)
    attempts = _auth_attempts.setdefault(identity, [])
    attempts[:] = [x for x in attempts if (now - x).total_seconds() <= window_seconds]
    if len(attempts) >= max_attempts:
        raise HTTPException(status_code=429, detail="Too many auth attempts")
    attempts.append(now)


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = decode_jwt(credentials.credentials)
        if "sub" not in payload or "role" not in payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def require_roles(*roles: str):
    def checker(payload: dict = Depends(require_auth)) -> dict:
        if payload.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return payload

    return checker
