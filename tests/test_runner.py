import pytest

from fleetlens.config import Settings
from fleetlens.runner import run_ansible_collection


def test_shell_runner_invokes_ansible(monkeypatch):
    calls = []

    def fake_run(command, check, env):
        calls.append((command, check, env))

    monkeypatch.setattr("fleetlens.runner.subprocess.run", fake_run)
    run_ansible_collection(Settings(inventory="hosts.ini"))
    command, check, env = calls[0]
    assert command == [
        "ansible-playbook",
        "-i",
        "hosts.ini",
        "ansible/playbooks/collect.yml",
    ]
    assert check is True
    assert env["ANSIBLE_CONFIG"] == "ansible/ansible.cfg"
    assert env["ANSIBLE_HOME"] == ".ansible"
    assert env["ANSIBLE_LOCAL_TEMP"] == ".ansible/tmp"


def test_unknown_runner_backend_raises():
    with pytest.raises(ValueError):
        run_ansible_collection(Settings(runner_backend="nope"))
