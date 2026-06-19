from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_INVENTORY = "ansible/inventories/example/hosts.ini"
DEFAULT_RAW_REPORT = "reports/raw-ansible.json"
DEFAULT_JSON_REPORT = "reports/latest.json"
DEFAULT_MARKDOWN_REPORT = "reports/latest.md"
DEFAULT_SMTP_PORT = 587


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip() for item in value.replace(";", ",").split(",") if item.strip()]


@dataclass(frozen=True, slots=True)
class Settings:
    inventory: str = DEFAULT_INVENTORY
    raw_report: str = DEFAULT_RAW_REPORT
    json_report: str = DEFAULT_JSON_REPORT
    markdown_report: str = DEFAULT_MARKDOWN_REPORT
    runner_backend: str = "shell"
    email_enabled: bool = False
    email_smtp_host: str = "smtp.example.com"
    email_smtp_port: int = DEFAULT_SMTP_PORT
    email_smtp_username: str = ""
    email_smtp_password: str = ""
    email_from: str = "fleetlens@example.com"
    email_to: tuple[str, ...] = ("admin@example.com",)
    email_use_tls: bool = True
    email_subject_prefix: str = "[FleetLens]"
    email_send_on_ok: bool = False
    email_send_on_warning: bool = True
    email_send_on_critical: bool = True
    notification_backend: str = "smtp"
    apprise_urls: tuple[str, ...] = ()
    heartbeat_enabled: bool = False
    heartbeat_start_url: str = ""
    heartbeat_success_url: str = ""
    heartbeat_failure_url: str = ""


def load_settings() -> Settings:
    return Settings(
        inventory=os.getenv("FLEETLENS_INVENTORY", DEFAULT_INVENTORY),
        raw_report=os.getenv("FLEETLENS_RAW_REPORT", DEFAULT_RAW_REPORT),
        json_report=os.getenv("FLEETLENS_JSON_REPORT", DEFAULT_JSON_REPORT),
        markdown_report=os.getenv("FLEETLENS_MARKDOWN_REPORT", DEFAULT_MARKDOWN_REPORT),
        runner_backend=os.getenv("FLEETLENS_RUNNER_BACKEND", "shell"),
        email_enabled=env_bool("FLEETLENS_EMAIL_ENABLED", False),
        email_smtp_host=os.getenv("FLEETLENS_EMAIL_SMTP_HOST", "smtp.example.com"),
        email_smtp_port=int(os.getenv("FLEETLENS_EMAIL_SMTP_PORT", str(DEFAULT_SMTP_PORT))),
        email_smtp_username=os.getenv("FLEETLENS_EMAIL_SMTP_USERNAME", ""),
        email_smtp_password=os.getenv("FLEETLENS_EMAIL_SMTP_PASSWORD", ""),
        email_from=os.getenv("FLEETLENS_EMAIL_FROM", "fleetlens@example.com"),
        email_to=tuple(env_list("FLEETLENS_EMAIL_TO") or ("admin@example.com",)),
        email_use_tls=env_bool("FLEETLENS_EMAIL_USE_TLS", True),
        email_subject_prefix=os.getenv("FLEETLENS_EMAIL_SUBJECT_PREFIX", "[FleetLens]"),
        email_send_on_ok=env_bool("FLEETLENS_EMAIL_SEND_ON_OK", False),
        email_send_on_warning=env_bool("FLEETLENS_EMAIL_SEND_ON_WARNING", True),
        email_send_on_critical=env_bool("FLEETLENS_EMAIL_SEND_ON_CRITICAL", True),
        notification_backend=os.getenv("FLEETLENS_NOTIFICATION_BACKEND", "smtp"),
        apprise_urls=tuple(env_list("FLEETLENS_APPRISE_URLS")),
        heartbeat_enabled=env_bool("FLEETLENS_HEARTBEAT_ENABLED", False),
        heartbeat_start_url=os.getenv("FLEETLENS_HEARTBEAT_START_URL", ""),
        heartbeat_success_url=os.getenv("FLEETLENS_HEARTBEAT_SUCCESS_URL", ""),
        heartbeat_failure_url=os.getenv("FLEETLENS_HEARTBEAT_FAILURE_URL", ""),
    )
