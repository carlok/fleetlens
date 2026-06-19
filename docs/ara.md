# ARA

ARA can record Ansible run history. It is optional and independent from FleetLens reports.

Start ARA:

```bash
podman compose --profile ara up -d ara
```

Then run FleetLens:

```bash
podman compose run --rm fleetlens-runner ./scripts/run-check.sh
```

Optional variables:

```text
FLEETLENS_ARA_ENABLED=false
ARA_API_CLIENT=http
ARA_API_SERVER=http://ara:8000
```

FleetLens must still work with ARA disabled.

