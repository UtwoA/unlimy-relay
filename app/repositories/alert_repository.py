from sqlalchemy.orm import Session

from app.models import AlertEvent


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, node_id: int | None, kind: str, severity: str, message: str, dedup_key: str = "") -> AlertEvent:
        event = AlertEvent(node_id=node_id, kind=kind, severity=severity, message=message, dedup_key=dedup_key)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
