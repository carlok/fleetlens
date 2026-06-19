# Cron

Example:

```cron
15 7 * * * cd /opt/fleetlens && ./scripts/run-check.sh >> logs/cron.log 2>&1
```

Use absolute paths, make `.env` available, and confirm the cron user can read SSH keys. SSH agents are often unavailable in cron, so key files should be directly usable.

When running through Podman, use the full Podman path if cron has a limited `PATH`. On SELinux hosts, keep the `:Z` volume labels from the README examples.

Rotate `logs/cron.log` and monitor failures from SMTP or heartbeat pings.

