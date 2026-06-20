"""
Generic SNMP v2c collector.

Supports Eaton ePDU G3 and APC Smart-UPS SRT (and any SNMP v2c device).
Falls back to a simulator when host is unreachable.

No real credentials stored here. Load community strings from environment.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import time
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def _try_import_pysnmp() -> bool:
    try:
        return importlib.util.find_spec("pysnmp.hlapi") is not None
    except ModuleNotFoundError:
        return False
    """Return True if pysnmp is installed, without importing unused names."""
    # return importlib.util.find_spec("pysnmp.hlapi") is not None


class SNMPCollector:
    """Poll SNMP OIDs and return a flat metric dict.

    Parameters
    ----------
    host        : SNMP agent host (IP or hostname).
    community   : SNMP v2c community string — loaded from env, never hard-coded.
    port        : SNMP UDP port (default 161).
    oid_map     : dict mapping metric_name → OID string.
    simulate    : True = built-in simulator; None = auto-detect.
    """

    def __init__(
        self,
        host: str | None = None,
        community: str | None = None,
        port: int = 161,
        oid_map: dict[str, str] | None = None,
        simulate: bool | None = None,
        device_name: str = "generic",
    ) -> None:
        self.host = host or "PLACEHOLDER"
        self.community = community or os.environ.get("SNMP_COMMUNITY", "PLACEHOLDER")
        self.port = port
        self.oid_map = oid_map or {}
        self.device_name = device_name
        self._has_pysnmp = _try_import_pysnmp()
        self._simulate = (
            simulate
            if simulate is not None
            else (self.host == "PLACEHOLDER" or not self._host_reachable())
        )
        if self._simulate:
            logger.warning("SNMPCollector[%s]: SIMULATION mode.", device_name)
        self._rng = np.random.default_rng(hash(device_name) % (2**32))

    def _host_reachable(self) -> bool:
        import socket

        try:
            socket.setdefaulttimeout(1)
            socket.socket().connect((self.host, self.port))
            return True
        except Exception:
            return False

    def poll(self) -> dict[str, Any]:
        """Return {metric_name: value} dict for all configured OIDs."""
        if self._simulate:
            return self._sim_poll()
        if not self._has_pysnmp:
            logger.error("pysnmp not installed. pip install pysnmp")
            return {}
        return self._live_poll()

    def _live_poll(self) -> dict[str, Any]:
        from pysnmp.hlapi import (
            CommunityData,
            ContextData,
            ObjectIdentity,
            ObjectType,
            SnmpEngine,
            UdpTransportTarget,
            getCmd,
        )

        result = {}
        for name, oid in self.oid_map.items():
            for err_ind, err_stat, _, var_binds in getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.host, self.port), timeout=5, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            ):
                if err_ind or err_stat:
                    logger.warning("SNMP error for %s: %s %s", name, err_ind, err_stat)
                else:
                    result[name] = var_binds[0][1].prettyPrint()
        return result

    def _sim_poll(self) -> dict[str, Any]:
        """Return plausible simulated values keyed by OID name."""
        templates = {
            "voltage": (230.0, 2.0),
            "current": (10.0, 1.0),
            "power": (3000.0, 150.0),
            "energy": (9999.0, 5.0),
            "pf": (0.95, 0.02),
            "charge": (95.0, 1.0),
            "temp": (25.0, 1.0),
            "load": (60.0, 5.0),
            "freq": (50.0, 0.1),
            "runtime": (120.0, 2.0),
        }
        result = {"timestamp": time.time()}
        for name in self.oid_map:
            key = next((k for k in templates if k in name.lower()), None)
            mu, sigma = templates.get(key, (100.0, 5.0))
            result[name] = round(float(self._rng.normal(mu, sigma)), 3)
        return result
