#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/load-env.sh"
fleetlens_load_env

export ANSIBLE_CONFIG="${ANSIBLE_CONFIG:-ansible/ansible.cfg}"
export ANSIBLE_HOME="${ANSIBLE_HOME:-/tmp/fleetlens-ansible}"
export ANSIBLE_LOCAL_TEMP="${ANSIBLE_LOCAL_TEMP:-/tmp/fleetlens-ansible/tmp}"
export ANSIBLE_SSH_CONTROL_PATH_DIR="${ANSIBLE_SSH_CONTROL_PATH_DIR:-/tmp/fleetlens-ansible/cp}"
mkdir -p "${ANSIBLE_HOME}" "${ANSIBLE_LOCAL_TEMP}" "${ANSIBLE_SSH_CONTROL_PATH_DIR}"

ansible-playbook \
  -i "${FLEETLENS_INVENTORY:-ansible/inventories/example/hosts.ini}" \
  ansible/playbooks/ping.yml
