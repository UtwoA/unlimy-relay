import os

import httpx
from fastapi import FastAPI, HTTPException, Request

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
MASTER_API_URL = os.getenv("MASTER_API_URL", "http://master-api:8080/api/v1")
MASTER_API_TOKEN = os.getenv("MASTER_API_TOKEN", "")

app = FastAPI(title="Unlimy Relay Bot Service")


def command_text(payload: dict) -> str:
    message = payload.get("message") or {}
    return (message.get("text") or "").strip()


def chat_id(payload: dict) -> int | None:
    message = payload.get("message") or {}
    chat = message.get("chat") or {}
    return chat.get("id")


async def tg_send(chat: int, text: str):
    if not BOT_TOKEN:
        return
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat, "text": text},
        )


async def api_get(path: str):
    headers = {"Authorization": f"Bearer {MASTER_API_TOKEN}"} if MASTER_API_TOKEN else {}
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{MASTER_API_URL}{path}", headers=headers)
        response.raise_for_status()
        return response.json()


async def api_post(path: str, body: dict | None = None):
    headers = {"Authorization": f"Bearer {MASTER_API_TOKEN}"} if MASTER_API_TOKEN else {}
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(f"{MASTER_API_URL}{path}", json=body or {}, headers=headers)
        response.raise_for_status()
        return response.json()


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    payload = await request.json()
    text = command_text(payload)
    cid = chat_id(payload)
    if not cid:
        return {"ok": True}

    try:
        if text == "/status":
            nodes = await api_get("/nodes")
            online = sum(1 for n in nodes if n.get("is_online"))
            await tg_send(cid, f"Nodes: {online}/{len(nodes)} online")
        elif text == "/proxy":
            proxy = await api_get("/proxy/random")
            await tg_send(cid, f"{proxy['tg_link']}")
        elif text.startswith("/rotate"):
            parts = text.split()
            if len(parts) < 2:
                await tg_send(cid, "Usage: /rotate <node_id>")
            else:
                node_id = int(parts[1])
                await api_post(f"/nodes/{node_id}/rotate", {"trigger_type": "manual"})
                await tg_send(cid, f"Node {node_id} rotation requested")
        elif text == "/alerts":
            alerts = await api_get("/alerts")
            latest = alerts[:5]
            lines = [f"{a['severity']}: {a['message']}" for a in latest] or ["No alerts"]
            await tg_send(cid, "\n".join(lines))
        else:
            await tg_send(cid, "Commands: /status /proxy /rotate <id> /alerts")
    except Exception as exc:
        await tg_send(cid, f"Command failed: {exc}")
    return {"ok": True}


@app.get("/healthz")
def healthz():
    return {"ok": True}
