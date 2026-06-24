# Sudoers

FleetLens starts best in no-sudo mode:

```ini
[vms:vars]
ansible_become=false
```

Keep these defaults for a first run:

```yaml
vm_healthcheck_refresh_apt_cache: false
vm_healthcheck_journal_errors_enabled: false
```

Enable sudo later only for checks that need privileged access.

## Simple Mode

Use an existing account with sudo rights. This is convenient for testing but can be awkward from cron if sudo prompts for a password.

## Restricted Checker Mode

Create a dedicated SSH key-only user such as `vmcheck`. Grant only the commands needed for collection where practical.

Ansible become behavior can complicate very narrow sudoers rules, so test with `scripts/run-ping.sh` and `scripts/run-check.sh` before scheduling.

Do not use `NOPASSWD: ALL` in production. It can be acceptable for a disposable lab only if the risk is understood.
