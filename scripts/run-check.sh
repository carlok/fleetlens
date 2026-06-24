#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports logs
export ANSIBLE_CONFIG="${ANSIBLE_CONFIG:-ansible/ansible.cfg}"
export ANSIBLE_HOME="${ANSIBLE_HOME:-/tmp/fleetlens-ansible}"
export ANSIBLE_LOCAL_TEMP="${ANSIBLE_LOCAL_TEMP:-/tmp/fleetlens-ansible/tmp}"
export ANSIBLE_SSH_CONTROL_PATH_DIR="${ANSIBLE_SSH_CONTROL_PATH_DIR:-/tmp/fleetlens-ansible/cp}"
mkdir -p "${ANSIBLE_HOME}" "${ANSIBLE_LOCAL_TEMP}" "${ANSIBLE_SSH_CONTROL_PATH_DIR}"

ansible-playbook \
  -i "${FLEETLENS_INVENTORY:-ansible/inventories/example/hosts.ini}" \
  ansible/playbooks/collect.yml

python -m fleetlens.cli render \
  --input "${FLEETLENS_RAW_REPORT:-reports/raw-ansible.json}" \
  --json-out "${FLEETLENS_JSON_REPORT:-reports/latest.json}" \
  --markdown-out "${FLEETLENS_MARKDOWN_REPORT:-reports/latest.md}"

if [[ "${FLEETLENS_EMAIL_ENABLED:-false}" == "true" ]]; then
  python -m fleetlens.cli email \
    --markdown "${FLEETLENS_MARKDOWN_REPORT:-reports/latest.md}" \
    --json "${FLEETLENS_JSON_REPORT:-reports/latest.json}"
fi
