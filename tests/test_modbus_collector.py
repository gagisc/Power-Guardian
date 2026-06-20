import sys
import importlib
import pytest

sys.path.insert(0, "src")

from collectors.modbus_collector import ModbusCollector


def test_modbus_init_defaults(monkeypatch):
    monkeypatch.delenv("SCHNEIDER_GALAXY_HOST", raising=False)
    c = ModbusCollector(simulate=True)
    assert c.host == "PLACEHOLDER"
    assert c.port == 502
    assert c.unit_id == 1


def test_modbus_sim_poll_values():
    c = ModbusCollector(simulate=True)
    r = c.poll()
    assert "output_power_kw" in r
    assert isinstance(r["output_power_kw"], float)


def test_modbus_host_unreachable_forces_sim(monkeypatch):
    monkeypatch.setattr(ModbusCollector, "_host_reachable", lambda self: False)
    c = ModbusCollector(simulate=None)
    assert c._simulate is True


def test_modbus_live_poll_missing_pymodbus(monkeypatch):
    monkeypatch.setattr(ModbusCollector, "_host_reachable", lambda self: True)

    def fake_import(name, *args, **kwargs):
        raise ImportError

    monkeypatch.setattr(importlib, "import_module", fake_import)

    c = ModbusCollector(simulate=False)
    out = c.poll()
    assert out == {}
