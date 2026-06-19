import json

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


def test_cli_email_dry_run(tmp_path, capsys):
    json_report = tmp_path / "latest.json"
    markdown_report = tmp_path / "latest.md"
    json_report.write_text(
        json.dumps(
            {
                "status": "OK",
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
    assert "DRY RUN" in capsys.readouterr().out

