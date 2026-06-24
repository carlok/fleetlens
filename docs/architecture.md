# Architecture

FleetLens is intentionally small:

```text
Ansible collector -> raw JSON -> Python renderer -> Markdown/JSON -> notification
```

Ansible owns SSH, sudo, fact gathering, and safe host commands. Python owns parsing, classification, report rendering, notifications, and heartbeat pings.

FleetLens runs from a local Python virtual environment on the scheduler host. This keeps SSH behavior familiar: the same user, keys, `known_hosts`, DNS, firewall rules, and cron/systemd environment determine what FleetLens can reach.

## Optional LLM Summarizer

A future read-only summarizer may be added after report rendering:

```text
Ansible collector -> JSON report -> Python renderer -> optional LLM summary -> email
```

The LLM receives only structured reports. It never receives SSH access, never executes sudo commands, never remediates hosts, and only produces human-readable recommendations.
