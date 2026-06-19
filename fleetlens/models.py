from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Status(StrEnum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


@dataclass(slots=True)
class HostResult:
    host: str
    reachable: bool = True
    sudo_ok: bool = True
    status: Status = Status.UNKNOWN
    hostname: str | None = None
    os: str | None = None
    kernel: str | None = None
    uptime: str | None = None
    load_average: str | None = None
    memory: dict[str, Any] = field(default_factory=dict)
    disk: dict[str, Any] = field(default_factory=dict)
    apt: dict[str, Any] = field(default_factory=dict)
    reboot_required: bool | None = None
    systemd: dict[str, Any] = field(default_factory=dict)
    journal: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    collected_at: str | None = None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> HostResult:
        return cls(
            host=str(value.get("host") or value.get("inventory_hostname") or "unknown"),
            reachable=bool(value.get("reachable", True)),
            sudo_ok=bool(value.get("sudo_ok", value.get("become_ok", True))),
            hostname=value.get("hostname"),
            os=value.get("os"),
            kernel=value.get("kernel"),
            uptime=value.get("uptime"),
            load_average=value.get("load_average"),
            memory=dict(value.get("memory") or {}),
            disk=dict(value.get("disk") or {}),
            apt=dict(value.get("apt") or {}),
            reboot_required=value.get("reboot_required"),
            systemd=dict(value.get("systemd") or {}),
            journal=dict(value.get("journal") or {}),
            notes=list(value.get("notes") or []),
            errors=list(value.get("errors") or []),
            collected_at=value.get("collected_at"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "reachable": self.reachable,
            "sudo_ok": self.sudo_ok,
            "status": self.status.value,
            "hostname": self.hostname,
            "os": self.os,
            "kernel": self.kernel,
            "uptime": self.uptime,
            "load_average": self.load_average,
            "memory": self.memory,
            "disk": self.disk,
            "apt": self.apt,
            "reboot_required": self.reboot_required,
            "systemd": self.systemd,
            "journal": self.journal,
            "notes": self.notes,
            "errors": self.errors,
            "collected_at": self.collected_at,
        }


@dataclass(slots=True)
class FleetReport:
    status: Status
    generated_at: str
    hosts: list[HostResult]
    warnings: list[str] = field(default_factory=list)
    criticals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "generated_at": self.generated_at,
            "summary": {
                "host_count": len(self.hosts),
                "warning_count": len(self.warnings),
                "critical_count": len(self.criticals),
            },
            "warnings": self.warnings,
            "criticals": self.criticals,
            "hosts": [host.to_dict() for host in self.hosts],
        }

