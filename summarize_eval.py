#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


def first_metric(metrics: dict):
    # Prefer common accuracy keys.
    for k in ["acc,none", "acc_norm,none", "exact_match,none", "f1,none"]:
        if k in metrics:
            return k, metrics[k]
    for k, v in metrics.items():
        if isinstance(v, (int, float)):
            return k, v
    return "", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    rows = []

    for p in sorted(input_dir.glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        results = data.get("results", {})
        for task, metrics in results.items():
            metric_name, metric_val = first_metric(metrics)
            rows.append({
                "file": p.name,
                "task": task,
                "metric": metric_name,
                "value": metric_val,
            })

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "task", "metric", "value"])
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()