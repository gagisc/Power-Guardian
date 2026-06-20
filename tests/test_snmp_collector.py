import sys
import importlib
import pytest

sys.path.insert(0, "src")

from collectors.snmp_collector import SNMPCollector, _try_import_pysnmp


def test_try_import_pysnmp_false(monkeypatch):
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)
    assert _try_import_pysnmp() is False


def test_snmp_init_defaults(monkeypatch):
    monkeypatch.delenv("SNMP_COMMUNITY", raising=False)
    c = SNMPCollector(simulate=True)
    assert c.community == "PLACEHOLDER"
    assert c.port == 161
    assert isinstance(c.oid_map, dict)


def test_snmp_sim_poll_values():
    c = SNMPCollector(
        oid_map={"voltage_phase1": "1.2.3.4"},
        simulate=True,
        device_name="testdev",
    )
    r = c.poll()
    assert "voltage_phase1" in r
    assert isinstance(r["voltage_phase1"], float)


def test_snmp_host_unreachable_forces_sim(monkeypatch):
    monkeypatch.setattr(SNMPCollector, "_host_reachable", lambda self: False)
    c = SNMPCollector(simulate=None)
    assert c._simulate is True


def test_snmp_live_poll_missing_pysnmp(monkeypatch):
    monkeypatch.setattr(SNMPCollector, "_host_reachable", lambda self: True)
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)

    c = SNMPCollector(simulate=False, oid_map={"x": "1.2.3"})
    out = c.poll()
    assert out == {}
