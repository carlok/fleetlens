# Security Policy

## Supported versions

Only the latest release receives fixes.

## Reporting a vulnerability

Please do **not** open a public issue for security problems.

Report privately through GitHub's [private vulnerability reporting](https://github.com/carlok/fleetlens/security/advisories/new). Include the affected version, a description, and reproduction steps if you have them. You should get an acknowledgement within a week.

## Scope

FleetLens runs with the SSH credentials of the user that invokes it and executes a fixed set of read-only commands on target hosts. Examples of relevant reports:

- a collector that mutates target state or runs commands beyond those documented in [docs/security-model.md](docs/security-model.md)
- secrets (SMTP credentials, heartbeat URLs, inventory data) leaking into reports, email, or logs
- weakening of SSH host key verification

Misconfigured inventories, sudoers rules, or SMTP providers on the operator's side are out of scope. [docs/sudoers.md](docs/sudoers.md) covers safe configuration.
