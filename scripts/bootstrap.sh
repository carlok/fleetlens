#!/usr/bin/env bash
set -euo pipefail

python_bin="${PYTHON:-python3}"

"${python_bin}" - <<'PY'
import sys

if sys.version_info < (3, 11):
    raise SystemExit("FleetLens requires Python 3.11 or newer.")
PY

"${python_bin}" -m venv .venv

# shellcheck source=/dev/null
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e . -r requirements-dev.txt

echo "FleetLens virtual environment ready."
echo "Activate it with: source .venv/bin/activate"
