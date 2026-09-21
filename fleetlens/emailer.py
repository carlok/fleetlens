from __future__ import annotations

import json
import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

from fleetlens.config import Settings
from fleetlens.models import FleetReport, Status


def should_send(report: FleetReport, settings: Settings) -> bool:
    return settings.email_enabled and status_wants_email(report, settings)


def status_wants_email(report: FleetReport, settings: Settings) -> bool:
    return {
        Status.OK: settings.email_send_on_ok,
        Status.WARNING: settings.email_send_on_warning,
        Status.CRITICAL: settings.email_send_on_critical,
        Status.UNKNOWN: True,
    }[report.status]


def build_subject(report: FleetReport, settings: Settings) -> str:
    host_part = f"{len(report.hosts)} host" + ("" if len(report.hosts) == 1 else "s")
    extras = []
    if report.warnings:
        warning_suffix = "" if len(report.warnings) == 1 else "s"
        extras.append(f"{len(report.warnings)} warning{warning_suffix}")
    if report.criticals:
        critical_suffix = "" if len(report.criticals) == 1 else "s"
        extras.append(f"{len(report.criticals)} critical{critical_suffix}")
    suffix = ", ".join([host_part, *extras])
    return f"{settings.email_subject_prefix} {report.status.value} - {suffix}"


def load_report(path: str | Path) -> FleetReport:
    from fleetlens.models import HostResult

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    hosts = [HostResult.from_mapping(item) for item in data.get("hosts", [])]
    return FleetReport(
        status=Status(data["status"]),
        generated_at=data["generated_at"],
        hosts=hosts,
        warnings=list(data.get("warnings", [])),
        criticals=list(data.get("criticals", [])),
    )


def build_message(
    report: FleetReport,
    settings: Settings,
    body: str,
    markdown_path: str | Path | None = None,
    json_path: str | Path | None = None,
) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = build_subject(report, settings)
    message["From"] = settings.email_from
    message["To"] = ", ".join(settings.email_to)
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain=settings.email_from.rsplit("@", 1)[-1])
    message.set_content(body)
    for path in [markdown_path, json_path]:
        if path:
            attach_path = Path(path)
            if attach_path.exists():
                message.add_attachment(
                    attach_path.read_bytes(),
                    maintype="application",
                    subtype="octet-stream",
                    filename=attach_path.name,
                )
    return message


def send_message(message: EmailMessage, settings: Settings) -> None:
    with smtplib.SMTP(settings.email_smtp_host, settings.email_smtp_port, timeout=30) as smtp:
        if settings.email_use_tls:
            smtp.starttls()
        if settings.email_smtp_username:
            smtp.login(settings.email_smtp_username, settings.email_smtp_password)
        smtp.send_message(message)
