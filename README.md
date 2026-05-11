# Unlimy Relay

![Unlimy Relay Hero](assets/branding/hero-banner-1.png)

![FastAPI](https://img.shields.io/badge/FastAPI-0EA5A8?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-111826?style=for-the-badge&logo=next.js&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Telegram Proxy](https://img.shields.io/badge/Telegram_Proxy-1F9BFF?style=for-the-badge&logo=telegram&logoColor=white)

Unlimy Relay — production-grade платформа для отказоустойчивой Telegram fallback-инфраструктуры.

Система объединяет безопасный control plane, удобную операционную панель и публичную выдачу конфигов в одном контуре: быстро разворачивается, просто поддерживается и устойчива в проде.

## Зачем этот проект

Большинство proxy-решений ломаются не на демо, а в реальной эксплуатации:
- нет полного lifecycle-управления нодами,
- слабая наблюдаемость,
- ручная и медленная реакция на инциденты,
- размытые security-границы,
- слабый UX для оператора.

Unlimy Relay закрывает эти проблемы за счет архитектуры, заточенной под реальный ops-поток.

## Ключевые возможности

- Lifecycle нод: create, update, enable/disable, check, rotate, restart, delete
- Публичная выдача прокси: random healthy proxy + QR
- Защищенный админ-контур: JWT + RBAC + TOTP
- Операционная автоматизация: health checks, планировщик задач, rotation jobs
- Аудит действий операторов/админов
- Антиабуз: rate limit + cooldown/cache для публичной выдачи
- Операционный дашборд: KPI, проблемные ноды, последние алерты/аудит, тренды за 24ч

## Архитектура

- `master-api` (FastAPI)
  - `/api/v1` control/data plane
  - auth, RBAC, audit, orchestration нод, выдача proxy
- `web` (Next.js)
  - public: `/config`
  - admin: `/admin/*`
- `worker` + `beat` (Celery)
  - фоновые проверки и ротации
- `postgres` + `redis`
  - состояние и очередь
- `prometheus` + `grafana`
  - метрики и мониторинг
- `bot-service`
  - Telegram automation/webhook (опционально)

## Модель безопасности

- Аутентификация: JWT
- 2FA: TOTP для входа администратора
- Авторизация: роли `viewer`, `operator`, `admin`
- Public boundary: наружу только безопасные proxy-endpoints
- Admin boundary: `/nodes`, `/jobs`, `/alerts`, `/audit` только с токеном
- Инфраструктурный hardening: fail2ban, firewall, DNS-over-TLS, sysctl tuning

## Маршрутизация Public/Admin

Рекомендуемая стратегия: один домен, разные пути.

- Public UX: `/config`
- Admin UX: `/admin/login`, `/admin`, `/admin/nodes`, `/admin/alerts`, `/admin/audit`

Такой split сохраняет простой onboarding для пользователей и жесткие границы доступа для админки.

## Основные API

Публичные:
- `GET /api/v1/proxy/random`
- `GET /api/v1/proxy/random/qr`
- `GET /api/v1/proxy/public-status`

Админские (требуют авторизацию):
- `POST /api/v1/auth/token`
- `GET /api/v1/nodes`
- `PATCH /api/v1/nodes/{id}`
- `POST /api/v1/nodes/{id}/check|rotate|restart|enable|disable`
- `POST /api/v1/jobs/health/run`
- `POST /api/v1/jobs/rotation/run`
- `GET /api/v1/admin/overview`
- `GET /api/v1/alerts`
- `GET /api/v1/audit`

## Быстрый старт (dev)

1. Создать env-файл:
```bash
cp .env.example .env
```

2. Заполнить обязательные переменные в `.env`:
- `JWT_SECRET`
- `ADMIN_USER`, `ADMIN_PASSWORD`, `ADMIN_TOTP_SECRET`
- `TELEGRAM_BOT_TOKEN` (опционально, если используется bot)

3. Запуск:
```bash
docker compose up -d --build
```

## Прод-запуск

```bash
docker compose -p relay -f docker-compose.prod.yml up -d --build
```

## Порты (prod compose)

- Web: `13000`
- API: `18080`
- Bot service: `18090`
- Prometheus: `19090`
- Grafana: `13001`

## Операционные принципы

- Явный audit trail для критичных действий
- Минимальный и безопасный публичный payload
- Fail-safe поведение при деградации healthy-пула
- Максимальная скорость оператора без утечки внутренних данных
- Маленькие PR с четкой зоной ответственности

## Roadmap

- углубление качества node-scoring и маршрутизации
- расширенный policy engine
- адаптивный антиабуз
- дальнейшее развитие админ-дашборда
- усиление секрет-менеджмента (KMS/Vault)

## Стандарт качества

Unlimy Relay строится с приоритетом production-практик:
- secure-by-default,
- прозрачная эксплуатация,
- автоматизация рутинных операций,
- строгая граница между public и admin контурами.

Если вам нужен надежный фундамент для Telegram fallback-инфраструктуры, этот проект создан именно для этого.
