import base64
import os
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


def encrypt_secret(secret: str) -> str:
    return base64.b64encode(secret.encode("utf-8")).decode("utf-8")


def decrypt_secret(secret_encrypted: str) -> str:
    return base64.b64decode(secret_encrypted.encode("utf-8")).decode("utf-8")


def build_tg_proxy_link(host: str, port: int, secret: str) -> str:
    return f"tg://proxy?server={host}&port={port}&secret={secret}"


def generate_jwt(username: str) -> str:
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": username, "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algo)


def verify_admin(username: str, password: str) -> bool:
    env_user = os.getenv("ADMIN_USER", "admin")
    env_pass = os.getenv("ADMIN_PASSWORD", "admin")
    return username == env_user and password == env_pass
