# FleetLens

Agentless VM health reports with Ansible, Podman, Python, and email.

FleetLens checks a small Debian/Ubuntu-like VM fleet over SSH. Ansible performs deterministic read-only collection, Python renders JSON/Markdown reports, and optional SMTP notifications send the result.

## Architecture

```text
cron/systemd timer
        |
        v
Podman container with dependencies
        |
        v
bind-mounted FleetLens source in /workspace
        |
        v
Ansible collector -> raw JSON -> Python renderer -> JSON, Markdown, email
```

The image contains dependencies only. The repository is mounted into `/workspace`, so normal source, playbook, test, and documentation edits do not require rebuilding the image. Rebuild only when dependencies or the `Containerfile` change.

## Quick Start

```bash
cp .env.example .env
podman build -t fleetlens:local .
podman run --rm \
  -v "$PWD:/workspace:Z" \
  -v "$HOME/.ssh:/home/runner/.ssh:ro,Z" \
  --env-file .env \
  fleetlens:local \
  ./scripts/run-ping.sh
```

Edit `ansible/inventories/example/hosts.ini` or copy it to an ignored local inventory directory and set `FLEETLENS_INVENTORY`.

For container runs, inventory SSH paths must match the container mount, for example
`/home/runner/.ssh/<key>` and `/home/runner/.ssh/known_hosts` when using the
command above.

For direct host runs, use host paths in the inventory instead:

```ini
myvm ansible_host=<ip> ansible_user=<user> ansible_port=<port> ansible_ssh_private_key_file=/Users/carlo/.ssh/<key> ansible_ssh_common_args='-o UserKnownHostsFile=/Users/carlo/.ssh/known_hosts'
```

Then run:

```bash
set -a
source .env
set +a
uv run ./scripts/run-check.sh
```

The project pins local `uv` execution to Python 3.11. Ansible currently fails
under the local Python 3.14 runtime.

The example inventory starts in no-sudo mode:

```ini
[vms:vars]
ansible_become=false
```

That is enough for the first read-only checks when apt cache refresh and journal errors are disabled. Enable sudo later only if you need privileged checks.

## Safety Model

FleetLens does not remediate hosts. It gathers facts, checks apt metadata, inspects disk/memory/systemd/reboot indicators, and writes reports. `apt-get update` is disabled by default and controlled by Ansible variables.

FleetLens does not disable SSH host key checking. Fix host keys on the host or mount a suitable `.ssh` directory into the container.

## Common Commands

```bash
make build
make ping
make run
make test
make lint
make email-dry-run
```

Reports are written to `reports/latest.json` and `reports/latest.md`.

## Email

SMTP is the default notification backend. Configure `.env` from `.env.example`, then test without sending:

```bash
python -m fleetlens.cli email --dry-run
```

Optional Apprise notifications are supported through environment variables but are disabled by default.

## Scheduling

Cron and systemd timer examples are in `docs/cron.md` and `docs/systemd-timer.md`. Use absolute paths and make sure SSH keys and environment variables are available to the scheduled process.

## Optional Integrations

ARA, Semaphore, Healthchecks-compatible heartbeat pings, ntfy, and Gotify are optional compose profiles. FleetLens works without starting any optional service.

## Testing

Tests do not require real SSH hosts:

```bash
python -m pytest
python -m coverage run -m pytest
python -m coverage report
python -m ruff check .
```

## Roadmap

Future versions may add a read-only LLM summarizer that receives only structured reports, never SSH credentials, and never executes remediation.
