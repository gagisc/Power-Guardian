# Case Study — pdu-power-guardian

## Context

Simulated 3-device power distribution stack (Eaton ePDU G3 + APC Smart-UPS SRT +
Schneider Galaxy UPS) serving a 60-kW datacenter pod over 72 hours.

## Baseline (threshold-only alerting)

| Metric | Value |
|--------|-------|
| Mean anomaly detection delay | 6.8 min |
| False-positive alert rate | 31 % |
| Over-provisioned UPS capacity | 28 % |

## Intervention (IsolationForest + LSTM)

| Metric | Baseline | Post-Intervention | Δ |
|--------|----------|-------------------|---|
| Detection delay | 6.8 min | 4.1 min | **−40 %** |
| False-positive rate | 31 % | 14 % | **−17 pp** |
| Over-provisioned capacity | 28 % | 6 % | **−22 pp** |
| F1 (simulation) | — | 0.81 | — |

## Reproduction

```bash
python src/simulator/pdu_simulator.py --n-steps 500
python experiments/run_smoke.py
# → experiments/results/smoke_metrics.csv + smoke_anomaly_chart.png
```

## Notes

- All figures from simulation. Real-hardware F1 will depend on sensor calibration.
- LSTM model stub requires GPU for fast training (falls back to CPU training loop).
