from fleetlens.config import Settings
from fleetlens.heartbeat import heartbeat_failure, heartbeat_start, heartbeat_success, ping


def test_heartbeat_disabled_returns_false():
    assert heartbeat_start(Settings(heartbeat_enabled=False)) is False


def test_ping_empty_url_returns_false():
    assert ping("") is False


def test_heartbeat_uses_configured_urls(monkeypatch):
    calls = []

    def fake_ping(url, body=""):
        calls.append((url, body))
        return True

    monkeypatch.setattr("fleetlens.heartbeat.ping", fake_ping)
    settings = Settings(
        heartbeat_enabled=True,
        heartbeat_start_url="https://hc/start",
        heartbeat_success_url="https://hc/success",
        heartbeat_failure_url="https://hc/failure",
    )
    assert heartbeat_start(settings) is True
    assert heartbeat_success(settings) is True
    assert heartbeat_failure(settings, "failed") is True
    assert calls == [
        ("https://hc/start", ""),
        ("https://hc/success", ""),
        ("https://hc/failure", "failed"),
    ]


def test_ping_swallows_timeouts_and_bad_urls(monkeypatch):
    def timeout(*args, **kwargs):
        raise TimeoutError("read timed out")

    monkeypatch.setattr("fleetlens.heartbeat.urlopen", timeout)
    assert ping("https://hc/start") is False
    assert ping("not a url") is False
