"""
Prometheus metrics exporter for PDU power data.

Exposes SNMP and Modbus readings as Prometheus gauges on :9200/metrics.

Usage: python src/exporter/prometheus_exporter.py
"""
from __future__ import annotations
import logging, time, os
logger = logging.getLogger(__name__)

try:
    from prometheus_client import Gauge, start_http_server  # type: ignore
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    logger.warning("prometheus_client not installed.")

GAUGES: dict = {}

METRIC_DEFS = {
    "pdu_eaton_power_watts":       ("Eaton ePDU G3 inlet power", ["device"]),
    "pdu_eaton_current_amps":      ("Eaton ePDU G3 inlet current", ["device"]),
    "pdu_eaton_power_factor":      ("Eaton ePDU G3 power factor", ["device"]),
    "pdu_apc_output_watts":        ("APC Smart-UPS SRT output power", ["device"]),
    "pdu_apc_battery_charge_pct":  ("APC Smart-UPS SRT battery charge %", ["device"]),
    "pdu_schneider_kw":            ("Schneider Galaxy output kW", ["device"]),
    "pdu_schneider_load_pct":      ("Schneider Galaxy load %", ["device"]),
    "pdu_anomaly_score":           ("PDU anomaly score (IsolationForest)", ["device"]),
}


def init_gauges():
    if not HAS_PROMETHEUS:
        return
    for name, (desc, labels) in METRIC_DEFS.items():
        GAUGES[name] = Gauge(name, desc, labels)


def export_metrics(metrics: dict, device: str = "sim"):
    if not HAS_PROMETHEUS:
        logger.info("(dry-run) metrics: %s", metrics)
        return
    mapping = {
        "eaton_power_w":      "pdu_eaton_power_watts",
        "eaton_current_a":    "pdu_eaton_current_amps",
        "eaton_pf":           "pdu_eaton_power_factor",
        "apc_output_w":       "pdu_apc_output_watts",
        "apc_battery_pct":    "pdu_apc_battery_charge_pct",
        "schneider_kw":       "pdu_schneider_kw",
        "schneider_load_pct": "pdu_schneider_load_pct",
    }
    for src, dst in mapping.items():
        if src in metrics and dst in GAUGES:
            GAUGES[dst].labels(device=device).set(metrics[src])


def main():
    port = int(os.environ.get("PROMETHEUS_PORT", 9200))
    if HAS_PROMETHEUS:
        init_gauges(); start_http_server(port)
        logger.info("Prometheus exporter started on :%d", port)
    # Import collector stubs (simulation mode)
    import sys; sys.path.insert(0,"src")
    from collectors.snmp_collector import SNMPCollector
    from collectors.modbus_collector import ModbusCollector
    snmp_eaton = SNMPCollector(device_name="eaton_epdu")
    snmp_apc   = SNMPCollector(device_name="apc_smartups")
    modbus_sch = ModbusCollector()
    while True:
        m = {}
        m.update(snmp_eaton.poll())
        m.update(snmp_apc.poll())
        m.update(modbus_sch.poll())
        export_metrics(m)
        time.sleep(30)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
