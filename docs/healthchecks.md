# Healthchecks

FleetLens can ping Healthchecks-compatible URLs for job start, success, and failure.

```text
FLEETLENS_HEARTBEAT_ENABLED=true
FLEETLENS_HEARTBEAT_START_URL=
FLEETLENS_HEARTBEAT_SUCCESS_URL=
FLEETLENS_HEARTBEAT_FAILURE_URL=
```

Failure pings include a short diagnostic body when possible.

Use hosted Healthchecks.io or any compatible endpoint you operate separately.
