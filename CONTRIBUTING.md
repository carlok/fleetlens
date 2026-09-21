# Contributing to FleetLens

Thanks for your interest. FleetLens is deliberately small: Ansible connects to machines and collects facts, and Python parses, classifies, renders, and notifies. Contributions that keep it predictable and auditable are welcome.

## Before you start

For anything bigger than a small fix, open an issue first. The project deliberately does **not** take:

- remediation of any kind (upgrades, restarts, reboots, cleanup)
- arbitrary remote commands configured through inventory
- plugin frameworks or speculative abstractions
- anything that weakens SSH host key checking

## Development setup

You need Python 3.11–3.13 (Ansible does not yet work here under 3.14).

```bash
uv sync --group dev --locked        # or: PYTHON=python3.11 ./scripts/bootstrap.sh
source .venv/bin/activate
```

## Checks

Run these before opening a pull request. CI runs the same ones:

```bash
python -m ruff check .
python -m coverage run -m pytest && python -m coverage report
ansible-playbook --syntax-check -i ansible/inventories/example/hosts.ini ansible/playbooks/collect.yml
ansible-lint ansible/playbooks ansible/roles
shellcheck scripts/*.sh
```

## Adding or changing a health check

A complete change normally touches:

1. Role defaults (`ansible/roles/vm_healthcheck/defaults/main.yml`) and the example `group_vars`.
2. A focused, read-only collector task file. Use `ansible.builtin.command` rather than `shell` where possible, and set `changed_when: false` and `failed_when: false`. Record `rc`, so a failed command becomes report data and doesn't abort the fleet run.
3. The raw result built in `tasks/main.yml`.
4. `fleetlens/models.py` (`from_mapping` and `to_dict`), `classify.py`, and `render.py`.
5. Fixtures and tests covering OK, WARNING/CRITICAL, and failing-command cases.
6. Docs, especially `docs/security-model.md` and `docs/sudoers.md` if privileges, dependencies, or sensitive data change.

Raw values from Ansible/Jinja can have loose types, such as `"0"` or `"CRITICAL "`. Parse them defensively.

Never emit passwords, tokens, connection strings, or large command output into reports.

## Local files

Keep real inventories in `ansible/inventories/local/` and settings in `.env`; both are git-ignored. Never commit keys, `known_hosts`, or generated reports.

## Pull requests

- Keep each change focused and covered by tests.
- Add an entry under a new or unreleased heading in `CHANGELOG.md`.
- Describe how you verified the change, ideally including a run against a real or throwaway VM.
