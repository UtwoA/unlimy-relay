from pydantic import BaseModel, Field


class NodeCreate(BaseModel):
    name: str
    host: str
    port: int = 443
    region: str = "unknown"
    provider: str = "unknown"
    asn: str = "unknown"
    ee_domain: str = ""
    secret: str = Field(min_length=8)


class NodeOut(BaseModel):
    id: int
    name: str
    host: str
    port: int
    region: str
    provider: str
    asn: str
    ee_domain: str
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
    age_hours: int

    class Config:
        from_attributes = True


class NodeStats(BaseModel):
    id: int
    is_online: bool
    rtt_ms: float
    packet_loss: float
    active_sessions: int
    bandwidth_mbps: float
    handshake_success_rate: float
    cpu_pct: float
    ram_pct: float
    traffic_rx_mb: float
    traffic_tx_mb: float
    age_hours: int


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
