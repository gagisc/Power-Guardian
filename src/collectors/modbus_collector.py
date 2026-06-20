"""
Modbus/TCP collector for Schneider Galaxy UPS.

Falls back to simulator when host is unreachable or pymodbus is not installed.
"""

from __future__ import annotations

import logging
import os
import time

import numpy as np

logger = logging.getLogger(__name__)

REGISTER_MAP = {
    "input_voltage_v": (0x0001, 0.1),
    "input_frequency_hz": (0x0003, 0.1),
    "output_voltage_v": (0x0010, 0.1),
    "output_current_a": (0x0012, 0.1),
    "output_power_kva": (0x0014, 0.01),
    "output_power_kw": (0x0016, 0.01),
    "output_load_pct": (0x0018, 1),
    "battery_voltage_v": (0x0020, 0.1),
    "battery_charge_pct": (0x0022, 1),
    "battery_temp_c": (0x0024, 0.1),
    "bypass_voltage_v": (0x0030, 0.1),
}


class ModbusCollector:
    """Poll Modbus/TCP input registers from a Schneider Galaxy UPS.

    Parameters
    ----------
    host     : Modbus TCP host — loaded from SCHNEIDER_GALAXY_HOST env var.
    port     : Modbus TCP port (default 502).
    unit_id  : Modbus slave/unit ID (default 1).
    simulate : None = auto-detect.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int = 502,
        unit_id: int = 1,
        simulate: bool | None = None,
    ) -> None:
        self.host = host or os.environ.get("SCHNEIDER_GALAXY_HOST", "PLACEHOLDER")
        self.port = port
        self.unit_id = unit_id
        self._simulate = (
            simulate
            if simulate is not None
            else (self.host == "PLACEHOLDER" or not self._host_reachable())
        )
        self._rng = np.random.default_rng(7)
        if self._simulate:
            logger.warning("ModbusCollector: SIMULATION mode.")

    def _host_reachable(self) -> bool:
        import socket

        try:
            socket.setdefaulttimeout(1)
            socket.socket().connect((self.host, self.port))
            return True
        except Exception:
            return False

    def poll(self) -> dict:
        return self._sim_poll() if self._simulate else self._live_poll()

    def _live_poll(self) -> dict:
        try:
            from pymodbus.client import ModbusTcpClient  # type: ignore
        except ImportError:
            logger.error("pip install pymodbus")
            return {}
        client = ModbusTcpClient(self.host, port=self.port)
        client.connect()
        result = {"timestamp": time.time()}
        for name, (addr, scale) in REGISTER_MAP.items():
            rr = client.read_input_registers(addr, count=1, slave=self.unit_id)
            if not rr.isError():
                result[name] = rr.registers[0] * scale
            else:
                logger.warning("Modbus read error for %s @ 0x%04X", name, addr)
        client.close()
        return result

    def _sim_poll(self) -> dict:
        result = {"timestamp": time.time()}
        sim = {
            "input_voltage_v": 230.0,
            "input_frequency_hz": 50.0,
            "output_voltage_v": 230.0,
            "output_current_a": 43.5,
            "output_power_kva": 10.0,
            "output_power_kw": 9.5,
            "output_load_pct": 63.0,
            "battery_voltage_v": 216.0,
            "battery_charge_pct": 94.0,
            "battery_temp_c": 26.0,
            "bypass_voltage_v": 230.0,
        }
        noises = {
            "voltage": 2.0,
            "current": 0.5,
            "power": 0.3,
            "kw": 0.2,
            "pct": 1.0,
            "freq": 0.05,
            "temp": 0.5,
        }
        for name, base in sim.items():
            key = next((k for k in noises if k in name), None)
            sigma = noises.get(key, 0.5)
            result[name] = round(float(base + self._rng.normal(0, sigma)), 3)
        return result
