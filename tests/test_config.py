from fleetlens.config import env_bool, env_list, load_env_file, load_settings


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


def test_load_env_file_sets_missing_values(tmp_path, monkeypatch):
    monkeypatch.delenv("FLEETLENS_INVENTORY", raising=False)
    monkeypatch.delenv("FLEETLENS_EMAIL_TO", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "FLEETLENS_INVENTORY=from-file.ini\n"
        "FLEETLENS_EMAIL_TO='ops@example.com, admin@example.com'\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("FLEETLENS_ENV_FILE", str(env_file))

    settings = load_settings()

    assert settings.inventory == "from-file.ini"
    assert settings.email_to == ("ops@example.com", "admin@example.com")
    monkeypatch.delenv("FLEETLENS_INVENTORY", raising=False)
    monkeypatch.delenv("FLEETLENS_EMAIL_TO", raising=False)


def test_load_env_file_preserves_existing_environment(tmp_path, monkeypatch):
    monkeypatch.delenv("FLEETLENS_EMAIL_TO", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("FLEETLENS_INVENTORY=from-file.ini\n", encoding="utf-8")
    monkeypatch.setenv("FLEETLENS_INVENTORY", "from-env.ini")

    load_env_file(env_file)

    assert load_settings().inventory == "from-env.ini"
