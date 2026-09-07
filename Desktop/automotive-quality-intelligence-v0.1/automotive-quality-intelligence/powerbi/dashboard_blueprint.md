# Power BI Dashboard Blueprint

## Page 1 — Quality Overview
KPI cards:
- First Pass Yield %
- Measurement Pass Rate %
- Out of Spec Measurements
- Defects per 100 Vehicles

Visuals:
- Line: FPY by production date / launch week
- Bar: defect count by station
- Stacked bar: pass/fail by model
- Matrix: station × shift with failure rate
- Slicers: date, model, station, shift

## Page 2 — Measurement Technology
Visuals:
- Histogram / distribution by characteristic
- Trend of measured value with LSL/Target/USL
- Cpk by characteristic
- Average absolute deviation by station
- Table of current out-of-spec measurements

## Page 3 — Defect Pareto & Drill-down
Visuals:
- Pareto: defect count by characteristic
- Cumulative defect percentage
- Defects by shift
- Drill-through table to vehicle ID and timestamp

## Page 4 — Launch Quality Monitoring
Visuals:
- Weekly failure rate
- FPY stabilization curve
- Cpk development by launch week (`vw_process_capability_weekly`)
- Heatmap: station × launch week
- "Top issue this week" card

## Page 5 — Data Quality / Pipeline Health
Visuals:
- records received per hour/day
- missing/invalid event count (future enhancement)
- source distribution
- latest event timestamp
- ingestion latency (future enhancement)
