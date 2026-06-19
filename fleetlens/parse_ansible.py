from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fleetlens.models import HostResult


def parse_apt_upgradable(output: str) -> tuple[int, int]:
    count = 0
    security_count = 0
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("Listing..."):
            continue
        if "/" not in line:
            continue
        count += 1
        if "security" in line.lower():
            security_count += 1
    return count, security_count


def load_raw_report(path: str | Path) -> list[HostResult]:
    with Path(path).open(encoding="utf-8") as handle:
        return parse_raw_report(json.load(handle))


def parse_raw_report(raw: Any) -> list[HostResult]:
    if isinstance(raw, list):
        return [HostResult.from_mapping(item) for item in raw]
    if isinstance(raw, dict):
        if isinstance(raw.get("hosts"), list):
            return [HostResult.from_mapping(item) for item in raw["hosts"]]
        fleetlens = raw.get("fleetlens")
        if isinstance(fleetlens, dict) and isinstance(fleetlens.get("hosts"), list):
            return [HostResult.from_mapping(item) for item in raw["fleetlens"]["hosts"]]
        callback_hosts = _parse_ansible_callback(raw)
        if callback_hosts:
            return callback_hosts
    raise ValueError("raw report does not contain FleetLens host results")


def _parse_ansible_callback(raw: dict[str, Any]) -> list[HostResult]:
    stats = raw.get("stats")
    if not isinstance(stats, dict):
        return []
    hosts: list[HostResult] = []
    for host, values in stats.items():
        failures = int(values.get("failures", 0))
        unreachable = int(values.get("unreachable", 0))
        hosts.append(
            HostResult(
                host=host,
                reachable=unreachable == 0,
                sudo_ok=failures == 0,
                errors=[] if unreachable == 0 else ["host unreachable"],
            )
        )
    return hosts
