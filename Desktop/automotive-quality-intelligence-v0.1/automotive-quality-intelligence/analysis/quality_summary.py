#!/usr/bin/env python3
import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def in_spec(row):
    return float(row["lower_spec_limit"]) <= float(row["measured_value"]) <= float(row["upper_spec_limit"])


def capability(values, lsl, usl):
    if len(values) < 2:
        return {"cp": None, "cpk": None}
    sigma = statistics.stdev(values)
    mean = statistics.mean(values)
    if sigma == 0:
        return {"cp": None, "cpk": None}
    cp = (usl - lsl) / (6 * sigma)
    cpk = min((usl - mean) / (3 * sigma), (mean - lsl) / (3 * sigma))
    return {"cp": round(cp, 3), "cpk": round(cpk, 3)}


def summarize(path):
    rows = list(csv.DictReader(Path(path).open(encoding="utf-8")))
    vehicles = defaultdict(list)
    weekly = defaultdict(lambda: {"measurements": 0, "defects": 0})
    grouped = defaultdict(list)

    for row in rows:
        passed = in_spec(row)
        vehicles[row["vehicle_id"]].append(passed)
        date = datetime.fromisoformat(row["event_time"]).date()
        iso = date.isocalendar()
        week = f"{iso.year}-W{iso.week:02d}"
        weekly[week]["measurements"] += 1
        weekly[week]["defects"] += 0 if passed else 1
        grouped[(row["station_code"], row["characteristic_code"], row["unit"])].append(row)

    defects = sum(1 for r in rows if not in_spec(r))
    fpy_vehicles = sum(1 for results in vehicles.values() if all(results))

    capability_rows = []
    for (station, characteristic, unit), grp in sorted(grouped.items()):
        values = [float(r["measured_value"]) for r in grp]
        lsl = float(grp[0]["lower_spec_limit"])
        usl = float(grp[0]["upper_spec_limit"])
        cap = capability(values, lsl, usl)
        capability_rows.append({
            "station": station,
            "characteristic": characteristic,
            "unit": unit,
            "samples": len(values),
            **cap
        })

    weekly_rows = []
    for week, vals in sorted(weekly.items()):
        weekly_rows.append({
            "week": week,
            "measurements": vals["measurements"],
            "defects": vals["defects"],
            "failure_rate_pct": round(100 * vals["defects"] / vals["measurements"], 2)
        })

    return {
        "measurements": len(rows),
        "vehicles": len(vehicles),
        "out_of_spec_measurements": defects,
        "measurement_pass_rate_pct": round(100 * (len(rows) - defects) / len(rows), 2) if rows else None,
        "first_pass_yield_pct": round(100 * fpy_vehicles / len(vehicles), 2) if vehicles else None,
        "weekly_quality": weekly_rows,
        "process_capability": capability_rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    result = summarize(args.csv_path)
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
