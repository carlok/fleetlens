# Systemd Timer

User-level service example:

```ini
[Unit]
Description=FleetLens VM healthcheck

[Service]
Type=oneshot
WorkingDirectory=/opt/fleetlens
EnvironmentFile=/opt/fleetlens/.env
ExecStart=/opt/fleetlens/scripts/run-check.sh
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

The service can also run the documented `podman run` command. Keep SSH key paths and volume labels explicit.

