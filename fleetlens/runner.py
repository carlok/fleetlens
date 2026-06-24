from __future__ import annotations

import os
import subprocess

from fleetlens.config import Settings


def run_ansible_collection(settings: Settings) -> None:
    backend = settings.runner_backend.lower()
    if backend == "shell":
        env = os.environ.copy()
        env.setdefault("ANSIBLE_CONFIG", "ansible/ansible.cfg")
        env.setdefault("ANSIBLE_HOME", "/tmp/fleetlens-ansible")
        env.setdefault("ANSIBLE_LOCAL_TEMP", "/tmp/fleetlens-ansible/tmp")
        subprocess.run(
            [
                "ansible-playbook",
                "-i",
                settings.inventory,
                "ansible/playbooks/collect.yml",
            ],
            check=True,
            env=env,
        )
        return
    if backend == "ansible-runner":
        _run_ansible_runner(settings)
        return
    raise ValueError(f"unsupported runner backend: {settings.runner_backend}")


def _run_ansible_runner(settings: Settings) -> None:
    try:
        import ansible_runner
    except ImportError as exc:
        message = "ansible-runner backend requested but ansible-runner is not installed"
        raise RuntimeError(message) from exc
    result = ansible_runner.run(
        private_data_dir=".",
        inventory=settings.inventory,
        playbook="ansible/playbooks/collect.yml",
    )
    if result.rc != 0:
        raise RuntimeError(f"ansible-runner failed with rc={result.rc}")
