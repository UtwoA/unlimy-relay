from prometheus_client import Counter, Gauge, Histogram

NODE_ONLINE = Gauge("unlimy_node_online", "Node online state", ["node"])
NODE_RTT = Gauge("unlimy_node_rtt_ms", "Node RTT", ["node"])
NODE_HANDSHAKE = Gauge("unlimy_node_handshake_ok", "Handshake status", ["node"])
NODE_SCORE = Gauge("unlimy_node_score", "Node health score", ["node"])
HEALTH_CHECK_DURATION = Histogram("unlimy_healthcheck_duration_seconds", "Health check duration")
ROTATION_TOTAL = Counter("unlimy_node_rotation_total", "Node rotations", ["trigger"])
AUTH_ATTEMPTS = Counter("unlimy_auth_attempts_total", "Auth attempts", ["result"])
ALERT_TOTAL = Counter("unlimy_alert_total", "Alert events", ["severity", "kind"])
