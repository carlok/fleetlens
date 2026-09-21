from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from fleetlens.config import Settings

PLAYBOOK = "ansible/playbooks/collect.yml"

# ansible-playbook still writes the raw report when individual hosts fail (2) or are
# unreachable (4); those hosts are reported, so the run must go on to rendering.
HOST_FAILURE_RETURN_CODES = frozenset({2, 4})


def run_ansible_collection(settings: Settings) -> int:
    backend = settings.runner_backend.lower()
    if backend not in {"shell", "ansible-runner"}:
        raise ValueError(f"unsupported runner backend: {settings.runner_backend}")
    raw_report = Path(settings.raw_report)
    # A stale report from a previous run must never be rendered as current.
    raw_report.unlink(missing_ok=True)
    run = _run_shell if backend == "shell" else _run_ansible_runner
    return_code = run(settings)
    return _check_result(return_code, raw_report)


def _run_shell(settings: Settings) -> int:
    env = os.environ.copy()
    env.setdefault("ANSIBLE_CONFIG", "ansible/ansible.cfg")
    env.setdefault("ANSIBLE_HOME", "/tmp/fleetlens-ansible")
    env.setdefault("ANSIBLE_LOCAL_TEMP", "/tmp/fleetlens-ansible/tmp")
    env.setdefault("ANSIBLE_SSH_CONTROL_PATH_DIR", "/tmp/fleetlens-ansible/cp")
    for name in ("ANSIBLE_HOME", "ANSIBLE_LOCAL_TEMP", "ANSIBLE_SSH_CONTROL_PATH_DIR"):
        Path(env[name]).mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["ansible-playbook", "-i", settings.inventory, PLAYBOOK],
        check=False,
        env=env,
    )
    return result.returncode


def _run_ansible_runner(settings: Settings) -> int:
    try:
        import ansible_runner
    except ImportError as exc:
        message = "ansible-runner backend requested but ansible-runner is not installed"
        raise RuntimeError(message) from exc
    result = ansible_runner.run(
        private_data_dir=".",
        inventory=settings.inventory,
        playbook=PLAYBOOK,
    )
    return result.rc


def _check_result(return_code: int, raw_report: Path) -> int:
    if return_code != 0 and return_code not in HOST_FAILURE_RETURN_CODES:
        raise RuntimeError(f"ansible-playbook failed with rc={return_code}")
    if not raw_report.exists():
        raise RuntimeError(f"ansible-playbook exited rc={return_code} without writing {raw_report}")
    if return_code:
        print(
            f"ansible-playbook exited rc={return_code}: some hosts failed; "
            "they are included in the report",
            file=sys.stderr,
        )
    return return_code
