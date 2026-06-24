# Systemd Timer

User-level service example:

```ini
[Unit]
Description=FleetLens VM healthcheck

[Service]
Type=oneshot
WorkingDirectory=/opt/fleetlens
EnvironmentFile=/opt/fleetlens/.env
ExecStart=/opt/fleetlens/.venv/bin/python -m fleetlens.cli run
```

Timer:

```ini
[Unit]
Description=Run FleetLens daily

[Timer]
OnCalendar=*-*-* 07:15:00
Persistent=true

[Install]
WantedBy=timers.target
```

The service user must be able to read the configured SSH private key and `known_hosts` file. Use absolute paths in inventory files when the service runs outside an interactive shell.
