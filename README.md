# Unlimy Relay

Production-oriented Telegram fallback infrastructure:
- `master-api` (FastAPI, `/api/v1`)
- `web` panel (Next.js)
- `bot-service` (Telegram webhook)
- `worker + beat` (Celery pipelines)
- `postgres + redis + prometheus + grafana`

## Implemented

- Node lifecycle: create/update/delete/enable/disable/restart/rotate/check
- Proxy distribution: `/proxy/random`, `/proxy/alive`, QR generation
- Health checks: TCP + MTProto-like handshake probe
- Auto rotation signals: age/success-rate/detection-score
- Auth/security: JWT + RBAC + TOTP, IP allowlist option, auth rate limit
- Audit log for admin/operator actions
- Domain pool model for EE domain strategy
- Telegram bot commands: `/status`, `/proxy`, `/rotate <id>`, `/alerts`

## API Base

- `http://localhost:8080/api/v1`
- Swagger: `http://localhost:8080/docs`

## Start

1. Copy env:
```bash
cp .env.example .env
```
2. Set required values in `.env`:
- `JWT_SECRET`
- `ADMIN_USER`, `ADMIN_PASSWORD`, `ADMIN_TOTP_SECRET`
- `TELEGRAM_BOT_TOKEN` (for bot)
3. Run:
```bash
docker compose up -d --build
```

## Services

- API: `:8080`
- Web panel: `:3000`
- Bot webhook service: `:8090`
- Prometheus: `:9090`
- Grafana: `:3001`

## TOTP note

Admin login requires a 6-digit TOTP for `ADMIN_TOTP_SECRET`.
Default demo secret in `.env.example` is `JBSWY3DPEHPK3PXP`.

## Security note

Secret storage currently uses base64 obfuscation (temporary mode).
Before production launch, replace with real encryption (Vault/KMS/libsodium).
