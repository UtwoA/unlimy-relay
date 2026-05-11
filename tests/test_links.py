from app.infra.links import build_https_proxy_link, build_tg_proxy_link


def test_link_generation():
    tg = build_tg_proxy_link("1.1.1.1", 443, "ee123")
    https = build_https_proxy_link("1.1.1.1", 443, "ee123")
    assert tg.startswith("tg://proxy")
    assert https.startswith("https://t.me/proxy")
