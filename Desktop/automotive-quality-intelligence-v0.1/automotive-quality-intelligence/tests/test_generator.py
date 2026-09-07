import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "generator"))

from generate_data import generate_row, load_config


def test_generated_measurement_has_valid_spec_limits():
    config = load_config(ROOT / "generator" / "config.json")
    row = generate_row(config, 10, datetime.now(timezone.utc), 42, 100)
    assert row["upper_spec_limit"] > row["lower_spec_limit"]


def test_generated_shift_is_valid():
    config = load_config(ROOT / "generator" / "config.json")
    row = generate_row(config, 10, datetime.now(timezone.utc), 42, 100)
    assert row["shift_code"] in {"A", "B", "C"}
