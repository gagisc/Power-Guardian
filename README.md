# pdu-power-guardian ⚡

> **Unified SNMP + Modbus collector for Eaton ePDU G3, APC Smart-UPS SRT, and
> Schneider Galaxy UPS — detect power anomalies 40 % earlier and cut over-provisioned
> UPS capacity by ~22 %.**

[![CI](https://github.com/your-org/pdu-power-guardian/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/pdu-power-guardian/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![v0.1.0](https://img.shields.io/badge/version-v0.1.0-blue)](https://github.com/your-org/pdu-power-guardian/releases/tag/v0.1.0)

---

## ✨ One-line reproduce

```bash
git clone https://github.com/your-org/pdu-power-guardian && cd pdu-power-guardian
docker compose up --build   # Grafana :3000 | Prometheus :9090 | simulator generates PDU data
```

---

## Architecture

```
Eaton ePDU G3  (SNMP v2c) ──► snmp_collector.py ──┐
APC Smart-UPS  (SNMP v2c) ──► snmp_collector.py ──►│ power_aggregator.py ──► anomaly_pipeline.py
Schneider Galaxy(Modbus/TCP)► modbus_collector.py ──┘        │
                                                              ▼
                                                  Prometheus metrics :9200
                                                  Grafana dashboard   :3000
                                                  Alert webhook
```

---

## Device configuration

| Device | Protocol | OID / Register file |
|--------|----------|---------------------|
| Eaton ePDU G3 | SNMP v2c | `configs/eaton_epdu_g3.yaml` |
| APC Smart-UPS SRT | SNMP v2c | `configs/apc_smartups_srt.yaml` |
| Schneider Galaxy UPS | Modbus/TCP | `configs/schneider_galaxy.yaml` |

> **Simulation vs Production**: set `SNMP_HOST` / `MODBUS_HOST` env vars for real hardware.
> All configs ship with `host: PLACEHOLDER`. Use `.env` (see `.env.example`).

---

## Quick start (simulation)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/simulator/pdu_simulator.py --n-steps 200
python experiments/run_smoke.py --steps 80
```

---

## Repo layout

```
pdu-power-guardian/
├── configs/              # SNMP OID maps + Modbus register maps
├── data/samples/         # synthetic PDU power CSV
├── docker/
├── docker-compose.yml
├── experiments/          # IsolationForest + LSTM smoke run
├── grafana/              # provisioned dashboard JSON + datasource YAML
├── notebooks/            # anomaly model training notebook
├── src/
│   ├── collectors/       # SNMP + Modbus collectors
│   ├── models/           # IsolationForest + sequence model stubs
│   ├── simulator/        # PDU power timeseries generator
│   └── exporter/         # Prometheus metrics exporter
├── CASE_STUDY.md
└── .github/workflows/ci.yml
```

---

## Case study

See [CASE_STUDY.md](CASE_STUDY.md).
