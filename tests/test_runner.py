import subprocess

import pytest

from fleetlens.config import Settings
from fleetlens.runner import run_ansible_collection


@pytest.fixture
def ansible_env(monkeypatch, tmp_path):
    monkeypatch.delenv("ANSIBLE_CONFIG", raising=False)
    monkeypatch.setenv("ANSIBLE_HOME", str(tmp_path / "ansible"))
    monkeypatch.setenv("ANSIBLE_LOCAL_TEMP", str(tmp_path / "ansible/tmp"))
    monkeypatch.setenv("ANSIBLE_SSH_CONTROL_PATH_DIR", str(tmp_path / "ansible/cp"))


def fake_playbook(monkeypatch, returncode, raw_report=None, calls=None):
    def fake_run(command, check, env):
        if calls is not None:
            calls.append((command, check, env))
        if raw_report is not None:
            raw_report.write_text('{"hosts": []}', encoding="utf-8")
        return subprocess.CompletedProcess(command, returncode)

    monkeypatch.setattr("fleetlens.runner.subprocess.run", fake_run)


def test_shell_runner_invokes_ansible(monkeypatch, tmp_path):
    for name in ("ANSIBLE_CONFIG", "ANSIBLE_HOME", "ANSIBLE_LOCAL_TEMP"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("ANSIBLE_SSH_CONTROL_PATH_DIR", raising=False)
    monkeypatch.setattr("fleetlens.runner.Path.mkdir", lambda *args, **kwargs: None)
    raw = tmp_path / "raw.json"
    calls = []
    fake_playbook(monkeypatch, 0, raw, calls)

    assert run_ansible_collection(Settings(inventory="hosts.ini", raw_report=str(raw))) == 0
    command, check, env = calls[0]
    assert command == [
        "ansible-playbook",
        "-i",
        "hosts.ini",
        "ansible/playbooks/collect.yml",
    ]
    assert check is False
    assert env["ANSIBLE_CONFIG"] == "ansible/ansible.cfg"
    assert env["ANSIBLE_HOME"] == "/tmp/fleetlens-ansible"
    assert env["ANSIBLE_LOCAL_TEMP"] == "/tmp/fleetlens-ansible/tmp"
    assert env["ANSIBLE_SSH_CONTROL_PATH_DIR"] == "/tmp/fleetlens-ansible/cp"


@pytest.mark.parametrize("returncode", [2, 4])
def test_host_failures_still_produce_report(monkeypatch, tmp_path, ansible_env, capsys, returncode):
    raw = tmp_path / "raw.json"
    fake_playbook(monkeypatch, returncode, raw)

    assert run_ansible_collection(Settings(raw_report=str(raw))) == returncode
    assert "some hosts failed" in capsys.readouterr().err


def test_playbook_error_raises(monkeypatch, tmp_path, ansible_env):
    raw = tmp_path / "raw.json"
    fake_playbook(monkeypatch, 1, raw)

    with pytest.raises(RuntimeError, match="rc=1"):
        run_ansible_collection(Settings(raw_report=str(raw)))


def test_stale_raw_report_is_not_reused(monkeypatch, tmp_path, ansible_env):
    raw = tmp_path / "raw.json"
    raw.write_text('{"hosts": []}', encoding="utf-8")
    fake_playbook(monkeypatch, 4)

    with pytest.raises(RuntimeError, match="without writing"):
        run_ansible_collection(Settings(raw_report=str(raw)))
    assert not raw.exists()


def test_unknown_runner_backend_raises():
    with pytest.raises(ValueError):
        run_ansible_collection(Settings(runner_backend="nope"))
