# Architecture

FleetLens is intentionally small:

```text
Ansible collector -> raw JSON -> Python renderer -> Markdown/JSON -> notification
```

Ansible owns SSH, sudo, fact gathering, and safe host commands. Python owns parsing, classification, report rendering, notifications, and heartbeat pings.

The Podman image is a dependency runtime. The repository is bind-mounted into `/workspace` for fast iteration, so code and playbook edits are immediately visible inside the container.

## Optional LLM Summarizer

A future read-only summarizer may be added after report rendering:

```text
Ansible collector -> JSON report -> Python renderer -> optional LLM summary -> email
```

The LLM receives only structured reports. It never receives SSH access, never executes sudo commands, never remediates hosts, and only produces human-readable recommendations.

