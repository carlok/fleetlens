# Cron

Example:

```cron
15 7 * * * cd /opt/fleetlens && . .venv/bin/activate && ./scripts/run-check.sh >> logs/cron.log 2>&1
```

Use absolute paths, make `.env` available, and confirm the cron user can read SSH keys and `known_hosts`. SSH agents are often unavailable in cron, so key files should be directly usable without prompting for a passphrase.

Rotate `logs/cron.log` and monitor failures from SMTP or heartbeat pings.
