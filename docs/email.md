# Email

FleetLens sends SMTP email with Python standard library modules.

Configure `.env` from `.env.example`:

```text
FLEETLENS_EMAIL_ENABLED=true
FLEETLENS_EMAIL_SMTP_HOST=smtp.example.com
FLEETLENS_EMAIL_SMTP_PORT=587
FLEETLENS_EMAIL_SMTP_USERNAME=
FLEETLENS_EMAIL_SMTP_PASSWORD=
FLEETLENS_EMAIL_FROM=fleetlens@example.com
FLEETLENS_EMAIL_TO=admin@example.com
```

Use app passwords or provider-specific tokens when required. Do not commit real credentials.

Dry-run:

```bash
python -m fleetlens.cli email --dry-run
```

Use send-on-status flags to avoid OK emails:

```text
FLEETLENS_EMAIL_SEND_ON_OK=false
FLEETLENS_EMAIL_SEND_ON_WARNING=true
FLEETLENS_EMAIL_SEND_ON_CRITICAL=true
```

Common failures are blocked SMTP ports, wrong TLS setting, invalid app password, and cron missing the expected `.env`.

