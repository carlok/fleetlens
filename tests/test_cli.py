import json

import pytest

from fleetlens.cli import main


def test_cli_render_writes_reports(tmp_path):
    raw = tmp_path / "raw.json"
    json_out = tmp_path / "latest.json"
    markdown_out = tmp_path / "latest.md"
    raw.write_text(
        json.dumps(
            {
                "hosts": [
                    {
                        "host": "vm1",
                        "reachable": True,
                        "sudo_ok": True,
                        "apt": {"upgradable_count": 0},
                        "systemd": {"failed_count": 0},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    assert main(
        [
            "render",
            "--input",
            str(raw),
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
        ]
    ) == 0
    assert json.loads(json_out.read_text(encoding="utf-8"))["status"] == "OK"
    assert markdown_out.read_text(encoding="utf-8").startswith("# FleetLens Report")


def test_cli_render_prints_terminal_summary(tmp_path, capsys):
    raw = tmp_path / "raw.json"
    json_out = tmp_path / "latest.json"
    markdown_out = tmp_path / "latest.md"
    raw.write_text(
        json.dumps(
            {
                "hosts": [
                    {
                        "host": "vm1",
                        "reachable": True,
                        "sudo_ok": True,
                        "apt": {"upgradable_count": 2, "packages": ["openssl/jammy 3.0 amd64"]},
                        "systemd": {"failed_count": 1},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    assert main(
        [
            "render",
            "--input",
            str(raw),
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
        ]
    ) == 0
    output = capsys.readouterr().out
    assert "Attention needed:" in output
    assert "vm1: WARNING" in output
    assert "updates available: 2 packages: openssl" in output
    assert "failed systemd units: 1 unit" in output


def write_fleet_json(path, status):
    path.write_text(
        json.dumps(
            {
                "status": status,
                "generated_at": "2026-06-19T12:00:00Z",
                "warnings": [],
                "criticals": [],
                "hosts": [],
            }
        ),
        encoding="utf-8",
    )


def test_cli_email_skips_status_not_configured(tmp_path, capsys, monkeypatch):
    json_report = tmp_path / "latest.json"
    write_fleet_json(json_report, "OK")
    monkeypatch.setattr("fleetlens.cli.send_message", lambda *args: pytest.fail("sent"))

    assert main(["email", "--json", str(json_report), "--markdown", str(tmp_path / "x.md")]) == 0
    assert "skipped email: FLEETLENS_EMAIL_SEND_ON_OK is false" in capsys.readouterr().out


def test_cli_email_force_sends(tmp_path, capsys, monkeypatch):
    json_report = tmp_path / "latest.json"
    write_fleet_json(json_report, "OK")
    sent = []
    monkeypatch.setattr("fleetlens.cli.send_message", lambda message, settings: sent.append(1))

    args = ["email", "--json", str(json_report), "--markdown", str(tmp_path / "x.md"), "--force"]
    assert main(args) == 0
    assert sent == [1]


@pytest.fixture
def fake_collection(monkeypatch, tmp_path):
    raw = tmp_path / "raw.json"
    monkeypatch.setenv("FLEETLENS_RAW_REPORT", str(raw))
    monkeypatch.setenv("FLEETLENS_JSON_REPORT", str(tmp_path / "latest.json"))
    monkeypatch.setenv("FLEETLENS_MARKDOWN_REPORT", str(tmp_path / "latest.md"))
    sent = []
    monkeypatch.setattr("fleetlens.cli.send_message", lambda message, settings: sent.append(1))

    def collect(hosts):
        monkeypatch.setattr(
            "fleetlens.cli.run_ansible_collection",
            lambda settings: raw.write_text(json.dumps({"hosts": hosts}), encoding="utf-8"),
        )
        return sent

    return collect


def test_cli_run_fail_on(fake_collection):
    fake_collection([{"host": "vm1", "apt": {"upgradable_count": 3}}])
    assert main(["run"]) == 0
    assert main(["run", "--fail-on", "critical"]) == 0
    assert main(["run", "--fail-on", "warning"]) == 1


def test_cli_run_email_follows_status_toggles(fake_collection, monkeypatch):
    monkeypatch.setenv("FLEETLENS_EMAIL_ENABLED", "true")
    sent = fake_collection([{"host": "vm1"}])
    assert main(["run"]) == 0
    assert sent == []

    sent = fake_collection([{"host": "vm1", "reachable": False}])
    assert main(["run"]) == 0
    assert sent == [1]


def test_cli_email_dry_run(tmp_path, capsys):
    json_report = tmp_path / "latest.json"
    markdown_report = tmp_path / "latest.md"
    json_report.write_text(
        json.dumps(
            {
                "status": "WARNING",
                "generated_at": "2026-06-19T12:00:00Z",
                "warnings": [],
                "criticals": [],
                "hosts": [],
            }
        ),
        encoding="utf-8",
    )
    markdown_report.write_text("# FleetLens Report\n", encoding="utf-8")

    assert main(
        [
            "email",
            "--json",
            str(json_report),
            "--markdown",
            str(markdown_report),
            "--dry-run",
        ]
    ) == 0
    output = capsys.readouterr().out
    assert "DRY RUN" in output
    assert "message_id=" in output
