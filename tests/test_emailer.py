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
    message = build_message(report(), Settings(email_to=("a@example.com", "b@example.com")), "body")
    assert message["To"] == "a@example.com, b@example.com"
    assert message.get_content().strip() == "body"
