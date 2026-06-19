from __future__ import annotations

from fleetlens.config import Settings
from fleetlens.emailer import build_message, send_message
from fleetlens.models import FleetReport


def notify(report: FleetReport, settings: Settings, body: str, dry_run: bool = False) -> str:
    backend = settings.notification_backend.lower()
    if backend == "smtp":
        message = build_message(report, settings, body)
        if dry_run:
            return f"DRY RUN smtp to {', '.join(settings.email_to)} subject {message['Subject']}"
        send_message(message, settings)
        return "sent smtp notification"
    if backend == "apprise":
        if dry_run:
            return f"DRY RUN apprise to {len(settings.apprise_urls)} url(s)"
        return _notify_apprise(report, settings, body)
    raise ValueError(f"unsupported notification backend: {settings.notification_backend}")


def _notify_apprise(report: FleetReport, settings: Settings, body: str) -> str:
    try:
        import apprise
    except ImportError as exc:
        raise RuntimeError("apprise backend requested but apprise is not installed") from exc
    client = apprise.Apprise()
    for url in settings.apprise_urls:
        client.add(url)
    ok = client.notify(title=f"FleetLens {report.status.value}", body=body)
    if not ok:
        raise RuntimeError("apprise notification failed")
    return "sent apprise notification"

