#!/usr/bin/env bash
# Collect, render, and optionally email a FleetLens report.
# Thin wrapper around `python -m fleetlens.cli run` so cron and systemd behave the same.
# Extra arguments are passed through, e.g. ./scripts/run-check.sh --fail-on critical
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/load-env.sh"
fleetlens_load_env

mkdir -p reports logs
export ANSIBLE_CONFIG="${ANSIBLE_CONFIG:-ansible/ansible.cfg}"
export ANSIBLE_HOME="${ANSIBLE_HOME:-/tmp/fleetlens-ansible}"
export ANSIBLE_LOCAL_TEMP="${ANSIBLE_LOCAL_TEMP:-/tmp/fleetlens-ansible/tmp}"
export ANSIBLE_SSH_CONTROL_PATH_DIR="${ANSIBLE_SSH_CONTROL_PATH_DIR:-/tmp/fleetlens-ansible/cp}"
mkdir -p "${ANSIBLE_HOME}" "${ANSIBLE_LOCAL_TEMP}" "${ANSIBLE_SSH_CONTROL_PATH_DIR}"

exec python -m fleetlens.cli run "$@"
