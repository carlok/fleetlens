# Semaphore

Semaphore UI is optional. It can run the same Ansible playbooks from a web UI and manage schedules outside cron.

Start it with:

```bash
podman compose --profile semaphore up -d
```

Semaphore is an orchestration control plane, not FleetLens healthcheck logic. AWX is a heavier alternative and is not implemented in version 1.

