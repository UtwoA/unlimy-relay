import base64
from datetime import datetime, timezone
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import check_ip_allowlist, rate_limit_auth, require_roles
from app.db.session import get_db
from app.infra.links import build_https_proxy_link, build_tg_proxy_link, qr_png_bytes
from app.infra.security import decrypt_secret
from app.models import AlertEvent, AuditLog, Node, Role
from app.schemas.api import (
    AlertOut,
    AuditOut,
    DomainIn,
    DomainOut,
    NodeCreate,
    NodeOut,
    NodeStats,
    NodeUpdate,
    ProxyOut,
    ProxyWithQrOut,
    RotationRequest,
    TokenRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService
from app.services.metrics import ALERT_TOTAL, AUTH_ATTEMPTS
from app.services.node_service import NodeService
from app.workers.celery_app import celery_app

router = APIRouter(prefix="/api/v1", tags=["v1"])

_proxy_lock = Lock()
_proxy_cache: dict[str, dict] = {}
_proxy_rate: dict[str, list[datetime]] = {}
_PROXY_CACHE_SECONDS = 60
_PROXY_RATE_WINDOW_SECONDS = 60
_PROXY_RATE_MAX = 30


def _proxy_guard(client_ip: str):
    now = datetime.now(tz=timezone.utc)
    with _proxy_lock:
        attempts = _proxy_rate.setdefault(client_ip, [])
        attempts[:] = [x for x in attempts if (now - x).total_seconds() <= _PROXY_RATE_WINDOW_SECONDS]
        if len(attempts) >= _PROXY_RATE_MAX:
            raise HTTPException(status_code=429, detail="Too many proxy requests")
        attempts.append(now)

        cached = _proxy_cache.get(client_ip)
        if cached:
            age = (now - cached["at"]).total_seconds()
            if age <= _PROXY_CACHE_SECONDS:
                return cached["payload"]
        return None


def _proxy_store(client_ip: str, payload: dict):
    with _proxy_lock:
        _proxy_cache[client_ip] = {"at": datetime.now(tz=timezone.utc), "payload": payload}


@router.post("/auth/token", response_model=TokenResponse)
def login(payload: TokenRequest, request: Request, db: Session = Depends(get_db)):
    check_ip_allowlist(request)
    identity = request.client.host if request.client else "unknown"
    rate_limit_auth(identity)

    service = AuthService(db)
    try:
        token, role = service.login(payload.username, payload.password, payload.totp_code)
        AUTH_ATTEMPTS.labels(result="success").inc()
        service.audit(payload.username, "auth.login", "user", payload.username)
        return TokenResponse(access_token=token, role=role)
    except ValueError as exc:
        AUTH_ATTEMPTS.labels(result="failure").inc()
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/nodes", response_model=list[NodeOut])
def list_nodes(_: dict = Depends(require_roles(Role.VIEWER.value, Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    return db.scalars(select(Node).order_by(Node.id)).all()


@router.post("/nodes", response_model=NodeOut)
def create_node(payload: NodeCreate, auth: dict = Depends(require_roles(Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    service = NodeService(db)
    try:
        node = service.create(payload)
        AuthService(db).audit(auth["sub"], "nodes.create", "node", str(node.id), f"name={node.name}")
        return node
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/nodes/{node_id}", response_model=NodeOut)
def update_node(node_id: int, payload: NodeUpdate, auth: dict = Depends(require_roles(Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    updated = NodeService(db).update(node, payload)
    AuthService(db).audit(auth["sub"], "nodes.update", "node", str(node.id))
    return updated


@router.delete("/nodes/{node_id}")
def delete_node(node_id: int, auth: dict = Depends(require_roles(Role.ADMIN.value)), db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    db.delete(node)
    db.commit()
    AuthService(db).audit(auth["sub"], "nodes.delete", "node", str(node_id))
    return {"ok": True}


@router.post("/nodes/{node_id}/rotate")
def rotate_node(node_id: int, payload: RotationRequest, auth: dict = Depends(require_roles(Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    NodeService(db).rotate(node, payload.trigger_type)
    AuthService(db).audit(auth["sub"], "nodes.rotate", "node", str(node_id), payload.trigger_type)
    return {"ok": True}


@router.post("/nodes/{node_id}/restart")
def restart_node(node_id: int, auth: dict = Depends(require_roles(Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    message = NodeService(db).restart(node)
    AuthService(db).audit(auth["sub"], "nodes.restart", "node", str(node_id))
    return {"ok": True, "message": message}


@router.post("/nodes/{node_id}/enable")
def enable_node(node_id: int, auth: dict = Depends(require_roles(Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    NodeService(db).set_status(node, True)
    AuthService(db).audit(auth["sub"], "nodes.enable", "node", str(node_id))
    return {"ok": True}


@router.post("/nodes/{node_id}/disable")
def disable_node(node_id: int, auth: dict = Depends(require_roles(Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    NodeService(db).set_status(node, False)
    AuthService(db).audit(auth["sub"], "nodes.disable", "node", str(node_id))
    return {"ok": True}


@router.post("/nodes/{node_id}/check")
def check_node(node_id: int, _: dict = Depends(require_roles(Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return NodeService(db).check_node(node)


@router.get("/proxy/random", response_model=ProxyOut)
def proxy_random(request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    cached = _proxy_guard(client_ip)
    if cached:
        return cached
    try:
        payload = NodeService(db).random_proxy()
        _proxy_store(client_ip, payload)
        return payload
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/proxy/alive", response_model=list[ProxyOut])
def proxy_alive(db: Session = Depends(get_db)):
    nodes = NodeService(db).repo.healthy_nodes()
    result = []
    for n in nodes:
        secret = decrypt_secret(n.secret_encrypted)
        result.append(
            {
                "node": n.name,
                "tg_link": build_tg_proxy_link(n.host, n.port, secret),
                "https_link": build_https_proxy_link(n.host, n.port, secret),
            }
        )
    return result


@router.get("/proxy/random/qr", response_model=ProxyWithQrOut)
def proxy_random_qr(request: Request, db: Session = Depends(get_db)):
    proxy = proxy_random(request, db)
    qr = base64.b64encode(qr_png_bytes(proxy["tg_link"])).decode("utf-8")
    return ProxyWithQrOut(**proxy, qr_base64=qr)


@router.get("/nodes/{node_id}/stats", response_model=NodeStats)
def node_stats(node_id: int, _: dict = Depends(require_roles(Role.VIEWER.value, Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return NodeStats(id=node.id, is_online=node.is_online, rtt_ms=node.rtt_ms, packet_loss=node.packet_loss, handshake_success_rate=node.handshake_success_rate, score=node.score)


@router.get("/domains", response_model=list[DomainOut])
def list_domains(_: dict = Depends(require_roles(Role.VIEWER.value, Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    return NodeService(db).list_domains()


@router.post("/domains", response_model=DomainOut)
def add_domain(payload: DomainIn, auth: dict = Depends(require_roles(Role.ADMIN.value)), db: Session = Depends(get_db)):
    item = NodeService(db).add_domain(payload.domain, payload.region_hint)
    AuthService(db).audit(auth["sub"], "domains.create", "domain", str(item.id), payload.domain)
    return item


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(_: dict = Depends(require_roles(Role.VIEWER.value, Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    return db.scalars(select(AlertEvent).order_by(AlertEvent.id.desc()).limit(200)).all()


@router.get("/audit", response_model=list[AuditOut])
def list_audit(_: dict = Depends(require_roles(Role.ADMIN.value)), db: Session = Depends(get_db)):
    return db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(500)).all()


@router.post("/jobs/health/run")
def run_health_jobs(_: dict = Depends(require_roles(Role.OPERATOR.value, Role.ADMIN.value))):
    celery_app.send_task("app.workers.tasks.run_health_checks")
    return {"ok": True}


@router.post("/jobs/rotation/run")
def run_rotation_jobs(_: dict = Depends(require_roles(Role.OPERATOR.value, Role.ADMIN.value))):
    celery_app.send_task("app.workers.tasks.run_auto_rotation")
    return {"ok": True}


@router.get("/metrics/summary")
def metrics_summary(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Node))
    online = db.scalar(select(func.count()).select_from(Node).where(Node.is_online.is_(True)))
    return {"nodes_total": total or 0, "nodes_online": online or 0}


@router.post("/alerts/test")
def create_test_alert(_: dict = Depends(require_roles(Role.OPERATOR.value, Role.ADMIN.value)), db: Session = Depends(get_db)):
    alert = AlertEvent(node_id=None, kind="test", severity="info", message="Test alert", dedup_key="test")
    db.add(alert)
    db.commit()
    ALERT_TOTAL.labels(severity="info", kind="test").inc()
    return {"ok": True}
