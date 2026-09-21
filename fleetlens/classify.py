from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fleetlens.models import FleetReport, HostResult, Status, normalize_status

# Collector sections whose command return code is recorded. A non-zero code on a
# reachable host means the check could not run, so its "all clear" is not trustworthy:
# report it as a warning rather than silently as OK.
CHECK_RETURN_CODES = (
    ("apt", "apt", "apt_list_rc"),
    ("systemd", "systemd", "rc"),
    ("journal", "journal", "rc"),
)


def classify_host(host: HostResult) -> HostResult:
    criticals: list[str] = []
    warnings: list[str] = []

    # The collector already records why a host is unreachable; only add a generic reason.
    if not host.reachable and not host.errors:
        criticals.append("unreachable")
    if not host.sudo_ok:
        criticals.append("sudo failed")

    for filesystem in host.disk.get("filesystems", []):
        status = normalize_status(filesystem.get("status"))
        mount = filesystem.get("mount", filesystem.get("filesystem", "disk"))
        if status == Status.CRITICAL:
            criticals.append(f"{mount} disk critical")
        elif status == Status.WARNING:
            warnings.append(f"{mount} disk warning")

    if int(host.apt.get("upgradable_count") or 0) > 0:
        warnings.append("updates available")
    if host.reboot_required:
        warnings.append("reboot required")
    if int(host.systemd.get("failed_count") or 0) > 0:
        warnings.append("failed systemd units")
    if int(host.journal.get("error_count") or 0) > 0:
        warnings.append("journal errors")
    if host.reachable:
        warnings.extend(failed_check_notes(host))

    host.errors.extend(item for item in criticals if item not in host.errors)
    host.notes.extend(item for item in warnings if item not in host.notes)
    # Errors and notes supplied by the collector count as much as the ones derived here.
    if host.errors:
        host.status = Status.CRITICAL
    elif host.notes:
        host.status = Status.WARNING
    else:
        host.status = Status.OK
    return host


def failed_check_notes(host: HostResult) -> list[str]:
    notes = []
    for label, section, key in CHECK_RETURN_CODES:
        return_code = _int_or_none(getattr(host, section).get(key))
        if return_code:
            notes.append(f"{label} check failed (rc={return_code})")
    return notes


def classify_disk_usage(used_percent: int, warning: int = 85, critical: int = 95) -> Status:
    if used_percent >= critical:
        return Status.CRITICAL
    if used_percent >= warning:
        return Status.WARNING
    return Status.OK


def classify_fleet(hosts: list[HostResult]) -> FleetReport:
    if not hosts:
        return FleetReport(
            status=Status.UNKNOWN,
            generated_at=_now(),
            hosts=[],
            criticals=["no host results found"],
        )

    classified = [classify_host(host) for host in hosts]
    criticals = [
        f"{host.host}: {issue}" for host in classified for issue in host.errors if issue
    ]
    warnings = [f"{host.host}: {issue}" for host in classified for issue in host.notes if issue]

    if any(host.status == Status.CRITICAL for host in classified):
        status = Status.CRITICAL
    elif any(host.status == Status.WARNING for host in classified):
        status = Status.WARNING
    elif any(host.status == Status.UNKNOWN for host in classified):
        status = Status.UNKNOWN
    else:
        status = Status.OK

    return FleetReport(
        status=status,
        generated_at=_now(),
        hosts=classified,
        warnings=warnings,
        criticals=criticals,
    )


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
