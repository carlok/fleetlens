# Roadmap

Ideas under consideration, in no particular order:

- Inventory-driven host-specific checks (for example database readiness or VPN tunnel status), enabled per group or host through scoped variables. Each check stays read-only and reports a structured `OK/WARNING/CRITICAL/UNKNOWN` result.
- Route the `run` notification step through the notifier abstraction, so Apprise can be used instead of SMTP.
- More Linux distribution collectors.
- Diffs between consecutive runs.
- Optional read-only LLM summary of the structured report (see [architecture.md](architecture.md)).

FleetLens will not add automatic remediation in version 1.
