import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_auth
from app.db.session import get_db
from app.models.node import Node
from app.schemas.node import NodeCreate, NodeOut, NodeStats, TokenRequest, TokenResponse
from app.services.health import mtproto_handshake_probe, tcp_check
from app.services.metrics import HEALTH_CHECK_DURATION, NODE_HANDSHAKE, NODE_ONLINE, NODE_RTT, ROTATIONS
from app.services.security import build_tg_proxy_link, decrypt_secret, encrypt_secret, generate_jwt, verify_admin

router = APIRouter()


@router.post("/auth/token", response_model=TokenResponse)
def login(payload: TokenRequest):
    if not verify_admin(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = generate_jwt(payload.username)
    return TokenResponse(access_token=token)


@router.get("/nodes", response_model=list[NodeOut], dependencies=[Depends(require_auth)])
def list_nodes(db: Session = Depends(get_db)):
    return db.scalars(select(Node).order_by(Node.id)).all()


@router.post("/nodes", response_model=NodeOut, dependencies=[Depends(require_auth)])
def create_node(payload: NodeCreate, db: Session = Depends(get_db)):
    entity = Node(
        name=payload.name,
        host=payload.host,
        port=payload.port,
        region=payload.region,
        provider=payload.provider,
        asn=payload.asn,
        ee_domain=payload.ee_domain,
        secret_encrypted=encrypt_secret(payload.secret),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.delete("/nodes/{node_id}", dependencies=[Depends(require_auth)])
def delete_node(node_id: int, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    db.delete(node)
    db.commit()
    return {"ok": True}


@router.post("/nodes/{node_id}/rotate", dependencies=[Depends(require_auth)])
def rotate_node(node_id: int, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    secret = decrypt_secret(node.secret_encrypted)
    node.secret_encrypted = encrypt_secret(f"{secret[:8]}{random.randint(100000, 999999)}")
    node.created_at = datetime.utcnow()
    node.age_hours = 0
    db.commit()
    ROTATIONS.labels(node=node.name).inc()
    return {"ok": True, "node_id": node.id}


@router.post("/nodes/{node_id}/restart", dependencies=[Depends(require_auth)])
def restart_node(node_id: int, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"ok": True, "message": "Restart command accepted (wire provider/docker integration in stage 2)."}


@router.get("/proxy/random")
def random_proxy(db: Session = Depends(get_db)):
    nodes = db.scalars(select(Node).where(Node.is_enabled.is_(True), Node.is_online.is_(True))).all()
    if not nodes:
        raise HTTPException(status_code=503, detail="No healthy nodes")
    node = random.choice(nodes)
    secret = decrypt_secret(node.secret_encrypted)
    return {"node": node.name, "tg_link": build_tg_proxy_link(node.host, node.port, secret)}


@router.get("/proxy/alive")
def alive_proxy(db: Session = Depends(get_db)):
    nodes = db.scalars(select(Node).where(Node.is_enabled.is_(True), Node.is_online.is_(True))).all()
    output = []
    for n in nodes:
        output.append(
            {
                "node": n.name,
                "host": n.host,
                "port": n.port,
                "tg_link": build_tg_proxy_link(n.host, n.port, decrypt_secret(n.secret_encrypted)),
            }
        )
    return output


@router.get("/nodes/{node_id}/stats", response_model=NodeStats, dependencies=[Depends(require_auth)])
def node_stats(node_id: int, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return NodeStats(
        id=node.id,
        is_online=node.is_online,
        rtt_ms=node.rtt_ms,
        packet_loss=node.packet_loss,
        active_sessions=node.active_sessions,
        bandwidth_mbps=node.bandwidth_mbps,
        handshake_success_rate=node.handshake_success_rate,
        cpu_pct=node.cpu_pct,
        ram_pct=node.ram_pct,
        traffic_rx_mb=node.traffic_rx_mb,
        traffic_tx_mb=node.traffic_tx_mb,
        age_hours=node.age_hours,
    )


@router.post("/nodes/{node_id}/check", dependencies=[Depends(require_auth)])
def check_single_node(node_id: int, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    with HEALTH_CHECK_DURATION.time():
        tcp_ok, rtt = tcp_check(node.host, node.port)
        handshake_ok = mtproto_handshake_probe(node.host, node.port) if tcp_ok else False

    node.is_online = bool(tcp_ok and handshake_ok)
    node.rtt_ms = rtt
    node.handshake_success_rate = 1.0 if handshake_ok else 0.0
    db.commit()

    NODE_ONLINE.labels(node=node.name).set(1 if node.is_online else 0)
    NODE_RTT.labels(node=node.name).set(node.rtt_ms)
    NODE_HANDSHAKE.labels(node=node.name).set(1 if handshake_ok else 0)

    return {"node": node.name, "tcp_ok": tcp_ok, "handshake_ok": handshake_ok, "rtt_ms": rtt}
