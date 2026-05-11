from datetime import datetime

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import AlertEvent, Node
from app.services.metrics import ALERT_TOTAL
from app.services.node_service import NodeService
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.run_health_checks")
def run_health_checks():
    db = SessionLocal()
    try:
        nodes = db.scalars(select(Node).where(Node.is_enabled.is_(True))).all()
        service = NodeService(db)
        for node in nodes:
            result = service.check_node(node)
            if not result["handshake_ok"]:
                event = AlertEvent(
                    node_id=node.id,
                    kind="handshake_failure",
                    severity="critical",
                    message=f"Node {node.name} failed handshake",
                    dedup_key=f"handshake:{node.id}",
                )
                db.add(event)
                ALERT_TOTAL.labels(severity="critical", kind="handshake_failure").inc()
        db.commit()
        return {"ok": True, "checked": len(nodes)}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.run_auto_rotation")
def run_auto_rotation():
    db = SessionLocal()
    rotated = 0
    try:
        nodes = db.scalars(select(Node).where(Node.is_enabled.is_(True))).all()
        service = NodeService(db)
        for node in nodes:
            node.age_hours = int((datetime.utcnow() - node.created_at).total_seconds() // 3600)
            if node.age_hours >= 72 or node.handshake_success_rate < 0.5 or node.detection_score > 80:
                service.rotate(node, "age" if node.age_hours >= 72 else "anomaly")
                rotated += 1
        db.commit()
        return {"ok": True, "rotated": rotated}
    finally:
        db.close()
