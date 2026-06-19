from fleetlens.config import env_bool, env_list, load_settings


def test_env_bool(monkeypatch):
    monkeypatch.setenv("X_BOOL", "true")
    assert env_bool("X_BOOL") is True


def test_env_list(monkeypatch):
    monkeypatch.setenv("X_LIST", "a@example.com, b@example.com")
    assert env_list("X_LIST") == ["a@example.com", "b@example.com"]


def test_load_settings_from_environment(monkeypatch):
    monkeypatch.setenv("FLEETLENS_INVENTORY", "local.ini")
    monkeypatch.setenv("FLEETLENS_EMAIL_TO", "ops@example.com")
    settings = load_settings()
    assert settings.inventory == "local.ini"
    assert settings.email_to == ("ops@example.com",)

