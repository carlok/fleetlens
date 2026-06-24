# Security Model

FleetLens defaults to collection, not remediation.

Allowed checks include Ansible fact gathering, `uname`, `uptime`, `free`, `df`, `apt list --upgradable`, `apt-get -s upgrade`, `/var/run/reboot-required`, `systemctl --failed`, and optional `journalctl`, `needrestart`, or `checkrestart`.

`apt-get update` is disabled by default and must be explicitly enabled in inventory variables.

FleetLens does not store secrets in the repository. Keep `.env`, private inventories, SSH keys, and notification URLs local and ignored.
