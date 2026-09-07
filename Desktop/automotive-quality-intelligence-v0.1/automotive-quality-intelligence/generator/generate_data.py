#!/usr/bin/env python3
import argparse
import csv
import json
import random
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config.json"


def load_config(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def shift_for_hour(hour):
    if 6 <= hour < 14:
        return "A"
    if 14 <= hour < 22:
        return "B"
    return "C"


def characteristic_catalog(config):
    catalog = []
    for station in config["stations"]:
        for characteristic in station["characteristics"]:
            catalog.append((station, characteristic))
    return catalog


def launch_factor(day_offset, horizon_days):
    # Simulates launch stabilization: early production has more variation.
    if horizon_days <= 1:
        return 1.0
    progress = max(0.0, min(1.0, day_offset / horizon_days))
    return 2.35 - 1.35 * progress


def generate_row(config, index, start_time, horizon_days, total_rows):
    catalog = characteristic_catalog(config)
    characteristics_per_vehicle = len(catalog)
    vehicle_num = index // characteristics_per_vehicle + 1
    characteristic_index = index % characteristics_per_vehicle
    station, c = catalog[characteristic_index]

    total_vehicles = max(1, (total_rows + characteristics_per_vehicle - 1) // characteristics_per_vehicle)
    production_progress = 0.0 if total_vehicles == 1 else (vehicle_num - 1) / (total_vehicles - 1)
    base_seconds = production_progress * max(1, horizon_days * 24 * 3600 - 3600)
    station_offset_seconds = characteristic_index * 7 * 60
    jitter_seconds = random.randint(0, 120)
    event_time = start_time + timedelta(seconds=base_seconds + station_offset_seconds + jitter_seconds)

    day_offset = (event_time - start_time).total_seconds() / 86400.0
    variability = c["sigma"] * launch_factor(day_offset, horizon_days)

    # Small, realistic process shifts by shift and station.
    shift = shift_for_hour(event_time.hour)
    shift_bias = {"A": 0.0, "B": 0.12, "C": -0.08}[shift] * variability
    station_bias = {"BODY": 0.10, "PAINT": -0.05, "ASSEMBLY": 0.03, "EOL": 0.0}.get(station["station_code"], 0.0) * variability

    measured = random.gauss(c["target"] + shift_bias + station_bias, variability)

    # Inject occasional special-cause defects.
    if random.random() < c.get("defect_bias", 0.01):
        direction = random.choice([-1, 1])
        excursion = random.uniform(1.1, 2.2) * max(
            c["usl"] - c["target"], c["target"] - c["lsl"]
        )
        measured = c["target"] + direction * excursion

    return {
        "event_time": event_time.isoformat(),
        "vehicle_id": f"VH{vehicle_num:07d}",
        "model": config["models"][(vehicle_num - 1) % len(config["models"])],
        "station_code": station["station_code"],
        "characteristic_code": c["code"],
        "shift_code": shift,
        "target_value": c["target"],
        "lower_spec_limit": c["lsl"],
        "upper_spec_limit": c["usl"],
        "measured_value": round(measured, 4),
        "unit": c["unit"],
        "source": "synthetic-launch-simulator",
        "batch_id": f"LAUNCH-{start_time.date().isoformat()}",
    }


def post_json(url, payload):
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def main():
    parser = argparse.ArgumentParser(description="Automotive quality data generator")
    parser.add_argument("--rows", type=int, default=25000)
    parser.add_argument("--days", type=int, default=42)
    parser.add_argument("--seed", type=int, default=47)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--mode", choices=["csv", "api", "nodered"], default="csv")
    parser.add_argument("--endpoint", default="http://localhost:8000/measurements/batch")
    parser.add_argument("--output", default="sample-data/generated_measurements.csv")
    parser.add_argument("--delay-ms", type=int, default=0)
    args = parser.parse_args()

    random.seed(args.seed)
    config = load_config(args.config)
    start_time = datetime.now(timezone.utc) - timedelta(days=args.days)
    rows = [generate_row(config, i, start_time, args.days, args.rows) for i in range(args.rows)]

    if args.mode == "csv":
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {output}")
        return

    if args.mode == "api":
        batch_size = 1000
        accepted = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            result = post_json(args.endpoint, batch)
            accepted += len(batch)
            print(f"Sent {accepted}/{len(rows)} rows: {result}")
        return

    for i, row in enumerate(rows, start=1):
        result = post_json(args.endpoint, row)
        if i % 50 == 0 or i == len(rows):
            print(f"Streamed {i}/{len(rows)} rows: {result}")
        if args.delay_ms:
            time.sleep(args.delay_ms / 1000.0)


if __name__ == "__main__":
    main()
