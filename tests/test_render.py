import json

from fleetlens.classify import classify_fleet
from fleetlens.models import HostResult
from fleetlens.render import render_markdown, write_json_report, write_markdown_report


def test_markdown_contains_summary():
    report = classify_fleet(
        [HostResult(host="vm1", apt={"upgradable_count": 0}, systemd={"failed_count": 0})]
    )
    markdown = render_markdown(report)
    assert "# FleetLens Report" in markdown
    assert "| vm1 | OK |" in markdown


def test_markdown_lists_package_updates():
    report = classify_fleet(
        [
            HostResult(
                host="vm1",
                apt={
                    "upgradable_count": 1,
                    "packages": ["openssl/jammy-security 3.0 amd64 [upgradable from: 2.0]"],
                },
                systemd={"failed_count": 0},
            )
        ]
    )
    markdown = render_markdown(report)
    assert "- Package updates:" in markdown
    assert "`openssl/jammy-security 3.0 amd64 [upgradable from: 2.0]`" in markdown


def test_write_reports(tmp_path):
    report = classify_fleet(
        [HostResult(host="vm1", apt={"upgradable_count": 0}, systemd={"failed_count": 0})]
    )
    json_path = tmp_path / "latest.json"
    markdown_path = tmp_path / "latest.md"
    write_json_report(report, json_path)
    write_markdown_report(report, markdown_path)
    assert json.loads(json_path.read_text())["status"] == "OK"
    assert markdown_path.read_text().startswith("# FleetLens Report")
