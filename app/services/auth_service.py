from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.security import generate_jwt, hash_password, verify_password, verify_totp
from app.models import Role, User
from app.repositories.auth_repository import AuthRepository


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuthRepository(db)

    def bootstrap_admin(self) -> None:
        user = self.repo.get_user(settings.admin_user)
        if user:
            return
        admin = User(
            username=settings.admin_user,
            password_hash=hash_password(settings.admin_password),
            role=Role.ADMIN.value,
            totp_secret=settings.admin_totp_secret,
            is_enabled=True,
        )
        self.repo.save_user(admin)

    def login(self, username: str, password: str, totp_code: str) -> tuple[str, str]:
        user = self.repo.get_user(username)
        if not user or not user.is_enabled:
            raise ValueError("Invalid credentials")
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        if not verify_totp(user.totp_secret, totp_code):
            raise ValueError("Invalid TOTP")
        token = generate_jwt(user.username, user.role)
        return token, user.role

    def audit(self, actor: str, action: str, object_type: str, object_id: str, details: str = ""):
        self.repo.log(actor, action, object_type, object_id, details)
