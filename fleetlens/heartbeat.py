from __future__ import annotations

from urllib.error import URLError
from urllib.request import Request, urlopen

from fleetlens.config import Settings


def ping(url: str, body: str = "") -> bool:
    if not url:
        return False
    data = body.encode("utf-8") if body else None
    request = Request(url, data=data, method="POST" if data else "GET")
    try:
        with urlopen(request, timeout=15) as response:
            return 200 <= response.status < 300
    except URLError:
        return False


def heartbeat_start(settings: Settings) -> bool:
    return settings.heartbeat_enabled and ping(settings.heartbeat_start_url)


def heartbeat_success(settings: Settings) -> bool:
    return settings.heartbeat_enabled and ping(settings.heartbeat_success_url)


def heartbeat_failure(settings: Settings, message: str) -> bool:
    return settings.heartbeat_enabled and ping(settings.heartbeat_failure_url, message[:500])

