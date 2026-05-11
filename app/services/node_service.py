import random
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.health import mtproto_handshake_probe, tcp_check
from app.infra.links import build_https_proxy_link, build_tg_proxy_link
from app.infra.providers import get_provider_adapter
from app.infra.security import decrypt_secret, encrypt_secret
from app.models import DomainPool, HealthCheckRun, Node, NodeStatus, RotationEvent
from app.repositories.node_repository import NodeRepository
from app.services.metrics import NODE_HANDSHAKE, NODE_ONLINE, NODE_RTT, NODE_SCORE, ROTATION_TOTAL


class NodeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NodeRepository(db)

    def create(self, payload) -> Node:
        if self.repo.get_by_name(payload.name):
            raise ValueError("Node name already exists")
        node = Node(
            name=payload.name,
            host=payload.host,
            port=payload.port,
            region=payload.region,
            country=payload.country,
            provider=payload.provider,
            asn=payload.asn,
            ee_domain=payload.ee_domain,
            secret_encrypted=encrypt_secret(payload.secret),
            upstream_socks5=payload.upstream_socks5,
            upstream_reality_tag=payload.upstream_reality_tag,
            status=NodeStatus.SCHEDULED.value,
        )
        return self.repo.save(node)

    def check_node(self, node: Node) -> dict:
        tcp_ok, rtt = tcp_check(node.host, node.port)
        handshake_ok = mtproto_handshake_probe(node.host, node.port) if tcp_ok else False
        node.is_online = bool(tcp_ok and handshake_ok)
        node.rtt_ms = rtt
        node.handshake_success_rate = 1.0 if handshake_ok else 0.0
        node.score = 100.0 if node.is_online else 10.0
        node.status = NodeStatus.ACTIVE.value if node.is_online else node.status
        self.db.add(HealthCheckRun(node_id=node.id, tcp_ok=tcp_ok, handshake_ok=handshake_ok, rtt_ms=rtt, packet_loss=0.0))
        self.db.commit()

        NODE_ONLINE.labels(node=node.name).set(1 if node.is_online else 0)
        NODE_RTT.labels(node=node.name).set(node.rtt_ms)
        NODE_HANDSHAKE.labels(node=node.name).set(1 if handshake_ok else 0)
        NODE_SCORE.labels(node=node.name).set(node.score)
        return {"tcp_ok": tcp_ok, "handshake_ok": handshake_ok, "rtt_ms": rtt}

    def rotate(self, node: Node, trigger_type: str = "manual") -> Node:
        old = node.status
        node.status = NodeStatus.SCHEDULED.value
        node.age_hours = 0
        # Keep existing secret unchanged. Truncating/mutating it breaks tg://proxy links.
        self.db.add(RotationEvent(node_id=node.id, trigger_type=trigger_type, old_status=old, new_status=node.status))
        self.db.commit()
        ROTATION_TOTAL.labels(trigger=trigger_type).inc()
        return node

    def restart(self, node: Node) -> str:
        adapter = get_provider_adapter(node.provider)
        result = adapter.restart_node(node.name)
        return result.message

    def random_proxy(self) -> dict:
        nodes = self.repo.healthy_nodes()
        if not nodes:
            raise ValueError("No healthy nodes")
        weighted = []
        for n in nodes:
            weight = max(1, int(n.score))
            weighted.extend([n] * min(weight, 100))
        selected = random.choice(weighted)
        secret = decrypt_secret(selected.secret_encrypted)
        return {
            "node": selected.name,
            "tg_link": build_tg_proxy_link(selected.host, selected.port, secret),
            "https_link": build_https_proxy_link(selected.host, selected.port, secret),
        }

    def set_status(self, node: Node, enabled: bool) -> Node:
        node.is_enabled = enabled
        if not enabled:
            node.status = NodeStatus.DRAINING.value
        self.db.commit()
        return node

    def update(self, node: Node, payload) -> Node:
        for field in ["ee_domain", "upstream_socks5", "upstream_reality_tag", "is_enabled"]:
            value = getattr(payload, field)
            if value is not None:
                setattr(node, field, value)
        self.db.commit()
        self.db.refresh(node)
        return node

    def list_domains(self):
        return self.db.scalars(select(DomainPool).order_by(DomainPool.id)).all()

    def add_domain(self, domain: str, region_hint: str):
        item = DomainPool(domain=domain, region_hint=region_hint)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def choose_domain(self, region: str) -> str | None:
        by_region = self.db.scalars(select(DomainPool).where(DomainPool.is_active.is_(True), DomainPool.region_hint == region)).all()
        pool = by_region or self.db.scalars(select(DomainPool).where(DomainPool.is_active.is_(True))).all()
        if not pool:
            return None
        return random.choice(pool).domain
