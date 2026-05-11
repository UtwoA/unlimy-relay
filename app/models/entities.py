from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class NodeStatus(str, Enum):
    SCHEDULED = "scheduled"
    PROVISIONING = "provisioning"
    VALIDATING = "validating"
    ACTIVE = "active"
    DRAINING = "draining"
    RETIRED = "retired"


class Role(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default=Role.ADMIN.value)
    totp_secret: Mapped[str] = mapped_column(String(64), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=443)
    region: Mapped[str] = mapped_column(String(64), default="unknown")
    country: Mapped[str] = mapped_column(String(64), default="unknown")
    provider: Mapped[str] = mapped_column(String(64), default="unknown")
    asn: Mapped[str] = mapped_column(String(64), default="unknown")
    ee_domain: Mapped[str] = mapped_column(String(255), default="")
    secret_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    upstream_socks5: Mapped[str] = mapped_column(String(255), default="")
    upstream_reality_tag: Mapped[str] = mapped_column(String(128), default="")
    status: Mapped[str] = mapped_column(String(32), default=NodeStatus.SCHEDULED.value)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    uptime_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    rtt_ms: Mapped[float] = mapped_column(Float, default=0.0)
    packet_loss: Mapped[float] = mapped_column(Float, default=0.0)
    active_sessions: Mapped[int] = mapped_column(Integer, default=0)
    bandwidth_mbps: Mapped[float] = mapped_column(Float, default=0.0)
    handshake_success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    cpu_pct: Mapped[float] = mapped_column(Float, default=0.0)
    ram_pct: Mapped[float] = mapped_column(Float, default=0.0)
    traffic_rx_mb: Mapped[float] = mapped_column(Float, default=0.0)
    traffic_tx_mb: Mapped[float] = mapped_column(Float, default=0.0)
    detection_score: Mapped[float] = mapped_column(Float, default=0.0)
    score: Mapped[float] = mapped_column(Float, default=100.0)
    age_hours: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    health_checks: Mapped[list["HealthCheckRun"]] = relationship(back_populates="node", cascade="all,delete")


class HealthCheckRun(Base):
    __tablename__ = "health_check_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"), nullable=False)
    tcp_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    handshake_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    rtt_ms: Mapped[float] = mapped_column(Float, default=0.0)
    packet_loss: Mapped[float] = mapped_column(Float, default=0.0)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    node: Mapped[Node] = relationship(back_populates="health_checks")


class RotationEvent(Base):
    __tablename__ = "rotation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(32), default="manual")
    old_status: Mapped[str] = mapped_column(String(32), default=NodeStatus.ACTIVE.value)
    new_status: Mapped[str] = mapped_column(String(32), default=NodeStatus.SCHEDULED.value)
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"), nullable=True)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="warning")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    dedup_key: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    object_type: Mapped[str] = mapped_column(String(64), nullable=False)
    object_id: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DomainPool(Base):
    __tablename__ = "domain_pool"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    region_hint: Mapped[str] = mapped_column(String(64), default="global")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
