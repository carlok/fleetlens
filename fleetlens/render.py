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
