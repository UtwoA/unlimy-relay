import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "Unlimy Relay Master")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://unlimy:unlimy@postgres:5432/unlimy_relay")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_algo: str = os.getenv("JWT_ALGO", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))
    rotation_default_hours: int = int(os.getenv("ROTATION_DEFAULT_HOURS", "72"))
    admin_user: str = os.getenv("ADMIN_USER", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin")
    admin_totp_secret: str = os.getenv("ADMIN_TOTP_SECRET", "JBSWY3DPEHPK3PXP")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
    ip_allowlist: str = os.getenv("IP_ALLOWLIST", "")


settings = Settings()
