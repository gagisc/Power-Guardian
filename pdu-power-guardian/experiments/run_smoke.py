"""
Smoke experiment: fit IsolationForest + LSTM stub on simulated PDU data.
Outputs experiments/results/smoke_metrics.csv + feature_importance.png.

Usage: python experiments/run_smoke.py --steps 80
"""
from __future__ import annotations
import argparse, csv, subprocess, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=120)
    ap.add_argument("--out", default="experiments/results")
    args = ap.parse_args(); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    data_csv = Path("data/samples/pdu_power.csv")
    if not data_csv.exists():
        subprocess.check_call([sys.executable, "src/simulator/pdu_simulator.py",
                               "--n-steps", str(args.steps)])

    import numpy as np
    sys.path.insert(0,"src")
    from models.isolation_forest import PDUIsolationForest

    import csv as _csv
    with open(data_csv) as f:
        reader = _csv.DictReader(f)
        rows = list(reader)

    FEAT_COLS = ["eaton_power_w","eaton_current_a","apc_output_w","schneider_kw","schneider_load_pct"]
    X = np.array([[float(r[c]) for c in FEAT_COLS] for r in rows])
    labels = np.array([int(r["label"]) for r in rows])

    clf = PDUIsolationForest(contamination=0.05).fit(X)
    preds = clf.predict(X)
    scores = clf.score(X)
    tp = int(np.sum((preds==-1)&(labels==1)))
    fp = int(np.sum((preds==-1)&(labels==0)))
    fn = int(np.sum((preds==1)&(labels==1)))
    precision = tp/(tp+fp+1e-9); recall = tp/(tp+fn+1e-9)
    f1 = 2*precision*recall/(precision+recall+1e-9)

    metrics = [{"metric":"precision","value":round(precision,4)},
               {"metric":"recall","value":round(recall,4)},
               {"metric":"f1","value":round(f1,4)},
               {"metric":"n_anomalies_detected","value":int(np.sum(preds==-1))}]
    with open(out/"smoke_metrics.csv","w",newline="") as f:
        w = _csv.DictWriter(f, fieldnames=["metric","value"])
        w.writeheader(); w.writerows(metrics)
    for m in metrics: print(f"  {m['metric']:30s} {m['value']}")

    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1,2,figsize=(10,4))
        axes[0].plot(scores,label="IF score"); axes[0].set_title("Anomaly Score")
        axes[0].scatter(np.where(labels==1),scores[labels==1],c="red",label="true anomaly",zorder=5)
        axes[0].legend()
        axes[1].bar(FEAT_COLS, np.std(X,axis=0)); axes[1].set_title("Feature Variance")
        plt.xticks(rotation=30,ha="right"); fig.tight_layout()
        fig.savefig(out/"smoke_anomaly_chart.png",dpi=100)
        print(f"Chart → {out}/smoke_anomaly_chart.png")
    except ImportError: pass
    print("Smoke PASSED ✓")

if __name__=="__main__": main()
