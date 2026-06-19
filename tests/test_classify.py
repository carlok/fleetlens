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
