"""
PDU power timeseries simulator.

Outputs data/samples/pdu_power.csv with columns:
  timestamp, eaton_power_w, eaton_current_a, eaton_pf,
  apc_output_w, apc_battery_pct, schneider_kw, schneider_load_pct, label

label=0 normal, label=1 anomaly (over-current spike or UPS transfer event).

Usage: python src/simulator/pdu_simulator.py --n-steps 500
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import numpy as np

COLUMNS = [
    "timestamp", "eaton_power_w", "eaton_current_a", "eaton_pf",
    "apc_output_w", "apc_battery_pct", "schneider_kw", "schneider_load_pct", "label",
]


def simulate(n_steps: int = 300, seed: int = 42) -> list[dict]:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    rows = []
    for i in range(n_steps):
        ts = t0 + i * 30
        label = 0
        eaton_p = 3200 + rng.normal(0, 80)
        apc_out = 5000 + rng.normal(0, 120)
        sch_kw = 9.5 + rng.normal(0, 0.3)
        # inject anomaly ~5 %
        if rng.random() < 0.05:
            kind = rng.integers(3)
            if kind == 0:
                eaton_p += rng.uniform(800, 2000)
                label = 1  # over-current
            elif kind == 1:
                apc_out -= rng.uniform(3000, 4000)
                label = 1  # UPS transfer
            else:
                sch_kw += rng.uniform(5, 12)
                label = 1  # load spike
        rows.append({
            "timestamp": ts,
            "eaton_power_w": round(eaton_p, 2),
            "eaton_current_a": round(eaton_p / 230.0, 3),
            "eaton_pf": round(float(rng.normal(0.95, 0.01)), 3),
            "apc_output_w": round(apc_out, 2),
            "apc_battery_pct": round(float(rng.normal(95, 1)), 1),
            "schneider_kw": round(sch_kw, 3),
            "schneider_load_pct": round(sch_kw / 15.0 * 100, 1),
            "label": label,
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-steps", type=int, default=300)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", default="data/samples")
    args = ap.parse_args()
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    rows = simulate(args.n_steps, args.seed)
    out = Path(args.out_dir) / "pdu_power.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    anomaly_count = sum(r["label"] for r in rows)
    print(f"Wrote {len(rows)} rows ({anomaly_count} anomalies) → {out}")


if __name__ == "__main__":
    main()
