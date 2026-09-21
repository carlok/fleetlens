import os

import pytest


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch, tmp_path):
    """Keep a developer's local .env and FLEETLENS_* variables out of the tests."""
    for name in list(os.environ):
        if name.startswith("FLEETLENS_"):
            monkeypatch.delenv(name)
    monkeypatch.setenv("FLEETLENS_ENV_FILE", str(tmp_path / "no-such.env"))
