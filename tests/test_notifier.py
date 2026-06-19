import pytest

from fleetlens.config import Settings
from fleetlens.models import FleetReport, Status
from fleetlens.notifier import notify


def test_smtp_dry_run():
    report = FleetReport(status=Status.OK, generated_at="now", hosts=[])
    result = notify(report, Settings(notification_backend="smtp"), "body", dry_run=True)
    assert result.startswith("DRY RUN smtp")


def test_apprise_dry_run():
    report = FleetReport(status=Status.OK, generated_at="now", hosts=[])
    result = notify(
        report,
        Settings(notification_backend="apprise", apprise_urls=("ntfy://example/topic",)),
        "body",
        dry_run=True,
    )
    assert "1 url" in result


def test_unknown_backend_raises():
    report = FleetReport(status=Status.OK, generated_at="now", hosts=[])
    with pytest.raises(ValueError):
        notify(report, Settings(notification_backend="unknown"), "body", dry_run=True)
