from fleetlens.classify import classify_disk_usage, classify_fleet
from fleetlens.models import HostResult, Status


def test_disk_thresholds():
    assert classify_disk_usage(84) == Status.OK
    assert classify_disk_usage(85) == Status.WARNING
    assert classify_disk_usage(95) == Status.CRITICAL


def test_global_ok_status():
    report = classify_fleet(
        [HostResult(host="vm1", apt={"upgradable_count": 0}, systemd={"failed_count": 0})]
    )
    assert report.status == Status.OK


def test_updates_and_reboot_are_warning():
    report = classify_fleet(
        [
            HostResult(
                host="vm1",
                apt={"upgradable_count": 1},
                reboot_required=True,
                systemd={"failed_count": 0},
            )
        ]
    )
    assert report.status == Status.WARNING
    assert "vm1: updates available" in report.warnings
    assert "vm1: reboot required" in report.warnings


def test_unreachable_is_critical():
    report = classify_fleet([HostResult(host="vm2", reachable=False, sudo_ok=False)])
    assert report.status == Status.CRITICAL
    assert any("unreachable" in item for item in report.criticals)


def test_empty_fleet_is_unknown():
    report = classify_fleet([])
    assert report.status == Status.UNKNOWN


def test_disk_status_tolerates_template_whitespace():
    from pathlib import Path

    from fleetlens.parse_ansible import load_raw_report

    fixture = Path(__file__).parent / "fixtures" / "ansible_template_whitespace.json"
    report = classify_fleet(load_raw_report(fixture))
    assert report.status == Status.CRITICAL
    assert "vm1: / disk critical" in report.criticals
    assert "vm1: /var disk warning" in report.warnings


def test_failed_check_is_warning():
    report = classify_fleet(
        [
            HostResult(
                host="vm1",
                apt={"upgradable_count": 0, "apt_list_rc": "100"},
                systemd={"failed_count": 0, "rc": 0},
                journal={"error_count": 0, "rc": 1},
            )
        ]
    )
    assert report.status == Status.WARNING
    assert "vm1: apt check failed (rc=100)" in report.warnings
    assert "vm1: journal check failed (rc=1)" in report.warnings
    assert not any("systemd" in item for item in report.warnings)


def test_unreachable_host_does_not_report_failed_checks():
    report = classify_fleet(
        [HostResult(host="vm2", reachable=False, apt={"apt_list_rc": 1}, systemd={"rc": 1})]
    )
    assert report.status == Status.CRITICAL
    assert report.warnings == []


def test_missing_host_placeholder_is_critical():
    from fleetlens.parse_ansible import parse_raw_report

    hosts = parse_raw_report(
        {"hosts": [{"host": "vm3", "reachable": False, "errors": ["no result collected"]}]}
    )
    report = classify_fleet(hosts)
    assert report.status == Status.CRITICAL
    assert "vm3: no result collected" in report.criticals
