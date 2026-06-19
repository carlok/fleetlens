#!/usr/bin/env bash
set -euo pipefail

export ANSIBLE_CONFIG="${ANSIBLE_CONFIG:-ansible/ansible.cfg}"
export ANSIBLE_HOME="${ANSIBLE_HOME:-.ansible}"
export ANSIBLE_LOCAL_TEMP="${ANSIBLE_LOCAL_TEMP:-.ansible/tmp}"
mkdir -p "${ANSIBLE_HOME}" "${ANSIBLE_LOCAL_TEMP}"

ansible-playbook \
  -i "${FLEETLENS_INVENTORY:-ansible/inventories/example/hosts.ini}" \
  ansible/playbooks/ping.yml
