from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    username: str
    password: str
    totp_code: str = Field(min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class NodeCreate(BaseModel):
    name: str
    host: str
    port: int = 443
    region: str = "unknown"
    country: str = "unknown"
    provider: str = "unknown"
    asn: str = "unknown"
    ee_domain: str = ""
    secret: str = Field(min_length=8)
    upstream_socks5: str = ""
    upstream_reality_tag: str = ""


class NodeUpdate(BaseModel):
    ee_domain: str | None = None
    upstream_socks5: str | None = None
    upstream_reality_tag: str | None = None
    is_enabled: bool | None = None


class NodeOut(BaseModel):
    id: int
    name: str
    host: str
    port: int
    region: str
    country: str
    provider: str
    asn: str
    ee_domain: str
    upstream_socks5: str
    upstream_reality_tag: str
    status: str
    is_enabled: bool
    is_online: bool
    uptime_ratio: float
    rtt_ms: float
    packet_loss: float
    active_sessions: int
    bandwidth_mbps: float
    handshake_success_rate: float
    cpu_pct: float
    ram_pct: float
    traffic_rx_mb: float
    traffic_tx_mb: float
    detection_score: float
    score: float
    age_hours: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProxyOut(BaseModel):
    node: str
    tg_link: str
    https_link: str


class ProxyWithQrOut(ProxyOut):
    qr_base64: str


class NodeStats(BaseModel):
    id: int
    is_online: bool
    rtt_ms: float
    packet_loss: float
    handshake_success_rate: float
    score: float


class RotationRequest(BaseModel):
    trigger_type: Literal["manual", "age", "success_rate", "anomaly"] = "manual"


class DomainIn(BaseModel):
    domain: str
    region_hint: str = "global"


class DomainOut(BaseModel):
    id: int
    domain: str
    region_hint: str
    is_active: bool

    class Config:
        from_attributes = True


class AuditOut(BaseModel):
    id: int
    actor: str
    action: str
    object_type: str
    object_id: str
    details: str
    created_at: datetime

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    id: int
    node_id: int | None
    kind: str
    severity: str
    message: str
    dedup_key: str
    created_at: datetime

    class Config:
        from_attributes = True


class OverviewKpiOut(BaseModel):
    nodes_total: int
    nodes_online: int
    nodes_offline: int
    nodes_draining: int
    avg_rtt_ms: float
    avg_handshake_rate: float
    active_alerts_count: int


class OverviewProblemNodeOut(BaseModel):
    id: int
    name: str
    status: str
    region: str
    provider: str
    is_online: bool
    is_enabled: bool
    rtt_ms: float
    handshake_success_rate: float
    score: float
    age_hours: int

    class Config:
        from_attributes = True


class OverviewTrendPointOut(BaseModel):
    hour: str
    online_ratio: float
    avg_rtt_ms: float
    handshake_ok_ratio: float


class AdminOverviewOut(BaseModel):
    kpi: OverviewKpiOut
    problem_nodes: list[OverviewProblemNodeOut]
    recent_alerts: list[AlertOut]
    recent_audit: list[AuditOut]
    trends_24h: list[OverviewTrendPointOut]
