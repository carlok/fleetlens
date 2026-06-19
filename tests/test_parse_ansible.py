from pathlib import Path

import pytest

from fleetlens.parse_ansible import load_raw_report, parse_apt_upgradable, parse_raw_report

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_success_fixture():
    hosts = load_raw_report(FIXTURES / "ansible_success.json")
    assert len(hosts) == 1
    assert hosts[0].host == "vm1"
    assert hosts[0].reachable is True


def test_parse_unreachable_fixture():
    hosts = load_raw_report(FIXTURES / "ansible_unreachable.json")
    assert hosts[0].reachable is False
    assert hosts[0].errors == ["ssh timeout"]


def test_parse_callback_stats():
    hosts = parse_raw_report({"stats": {"vm1": {"failures": 0, "unreachable": 1}}})
    assert hosts[0].host == "vm1"
    assert hosts[0].reachable is False


def test_parse_apt_upgradable_counts_security_lines():
    output = """Listing...
openssl/jammy-security 3.0 amd64 [upgradable from: 2.0]
vim/jammy-updates 9.0 amd64 [upgradable from: 8.2]
"""
    assert parse_apt_upgradable(output) == (2, 1)


def test_parse_invalid_raw_raises():
    with pytest.raises(ValueError):
        parse_raw_report({"unexpected": []})
