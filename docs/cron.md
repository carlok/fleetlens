# Cron

Example:

```cron
15 7 * * * cd /opt/fleetlens && . .venv/bin/activate && ./scripts/run-check.sh >> logs/cron.log 2>&1
```

Use absolute paths, make `.env` available, and confirm the cron user can read SSH keys and `known_hosts`. SSH agents are often unavailable in cron, so key files should be directly usable without prompting for a passphrase.

`run-check.sh` passes its arguments to `fleetlens run`. Add `--fail-on critical` (or `--fail-on warning`) to make the job exit with code 1 at that fleet status, so cron mail or a wrapper can notice:

```cron
15 7 * * * cd /opt/fleetlens && . .venv/bin/activate && ./scripts/run-check.sh --fail-on critical >> logs/cron.log 2>&1
```

Rotate `logs/cron.log` and monitor failures from SMTP or heartbeat pings.
