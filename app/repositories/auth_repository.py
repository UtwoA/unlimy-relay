from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog, User


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def save_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def log(self, actor: str, action: str, object_type: str, object_id: str, details: str = "") -> None:
        self.db.add(AuditLog(actor=actor, action=action, object_type=object_type, object_id=object_id, details=details))
        self.db.commit()
