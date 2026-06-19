from __future__ import annotations

from datetime import UTC, datetime

from fleetlens.models import FleetReport, HostResult, Status


def classify_host(host: HostResult) -> HostResult:
    criticals: list[str] = []
    warnings: list[str] = []

    if not host.reachable:
        criticals.append("unreachable")
    if not host.sudo_ok:
        criticals.append("sudo failed")

    for filesystem in host.disk.get("filesystems", []):
        status = str(filesystem.get("status", "")).upper()
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

    host.errors.extend(item for item in criticals if item not in host.errors)
    host.notes.extend(item for item in warnings if item not in host.notes)
    if criticals:
        host.status = Status.CRITICAL
    elif warnings:
        host.status = Status.WARNING
    else:
        host.status = Status.OK
    return host


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


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
