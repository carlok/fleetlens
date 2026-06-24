from __future__ import annotations

import json
from pathlib import Path

from fleetlens.models import FleetReport, HostResult


def write_json_report(report: FleetReport, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
    target.write_text(payload, encoding="utf-8")


def write_markdown_report(report: FleetReport, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown(report), encoding="utf-8")


def render_markdown(report: FleetReport) -> str:
    lines = [
        "# FleetLens Report",
        "",
        f"Generated: {report.generated_at}",
        "",
        f"Global status: {report.status.value}",
        "",
        "## Summary",
        "",
        "| Host | Status | Reachable | Updates | Reboot | Failed Units | Disk | Notes |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for host in report.hosts:
        lines.append(_summary_row(host))
    lines.extend(["", "## Details", ""])
    for host in report.hosts:
        lines.extend(_host_detail(host))
    return "\n".join(lines).rstrip() + "\n"


def render_terminal_summary(report: FleetReport) -> str:
    lines = [f"FleetLens status: {report.status.value}"]
    problem_hosts = [
        host for host in report.hosts if host.errors or host.notes or host.status != "OK"
    ]
    if not problem_hosts:
        lines.append("All scanned hosts are OK.")
        return "\n".join(lines)

    lines.append("Attention needed:")
    for host in problem_hosts:
        lines.append(f"- {host.host}: {host.status.value}")
        for item in _host_terminal_findings(host):
            lines.append(f"  - {item}")
    return "\n".join(lines)


def _host_terminal_findings(host: HostResult) -> list[str]:
    findings: list[str] = []
    if host.errors:
        findings.extend(host.errors)

    upgradable_count = int(host.apt.get("upgradable_count") or 0)
    if upgradable_count:
        packages = _package_names(host.apt.get("packages") or [])
        package_text = f"{upgradable_count} package" + ("" if upgradable_count == 1 else "s")
        if packages:
            package_text += f": {', '.join(packages)}"
        findings.append(f"updates available: {package_text}")

    if host.reboot_required:
        findings.append("reboot required")

    failed_units = int(host.systemd.get("failed_count") or 0)
    if failed_units:
        findings.append(
            f"failed systemd units: {failed_units} unit" + ("" if failed_units == 1 else "s")
        )

    journal_errors = int(host.journal.get("error_count") or 0)
    if journal_errors:
        findings.append(
            f"journal errors: {journal_errors} line" + ("" if journal_errors == 1 else "s")
        )

    for filesystem in host.disk.get("filesystems", []):
        status = str(filesystem.get("status", "")).upper()
        if status not in {"WARNING", "CRITICAL"}:
            continue
        mount = filesystem.get("mount", filesystem.get("filesystem", "disk"))
        used = filesystem.get("used_percent", "unknown")
        findings.append(f"{mount} disk {status.lower()}: {used}% used")

    if not findings and host.notes:
        findings.extend(host.notes)
    return findings or ["status needs review"]


def _package_names(packages: list[str], limit: int = 5) -> list[str]:
    names = [str(package).split("/", 1)[0] for package in packages]
    if len(names) <= limit:
        return names
    return [*names[:limit], f"+{len(names) - limit} more"]


def _summary_row(host: HostResult) -> str:
    return (
        f"| {host.host} | {host.status.value} | {_yes_no(host.reachable)} | "
        f"{host.apt.get('upgradable_count', 'n/a')} | {_yes_no(host.reboot_required)} | "
        f"{host.systemd.get('failed_count', 'n/a')} | {_disk_summary(host)} | "
        f"{', '.join(host.notes + host.errors) or 'none'} |"
    )


def _host_detail(host: HostResult) -> list[str]:
    lines = [
        f"### {host.host}",
        "",
        f"- Reachable: {_yes_no(host.reachable)}",
        f"- OS: {host.os or 'unknown'}",
        f"- Kernel: {host.kernel or 'unknown'}",
        f"- Uptime: {host.uptime or 'unknown'}",
        f"- Load average: {host.load_average or 'unknown'}",
        f"- Memory: {_memory_summary(host)}",
        f"- Upgradable packages: {host.apt.get('upgradable_count', 'unknown')}",
        f"- Security updates: {host.apt.get('security_updates_count', 'unknown')}",
        f"- Reboot required: {_yes_no(host.reboot_required)}",
        f"- Failed systemd units: {host.systemd.get('failed_count', 'unknown')}",
    ]
    packages = host.apt.get("packages") or []
    if packages:
        lines.append("- Package updates:")
        for package in packages:
            lines.append(f"  - `{package}`")
    lines.append("- Disk:")
    filesystems = host.disk.get("filesystems") or []
    if not filesystems:
        lines.append("  - unknown")
    for filesystem in filesystems:
        mount = filesystem.get("mount", filesystem.get("filesystem", "unknown"))
        used = filesystem.get("used_percent", "unknown")
        status = filesystem.get("status", "UNKNOWN")
        lines.append(f"  - `{mount}`: {used}% {status}")
    if host.errors:
        lines.append(f"- Errors: {', '.join(host.errors)}")
    lines.append("")
    return lines


def _disk_summary(host: HostResult) -> str:
    statuses = {
        str(item.get("status", "UNKNOWN")).upper()
        for item in host.disk.get("filesystems", [])
    }
    if "CRITICAL" in statuses:
        return "critical"
    if "WARNING" in statuses:
        return "warning"
    if "OK" in statuses:
        return "ok"
    return "unknown"


def _memory_summary(host: HostResult) -> str:
    if not host.memory:
        return "unknown"
    used = host.memory.get("used_mb")
    total = host.memory.get("total_mb")
    if used is not None and total is not None:
        return f"{used}/{total} MB"
    return str(host.memory)


def _yes_no(value: bool | None) -> str:
    if value is None:
        return "n/a"
    return "yes" if value else "no"
