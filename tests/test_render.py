import json

from fleetlens.classify import classify_fleet
from fleetlens.models import HostResult
from fleetlens.render import (
    render_markdown,
    render_terminal_summary,
    write_json_report,
    write_markdown_report,
)


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


def test_terminal_summary_highlights_host_findings():
    report = classify_fleet(
        [
            HostResult(
                host="vm1",
                apt={
                    "upgradable_count": 6,
                    "packages": [
                        "openssl/jammy-security 3.0 amd64 [upgradable from: 2.0]",
                        "vim/jammy-updates 9.0 amd64 [upgradable from: 8.2]",
                        "curl/jammy-updates 8.0 amd64 [upgradable from: 7.0]",
                        "git/jammy-updates 2.0 amd64 [upgradable from: 1.0]",
                        "bash/jammy-updates 5.0 amd64 [upgradable from: 4.0]",
                        "tmux/jammy-updates 3.0 amd64 [upgradable from: 2.0]",
                    ],
                },
                systemd={"failed_count": 1},
            )
        ]
    )
    summary = render_terminal_summary(report)
    assert "FleetLens status: WARNING" in summary
    assert "- vm1: WARNING" in summary
    assert "updates available: 6 packages: openssl, vim, curl, git, bash, +1 more" in summary
    assert "failed systemd units: 1 unit" in summary


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
