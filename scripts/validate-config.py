#!/usr/bin/env python
from fleetlens.config import load_settings

settings = load_settings()
print(f"inventory={settings.inventory}")
print(f"raw_report={settings.raw_report}")
print(f"json_report={settings.json_report}")
print(f"markdown_report={settings.markdown_report}")
print(f"runner_backend={settings.runner_backend}")

