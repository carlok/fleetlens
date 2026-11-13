# FleetLens — guide for coding agents

This document is for automated coding agents (and humans using them) working in this repository. Human contributors should also read [CONTRIBUTING.md](CONTRIBUTING.md).

## Project summary

FleetLens is a small Python + Ansible tool: Ansible collects read-only health facts over SSH; Python parses, classifies, renders reports, and optionally sends email or heartbeat pings. There is no agent on targets and no remediation scope.

## Setup

Requirements: Python **3.11–3.13** (not 3.14+), Linux or macOS as the control machine.

Preferred (matches CI):

```bash
uv sync --group dev --locked
uv run <command>
```

Alternative:

```bash
PYTHON=python3.11 ./scripts/bootstrap.sh   # or python3.12 / 3.13
source .venv/bin/activate
```

Ansible-related env vars used in CI (optional locally):

```bash
export ANSIBLE_CONFIG=ansible/ansible.cfg
export ANSIBLE_HOME=.ansible
export ANSIBLE_LOCAL_TEMP=.ansible/tmp
```

Local operator config (never commit):

```bash
cp .env.example .env
mkdir -p ansible/inventories/local
cp ansible/inventories/example/hosts.ini ansible/inventories/local/hosts.ini
```

## Tests, coverage, and lint

Run the same checks as [`.github/workflows/ci.yml`](.github/workflows/ci.yml) before you commit.

```bash
uv run ruff check .
uv run coverage run -m pytest
uv run coverage report
mkdir -p .ansible/tmp
uv run ansible-playbook --syntax-check -i ansible/inventories/example/hosts.ini ansible/playbooks/ping.yml
uv run ansible-playbook --syntax-check -i ansible/inventories/example/hosts.ini ansible/playbooks/collect.yml
uv run ansible-lint ansible/playbooks ansible/roles
shellcheck -x scripts/*.sh
```

With an activated venv, `make test` and `make coverage` wrap pytest and coverage; `make lint` runs Ruff.

Coverage is configured in `pyproject.toml`: `source = ["fleetlens"]`, branch coverage on, **`fail_under = 85`**. `coverage report` exits non-zero if total coverage drops below 85%.

## Project layout

```text
fleetlens/          # Python package: cli, config, parse/classify/render, notifier, email, heartbeat
ansible/
  playbooks/        # ping.yml, collect.yml
  roles/vm_healthcheck/   # read-only collection tasks
  inventories/example/      # safe example inventory and group_vars (committed)
  inventories/local/        # real inventory (git-ignored)
tests/              # pytest + JSON fixtures under tests/fixtures/
scripts/            # bootstrap, run-check, run-ping, shell helpers
docs/               # user-facing architecture, security, ops guides
reports/            # generated output (git-ignored)
```

Entry point: `fleetlens` CLI (`fleetlens.cli:main`).

## Conventions

- **Scope**: read-only checks only; no upgrades, restarts, arbitrary remote commands, or weakening SSH host key checking.
- **Style**: Ruff (`line-length = 100`, rules E, F, I, UP, B, SIM). Match existing patterns in touched files.
- **Ansible**: prefer `ansible.builtin.command` over `shell`; `changed_when: false`, `failed_when: false` on collectors; record `rc` for failures.
- **Types**: parse raw Ansible/Jinja values defensively (strings like `"0"` or `"CRITICAL "`).
- **Secrets**: never put passwords, tokens, URLs with credentials, or large command output into reports, logs, or committed files.
- **Health-check changes**: touch role tasks/defaults, `fleetlens/models.py`, `classify.py`, `render.py`, fixtures, tests, and docs as needed (see CONTRIBUTING).
- **Changelog**: add a note under an unreleased section in [CHANGELOG.md](CHANGELOG.md) for user-visible changes.
- **Public docs** (`README.md`, `docs/`, issue templates): keep examples generic (placeholders like `smtp.example.com`, `<ip-or-hostname>`). Do not document or commit host-specific paths, real hostnames, or personal infrastructure details.

## Rules for agents

1. **Test coverage**: Always try to **increase test coverage** (or at least preserve it above the 85% gate) before each commit. Add or extend tests in `tests/` when you change behavior in `fleetlens/`.
2. **No secrets or host-specific values** in commits: no `.env`, real inventories under `local/`, SSH keys, SMTP credentials, heartbeat URLs with tokens, or generated `reports/`.
3. **Keep public documentation general**; use example inventory and `.env.example` patterns only.
4. **Do not change [LICENSE](LICENSE)** (MIT) unless explicitly requested.
5. **Minimize diff**: no drive-by refactors, speculative features, or product behavior changes when the task is repo/docs/CI maintenance.
6. **License and conduct**: follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). For security issues, see [SECURITY.md](SECURITY.md) (private advisory), not public issues.

## License

[MIT](LICENSE) © Carlo Perassi — unchanged by this document.
