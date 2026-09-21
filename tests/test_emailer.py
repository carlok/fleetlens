from fleetlens.config import Settings
from fleetlens.emailer import build_message, build_subject, should_send
from fleetlens.models import FleetReport, HostResult, Status


def report(status=Status.WARNING):
    return FleetReport(
        status=status,
        generated_at="2026-06-19T12:00:00Z",
        hosts=[HostResult(host="vm1")],
        warnings=["vm1: updates"],
    )


def test_subject_includes_status_and_counts():
    assert build_subject(report(), Settings()) == "[FleetLens] WARNING - 1 host, 1 warning"


def test_should_send_honors_enabled_flag():
    assert should_send(report(), Settings(email_enabled=False)) is False
    assert should_send(report(), Settings(email_enabled=True)) is True


def test_build_message_has_recipients():
    message = build_message(
        report(),
        Settings(email_from="fleetlens@example.com", email_to=("a@example.com", "b@example.com")),
        "body",
    )
    assert message["To"] == "a@example.com, b@example.com"
    assert message["Date"]
    assert message["Message-ID"].endswith("@example.com>")
    assert message.get_content().strip() == "body"


def test_should_send_honors_status_toggles():
    settings = Settings(email_enabled=True)
    assert should_send(report(Status.OK), settings) is False
    assert should_send(report(Status.CRITICAL), settings) is True
    assert should_send(report(Status.OK), Settings(email_enabled=True, email_send_on_ok=True))
    quiet = Settings(email_enabled=True, email_send_on_warning=False)
    assert should_send(report(Status.WARNING), quiet) is False


def test_load_report_keeps_host_status(tmp_path):
    import json

    from fleetlens.emailer import load_report

    path = tmp_path / "latest.json"
    path.write_text(json.dumps(report(Status.WARNING).to_dict()), encoding="utf-8")
    loaded = load_report(path)
    assert loaded.status == Status.WARNING
    assert loaded.hosts[0].status == Status.UNKNOWN  # report() host is never classified
    classified = report(Status.WARNING)
    classified.hosts[0].status = Status.WARNING
    path.write_text(json.dumps(classified.to_dict()), encoding="utf-8")
    assert load_report(path).hosts[0].status == Status.WARNING
