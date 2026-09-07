# Automotive Quality Intelligence & Measurement Analytics Platform

A reusable, end-to-end quality analytics project for manufacturing measurement data.

The project simulates an automotive vehicle-launch quality scenario, streams or batches measurement events through Node-RED/FastAPI, stores them in PostgreSQL, and exposes BI-ready views for Power BI.

> **Important:** All production and vehicle data in this repository is synthetic. The project is independent and is not affiliated with, endorsed by, or built from proprietary data of Mercedes-Benz or any other manufacturer.

## What the project demonstrates

- Automotive/manufacturing quality analytics
- Measurement tolerance evaluation
- First Pass Yield (FPY)
- Defect rate and Pareto analysis
- Process capability (Cp / Cpk)
- Launch-quality stabilization over time
- Power BI + DAX + Power Query M
- Python-based synthetic data generation
- Node-RED + JavaScript ingestion/validation
- PostgreSQL quality data model
- Linux-based Docker containers
- REST API integration

## Architecture

```text
Data Generator / Future Real Source
              |
              v
        Node-RED :1880
   JavaScript validation
              |
              v
         FastAPI :8000
              |
              v
       PostgreSQL :5432
              |
              v
          Power BI
```

Batch loading can also go directly to the FastAPI endpoint.

## Quick start

### 1. Clone and configure

```bash
git clone <your-repository-url>
cd automotive-quality-intelligence
cp .env.example .env
```

### 2. Start the platform

```bash
docker compose up -d --build
```

Services:

- PostgreSQL: `localhost:5432`
- API docs: `http://localhost:8000/docs`
- Node-RED: `http://localhost:1880`

### 3. Generate useful launch-quality data

For a fast 25,000-row seed:

```bash
python generator/generate_data.py \
  --rows 25000 \
  --days 42 \
  --mode api \
  --endpoint http://localhost:8000/measurements/batch
```

For a visible event-by-event Node-RED stream:

```bash
python generator/generate_data.py \
  --rows 500 \
  --mode nodered \
  --endpoint http://localhost:1880/ingest/measurement \
  --delay-ms 100
```

For an offline CSV:

```bash
python generator/generate_data.py \
  --rows 25000 \
  --days 42 \
  --mode csv \
  --output sample-data/generated_measurements.csv
```

## Verify the result

Open:

```text
http://localhost:8000/kpis/overview?days=60
```

and:

```text
http://localhost:8000/kpis/pareto?days=60&limit=10
```

The synthetic model intentionally has higher process variability early in the launch window and stabilizes over time, so the project produces a meaningful quality-improvement signal.

## Deterministic sample result

With the default seed (`47`), 25,000 measurements over 42 days produce a reproducible demonstration dataset. The current reference sample contains:

- 25,000 measurements
- 3,572 vehicles
- 98.01% measurement pass rate
- 86.93% vehicle first-pass yield
- launch-week failure rate declining from about 4.8% to below 1%

These are **simulation outputs**, not manufacturing benchmarks or acceptance targets.

## PostgreSQL connection for Power BI

Use:

- Server: `localhost:5432`
- Database: `qualitydb`
- User: `quality_user`
- Password: `quality_password`

Recommended views:

- `vw_quality_measurements`
- `vw_vehicle_quality`
- `vw_process_capability`
- `vw_process_capability_weekly`
- `vw_defect_pareto`

See:
- `powerbi/power_query_m.md`
- `powerbi/dax_measures.md`
- `powerbi/dashboard_blueprint.md`

## Core quality KPIs

### Measurement pass rate

```text
in-spec measurements / total measurements
```

### First Pass Yield (project definition)

```text
vehicles with zero out-of-spec measurements / total vehicles
```

### Cp

```text
(USL - LSL) / (6 × sigma)
```

### Cpk

```text
min((USL - mean)/(3 × sigma), (mean - LSL)/(3 × sigma))
```

The demo project uses Cpk as a process-capability indicator. Production acceptance rules depend on the actual organization/process and are intentionally not claimed here.

## Repository structure

```text
.
├── api/                       FastAPI ingestion service
├── db/                        PostgreSQL schema and BI views
├── generator/                 Synthetic launch-quality simulator
├── node-red/                  Node-RED flow with JavaScript validation
├── powerbi/                   DAX, M and dashboard blueprint
├── docs/                      Architecture and event contract
├── tests/                     Basic tests
├── docker-compose.yml
└── README.md
```

## Roadmap

### v0.1 — End-to-end platform
- [x] Measurement event contract
- [x] Synthetic launch-quality generator
- [x] Node-RED validation gateway
- [x] FastAPI ingestion
- [x] PostgreSQL model
- [x] BI views
- [x] DAX measure pack
- [x] Power Query M starter query

### v0.2 — Statistical Process Control
- [ ] X-bar / control-limit views
- [ ] rolling sigma
- [ ] Western Electric rule detection
- [ ] process drift alerts

### v0.3 — Rework + root-cause analytics
- [ ] repair events
- [ ] defect categories
- [ ] station/shift correlation
- [ ] supplier/component dimensions

### v0.4 — Real-time / IoT
- [ ] MQTT source
- [ ] equipment/sensor telemetry
- [ ] live monitoring page
- [ ] anomaly scoring

## Portfolio statement

This project is intended to demonstrate how IoT/data-pipeline experience can be applied to manufacturing quality and measurement technology. It is designed as a reusable architecture rather than a one-off dashboard.
