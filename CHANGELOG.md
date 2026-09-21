# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## 0.2.0 - 2026-09-21

### Fixed

- Disk WARNING and CRITICAL results were never reported: the collector emitted
  statuses with trailing whitespace that the classifier did not match.
- `FLEETLENS_EMAIL_SEND_ON_OK/WARNING/CRITICAL` were ignored; `run` and `email`
  now honour them.
- Hosts whose collection aborted early were silently dropped from the report;
  they now appear as CRITICAL with `no result collected`.
- A single failed or unreachable host made `ansible-playbook` exit non-zero and
  aborted the whole run before rendering. Rendering now continues, and a stale
  raw report from a previous run is never reused.
- Errors supplied by the collector did not affect host status.
- Per-host status was lost when a JSON report was reloaded for `email`.
- Heartbeat pings could raise on timeouts or malformed URLs.
- Unreachable hosts reported `reboot_required: false` instead of unknown.

### Added

- A non-zero exit code from the apt, systemd, or journal check on a reachable
  host is reported as a WARNING (`<check> check failed (rc=N)`).
- `needrestart` results are included in JSON and shown in Markdown details
  (informational; they do not change status).
- `fleetlens run --fail-on none|warning|critical` for scheduler-visible exit codes.
- `fleetlens email --force` to send regardless of status toggles.
- `fleetlens` console script entry point.

### Changed

- `scripts/run-check.sh` is a thin wrapper around `fleetlens run`, so cron and
  systemd timer runs behave identically (heartbeats, email gating).
- Memory "used" excludes page cache and buffers.

### Removed

- The container-era build prompt (`prompts/MAIN.md`).

## 0.1.0

- Initial release: Ansible collector, Python renderer, SMTP notifications,
  heartbeat pings, tests, and docs.

