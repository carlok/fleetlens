# FleetLens

[![CI](https://github.com/carlok/fleetlens/actions/workflows/ci.yml/badge.svg)](https://github.com/carlok/fleetlens/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python 3.11–3.13](https://img.shields.io/badge/python-3.11%E2%80%933.13-blue.svg)

Agentless, read-only health reports for a small Debian/Ubuntu VM fleet.

FleetLens logs into each machine over SSH with Ansible, collects a fixed set of read-only facts, and turns them into a JSON report, a Markdown report, a terminal summary, and an optional email. Nothing is installed on the targets and nothing on them is changed.

It fits the gap between "I SSH in and look around every few weeks" and a full monitoring stack: a handful of VMs, a daily cron job, and a report that tells you which ones need attention.

## What it checks

For every host in the `vms` inventory group:

| Check | Source | Result |
|---|---|---|
| Reachability | Ansible connection | CRITICAL if unreachable or collection aborted |
| Disk usage | `df -P` | WARNING ≥ 85%, CRITICAL ≥ 95% (configurable) |
| Pending updates | `apt list --upgradable` | WARNING, with package names and security count |
| Reboot required | `/var/run/reboot-required` | WARNING |
| Failed units | `systemctl --failed` | WARNING |
| Journal errors | `journalctl -p err` (opt-in) | WARNING |
| Services needing restart | `needrestart -b` (if installed) | informational |
| OS, kernel, uptime, load, memory | Ansible facts, `/proc/loadavg` | informational |

If one of these commands fails on a reachable host, the host is marked WARNING (`apt check failed (rc=N)`). A failed check never counts as a pass.

The fleet status is the worst host status: `OK`, `WARNING`, `CRITICAL`, or `UNKNOWN` (no results at all).

## How it works

```text
cron / systemd timer / shell
        |
        v
fleetlens run  ──>  ansible-playbook collect.yml  ──>  reports/raw-ansible.json
                                                              |
                     parse -> classify -> render  <───────────┘
                              |
                              +──> reports/latest.json
                              +──> reports/latest.md
                              +──> terminal summary
                              +──> email (SMTP), heartbeat pings
```

Ansible does the SSH work and the collection. Python handles parsing, classification, rendering, and notification. FleetLens runs on the host, so it uses the SSH keys, `known_hosts`, DNS, and network access of whichever user runs it. See [docs/architecture.md](docs/architecture.md).

## Requirements

- macOS or Linux (Ubuntu/Debian) as the control machine
- Python 3.11, 3.12, or 3.13 (Ansible does not yet work here under 3.14)
- OpenSSH client and key-based SSH access to the targets
- Debian/Ubuntu targets with `/usr/bin/python3`

## Install

macOS with Homebrew:

```bash
brew install python@3.11
PYTHON=python3.11 ./scripts/bootstrap.sh
source .venv/bin/activate
```

Ubuntu:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip openssh-client
./scripts/bootstrap.sh
source .venv/bin/activate
```

Contributors can use `uv sync --group dev --locked` instead.

## Configure

Create local config files. Both locations are git-ignored:

```bash
cp .env.example .env
mkdir -p ansible/inventories/local
cp ansible/inventories/example/hosts.ini ansible/inventories/local/hosts.ini
```

Point `.env` at the inventory:

```text
FLEETLENS_INVENTORY=ansible/inventories/local/hosts.ini
```

Add your hosts to `ansible/inventories/local/hosts.ini`:

```ini
[vms]
myvm ansible_host=<ip-or-hostname> ansible_user=<user> ansible_port=<port> ansible_ssh_private_key_file=~/.ssh/<private_key_or_pem> ansible_ssh_common_args='-o UserKnownHostsFile=~/.ssh/known_hosts' ansible_python_interpreter=/usr/bin/python3

[vms:vars]
ansible_become=false
```

If your usual command is `ssh -i ~/.ssh/<key> -p <port> <user>@<ip>`, those same four values go into `ansible_ssh_private_key_file`, `ansible_port`, `ansible_user`, and `ansible_host`.

FleetLens keeps SSH host key checking on. Add each host key once:

```bash
ssh-keyscan -p <port> <ip-or-hostname> >> "$HOME/.ssh/known_hosts"
```

Thresholds and optional checks are Ansible variables; see [`ansible/inventories/example/group_vars/all.yml`](ansible/inventories/example/group_vars/all.yml).

## Run

With the virtual environment active:

```bash
./scripts/run-ping.sh    # connectivity only
./scripts/run-check.sh   # full collection, report, optional email
```

`run-check.sh` loads `.env` and calls `fleetlens run`, which is the same command a systemd timer uses. To load a different env file, run `FLEETLENS_ENV_FILE=/path/to/fleetlens.env ./scripts/run-check.sh`.

After the Ansible recap, the terminal shows only what needs attention:

```text
FleetLens status: CRITICAL
Attention needed:
- web1: WARNING
  - updates available: 10 packages: openssl, curl, libssl3, git, vim, +5 more
  - reboot required
- db1: CRITICAL
  - / disk critical: 96% used
- old-vm: CRITICAL
  - host unreachable
CRITICAL: FleetLens run complete
```

Reports are written to `reports/latest.json` and `reports/latest.md`. The Markdown report has a summary table and per-host details.

By default the command exits 0 whatever the fleet status, so a WARNING doesn't count as a failed job. Add `--fail-on critical` or `--fail-on warning` if you want the scheduler to see a non-zero exit code:

```bash
./scripts/run-check.sh --fail-on critical
```

## Email and heartbeats

SMTP email is off by default. Enable it in `.env`:

```text
FLEETLENS_EMAIL_ENABLED=true
FLEETLENS_EMAIL_SMTP_HOST=smtp.example.com
FLEETLENS_EMAIL_SMTP_PORT=587
FLEETLENS_EMAIL_FROM=fleetlens@example.com
FLEETLENS_EMAIL_TO=admin@example.com
```

By default you get mail only for WARNING and CRITICAL (`FLEETLENS_EMAIL_SEND_ON_*`). Preview with `python -m fleetlens.cli email --dry-run`. Each sent message prints a `message_id=...` you can trace in provider logs. See [docs/email.md](docs/email.md).

FleetLens can also ping [Healthchecks](https://healthchecks.io)-compatible URLs at start, success, and failure, so a run that never happens still gets noticed. See [docs/healthchecks.md](docs/healthchecks.md).

## Scheduling

- [docs/cron.md](docs/cron.md)
- [docs/systemd-timer.md](docs/systemd-timer.md)

Use absolute paths. The scheduled user needs read access to `.env`, the inventory, and the SSH key, and the key must work without a passphrase prompt.

## Safety model

- **Read-only by default.** No upgrades, restarts, reboots, or cleanup. Remediation is out of scope.
- **No sudo by default.** The example inventory uses `ansible_become=false`. `apt-get update` only runs if you set `vm_healthcheck_refresh_apt_cache: true` and grant sudo.
- **Host key checking stays on.**
- **No secrets in the repo.** `.env`, local inventories, keys, and reports are git-ignored.

See [docs/security-model.md](docs/security-model.md) and [docs/sudoers.md](docs/sudoers.md).

## Documentation

| Topic | Doc |
|---|---|
| Architecture | [docs/architecture.md](docs/architecture.md) |
| Security model / sudo | [docs/security-model.md](docs/security-model.md), [docs/sudoers.md](docs/sudoers.md) |
| Email | [docs/email.md](docs/email.md) |
| Heartbeats | [docs/healthchecks.md](docs/healthchecks.md) |
| Scheduling | [docs/cron.md](docs/cron.md), [docs/systemd-timer.md](docs/systemd-timer.md) |
| Troubleshooting | [docs/troubleshooting.md](docs/troubleshooting.md) |
| When to use something else | [docs/alternatives.md](docs/alternatives.md) |
| Roadmap | [docs/roadmap.md](docs/roadmap.md) |

## Development

```bash
python -m pytest
python -m coverage run -m pytest && python -m coverage report
python -m ruff check .
ansible-playbook --syntax-check -i ansible/inventories/example/hosts.ini ansible/playbooks/collect.yml
ansible-lint ansible/playbooks ansible/roles
```

See [CONTRIBUTING.md](CONTRIBUTING.md). To report a vulnerability, see [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) © Carlo Perassi
