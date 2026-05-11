from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=443)
    region: Mapped[str] = mapped_column(String(64), default="unknown")
    provider: Mapped[str] = mapped_column(String(64), default="unknown")
    asn: Mapped[str] = mapped_column(String(64), default="unknown")
    ee_domain: Mapped[str] = mapped_column(String(255), default="")
    secret_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
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
    age_hours: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
