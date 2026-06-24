# FleetLens

Agentless VM health reports with Ansible, Python, local SSH, and optional email.

FleetLens checks a small Debian/Ubuntu-like VM fleet over SSH. Ansible performs deterministic read-only collection, Python renders JSON/Markdown reports, and optional SMTP notifications send the result.

## Architecture

```text
cron/systemd/manual shell
        |
        v
local Python virtual environment
        |
        v
Ansible collector -> raw JSON -> Python renderer -> JSON, Markdown, email
```

FleetLens is host-native. It uses the SSH keys, `known_hosts`, network access, and scheduler environment of the user that runs it.

## Requirements

- macOS or Ubuntu
- Python 3.11, 3.12, or 3.13
- `python3-venv` on Ubuntu
- OpenSSH client
- SSH access to the target VMs

Ansible currently fails in this project under the local Python 3.14 runtime, so use Python 3.11-3.13 for the virtual environment.

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

Contributor shortcut with `uv`:

```bash
uv sync --group dev --locked
```

## Configure

Create local config files:

```bash
cp .env.example .env
mkdir -p ansible/inventories/local
cp ansible/inventories/example/hosts.ini ansible/inventories/local/hosts.ini
```

Edit `.env`:

```text
FLEETLENS_INVENTORY=ansible/inventories/local/hosts.ini
```

Edit `ansible/inventories/local/hosts.ini`:

```ini
[vms]
myvm ansible_host=<ip-or-hostname> ansible_user=<user> ansible_port=<port> ansible_ssh_private_key_file=~/.ssh/<private_key_or_pem> ansible_ssh_common_args='-o UserKnownHostsFile=~/.ssh/known_hosts' ansible_python_interpreter=/usr/bin/python3

[vms:vars]
ansible_become=false
```

If your daily SSH command is:

```bash
ssh -i "$HOME/.ssh/<key>" -p <port> <user>@<ip>
```

then the matching inventory values are:

```ini
ansible_host=<ip>
ansible_user=<user>
ansible_port=<port>
ansible_ssh_private_key_file=~/.ssh/<key>
```

FleetLens does not disable SSH host key checking. If needed, add the host key first:

```bash
ssh-keyscan -p <port> <ip-or-hostname> >> "$HOME/.ssh/known_hosts"
```

## Run

With the virtual environment active:

```bash
./scripts/run-ping.sh
./scripts/run-check.sh
```

The scripts load `.env` automatically. Use a different env file with:

```bash
FLEETLENS_ENV_FILE=/path/to/fleetlens.env ./scripts/run-check.sh
```

Reports are written to:

```text
reports/raw-ansible.json
reports/latest.json
reports/latest.md
```

The terminal output includes an actionable summary after the Ansible recap:

```text
FleetLens status: WARNING
Attention needed:
- myvm: WARNING
  - updates available: 10 packages: openssl, curl, +8 more
  - failed systemd units: 1 unit
```

## Email

SMTP is the default notification backend. Configure `.env` from `.env.example`, then test without sending:

```bash
python -m fleetlens.cli email --dry-run
```

Enable email:

```text
FLEETLENS_EMAIL_ENABLED=true
FLEETLENS_EMAIL_SMTP_HOST=smtp.example.com
FLEETLENS_EMAIL_SMTP_PORT=587
FLEETLENS_EMAIL_SMTP_USERNAME=
FLEETLENS_EMAIL_SMTP_PASSWORD=
FLEETLENS_EMAIL_FROM=fleetlens@example.com
FLEETLENS_EMAIL_TO=admin@example.com
```

FleetLens prints a `message_id=...` after SMTP submission so delayed mail can be traced in provider logs.

## Scheduling

Cron and systemd timer examples are in `docs/cron.md` and `docs/systemd-timer.md`. Use absolute paths and make sure the scheduled user can read `.env`, the inventory, and SSH keys.

## Testing

With the virtual environment active:

```bash
python -m pytest
python -m coverage run -m pytest
python -m coverage report
python -m ruff check .
ansible-playbook --syntax-check -i ansible/inventories/example/hosts.ini ansible/playbooks/collect.yml
ansible-lint ansible/playbooks ansible/roles
```

## Safety Model

FleetLens does not remediate hosts. It gathers facts, checks apt metadata, inspects disk/memory/systemd/reboot indicators, and writes reports. `apt-get update` is disabled by default and controlled by Ansible variables.

The example inventory starts in no-sudo mode. Enable sudo later only if you need privileged checks.
