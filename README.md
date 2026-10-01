# Automotive Quality Intelligence

A simple, visual overview of a manufacturing quality analytics project for automotive inspection and launch performance.

This repository brings together synthetic vehicle inspection data, data preparation, quality KPIs, and a Power BI-style reporting experience. It is designed to demonstrate how raw production data becomes actionable quality insight.

> The project is based on synthetic data and is intended for learning, portfolio use, and demonstration.

## What this project does

It answers practical quality questions such as:

- How many inspections pass or fail?
- Which stations have the highest defect rates?
- Are vehicles passing on the first attempt?
- Is quality improving over time?
- How can a BI report present the results clearly?

## End-to-end flow

```text
Synthetic inspection data
          |
          v
   Data preparation
          |
          v
   Quality modeling
          |
          v
  KPI calculation
          |
          v
 Power BI dashboard
```

## Core concepts

- Inspection data: vehicle and station-level quality records
- Defect analysis: failed inspections and recurring issues
- First Pass Yield (FPY): vehicles completing all required checks successfully
- Trend analysis: quality performance over time
- Dashboard reporting: a readable summary for operations and leadership

## Typical KPI outputs

- Raw inspections received
- Valid vs. rejected records
- Failed inspection rate
- Defect rate by category
- Complete vehicle count
- First-pass vehicle yield
- Rework hours or delay impact

## Repository structure

```text
.
├── Desktop/
│   └── automotive-quality-intelligence-v0.1/
│       └── automotive-quality-intelligence/
│           ├── api/
│           ├── db/
│           ├── generator/
│           ├── node-red/
│           ├── powerbi/
│           ├── docs/
│           └── tests/
├── powerbi-quality-report/
│   ├── data/
│   ├── dax/
│   ├── power-query/
│   ├── scripts/
│   ├── tests/
│   └── Quality.pbip
├── README.md
└── LICENSE
```

## Quick view of the reporting workflow

1. Data is prepared and cleaned.
2. The model organizes facts and dimensions.
3. DAX calculates the quality measures.
4. Power BI presents the results in a dashboard.

## Why this matters

This project demonstrates a real-world analytics pattern:

- collect measurement data
- validate and normalize it
- calculate business KPIs
- visualize the output for operational decisions

It is a practical example of how manufacturing quality information can be transformed into a decision-support story.

## How to use it

- Open the Power BI project under `powerbi-quality-report/`
- Review the data and transformation logic in `power-query/`
- Inspect the KPI definitions in `dax/`
- Use the Python scripts for data generation and validation

## Portfolio summary

This project is a compact example of automotive quality intelligence: a data pipeline, a quality model, and a reporting layer working together to make production performance understandable at a glance.

