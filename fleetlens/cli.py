from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fleetlens.classify import classify_fleet
from fleetlens.config import load_settings
from fleetlens.emailer import build_message, load_report, send_message
from fleetlens.heartbeat import heartbeat_failure, heartbeat_start, heartbeat_success
from fleetlens.parse_ansible import load_raw_report
from fleetlens.render import render_markdown, write_json_report, write_markdown_report
from fleetlens.runner import run_ansible_collection


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fleetlens")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("--input", default=None)
    render_parser.add_argument("--json-out", default=None)
    render_parser.add_argument("--markdown-out", default=None)

    email_parser = subparsers.add_parser("email")
    email_parser.add_argument("--json", default=None)
    email_parser.add_argument("--markdown", default=None)
    email_parser.add_argument("--dry-run", action="store_true")

    subparsers.add_parser("run")

    args = parser.parse_args(argv)
    settings = load_settings()
    try:
        if args.command == "render":
            render_command(args, settings)
        elif args.command == "email":
            email_command(args, settings)
        elif args.command == "run":
            run_command(settings)
    except Exception as exc:
        heartbeat_failure(settings, str(exc))
        raise
    return 0


def render_command(args: argparse.Namespace, settings) -> None:
    raw_path = args.input or settings.raw_report
    json_path = args.json_out or settings.json_report
    markdown_path = args.markdown_out or settings.markdown_report
    report = classify_fleet(load_raw_report(raw_path))
    write_json_report(report, json_path)
    write_markdown_report(report, markdown_path)
    print(f"{report.status.value}: wrote {json_path} and {markdown_path}")


def email_command(args: argparse.Namespace, settings) -> None:
    json_path = args.json or settings.json_report
    markdown_path = args.markdown or settings.markdown_report
    report = load_report(json_path)
    if Path(markdown_path).exists():
        body = Path(markdown_path).read_text(encoding="utf-8")
    else:
        body = render_markdown(report)
    message = build_message(report, settings, body, markdown_path, json_path)
    if args.dry_run:
        print(
            f"DRY RUN: to={', '.join(settings.email_to)} "
            f"subject={message['Subject']} message_id={message['Message-ID']}"
        )
        return
    send_message(message, settings)
    print(f"submitted email to {', '.join(settings.email_to)} message_id={message['Message-ID']}")


def run_command(settings) -> None:
    heartbeat_start(settings)
    run_ansible_collection(settings)
    report = classify_fleet(load_raw_report(settings.raw_report))
    write_json_report(report, settings.json_report)
    write_markdown_report(report, settings.markdown_report)
    if settings.email_enabled:
        body = render_markdown(report)
        message = build_message(
            report,
            settings,
            body,
            settings.markdown_report,
            settings.json_report,
        )
        send_message(message, settings)
    heartbeat_success(settings)
    print(f"{report.status.value}: FleetLens run complete")


if __name__ == "__main__":
    sys.exit(main())
