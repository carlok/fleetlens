from __future__ import annotations

from urllib.request import Request, urlopen

from fleetlens.config import Settings


def ping(url: str, body: str = "") -> bool:
    if not url:
        return False
    data = body.encode("utf-8") if body else None
    try:
        request = Request(url, data=data, method="POST" if data else "GET")
        with urlopen(request, timeout=15) as response:
            return 200 <= response.status < 300
    # A heartbeat problem must never break the health run itself. URLError and
    # timeouts are OSError subclasses; malformed URLs raise ValueError.
    except (OSError, ValueError):
        return False


def heartbeat_start(settings: Settings) -> bool:
    return settings.heartbeat_enabled and ping(settings.heartbeat_start_url)


def heartbeat_success(settings: Settings) -> bool:
    return settings.heartbeat_enabled and ping(settings.heartbeat_success_url)


def heartbeat_failure(settings: Settings, message: str) -> bool:
    return settings.heartbeat_enabled and ping(settings.heartbeat_failure_url, message[:500])
