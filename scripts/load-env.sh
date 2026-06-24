#!/usr/bin/env bash

fleetlens_load_env() {
  local env_file="${FLEETLENS_ENV_FILE:-.env}"
  if [[ -f "${env_file}" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "${env_file}"
    set +a
  fi
}
