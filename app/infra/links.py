import io

import qrcode


def build_tg_proxy_link(host: str, port: int, secret: str) -> str:
    return f"tg://proxy?server={host}&port={port}&secret={secret}"


def build_https_proxy_link(host: str, port: int, secret: str) -> str:
    return f"https://t.me/proxy?server={host}&port={port}&secret={secret}"


def qr_png_bytes(content: str) -> bytes:
    image = qrcode.make(content)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()
