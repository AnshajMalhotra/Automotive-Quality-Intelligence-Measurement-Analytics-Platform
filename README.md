# Automotive Quality Report — Power BI

A focused portfolio project for quality reporting: **Power Query prepares inspection records; DAX calculates quality KPIs; a native Power BI report presents the results.** All data is synthetic and unrelated to Mercedes-Benz or any employer.

**Status:** Editable PBIP/PBIR source generated and locally checked. Power BI Desktop has not been run in this environment; opening, refreshing, and visual acceptance in Desktop remain required. This is not a prevalidated PBIX file.

## Open the report

1. Download or clone this repository to a local Windows folder.
2. Open `powerbi-quality-report/Quality.pbip` in current Power BI Desktop. Enable Power BI Project saving under Options → Preview features if your version requires it.
3. In **Transform data → Manage parameters**, set `DataFolder` to the absolute path of this project's `powerbi-quality-report/data` folder. The default is an example Windows path.
4. Choose **Close & Apply**, then **Refresh**. The local CSV requires no credentials.
5. Check the totals below with date/model/shift slicers cleared. Check that model and shift change the results and that the import audit stays constant. Save as PBIP, or use Desktop's Save As to create a PBIX.

The report contains four KPI cards, three slicers, a daily trend, a defect bar chart, a station table, and a refresh audit table. If a Desktop version rejects a visual definition, the complete bindings and layout are in `powerbi-quality-report/scripts/build_project.py`; recreate that visual using the same fields while retaining the semantic model.

## Expected full-data results

| KPI | Reference result |
|---|---:|
| Raw rows | 2,534 |
| Invalid rows quarantined | 4 |
| Older duplicates removed | 10 |
| Valid inspections | 2,520 |
| Failed inspections | 324 |
| Inspection defect rate | 12.8571% |
| Complete vehicles | 840 |
| First-pass vehicles | 562 |
| Vehicle first-pass yield | 66.9048% |
| Recorded rework hours | 159.5167 |

These results come from an independent Python reference, **not an executed DAX engine**. Compare Desktop results against `powerbi-quality-report/data/expected_kpis.json` before presenting the project as validated.

## How it works

**Power Query (M):** reads the CSV, selects required columns, trims whitespace, normalizes station/result/shift text, explicitly parses dates and numbers, quarantines invalid rows, and keeps the latest valid version per inspection ID. Buffering the sorted rows before distinct preserves the intended deduplication order. `RejectedRows` records the reason each invalid row failed. The audit accounts for every input row: raw = rejected + duplicates + clean.

**Model:** `FactInspection` contains one first-attempt inspection per vehicle per station. `FactVehicle` contains one vehicle summary. Date, model, and shift dimensions filter both facts; station filters inspections only. Relationships are single direction. A complete vehicle must have exactly three inspections at three distinct valid stations, with consistent date, model, and shift.

**DAX:** `COUNTROWS` counts inspections. `CALCULATE` adds a FAIL filter to count failed inspections. `KEEPFILTERS` intersects existing result filters. `DIVIDE` calculates ratios safely when there is no denominator. Vehicle FPY divides vehicles that pass every required station by complete vehicles. Rework minutes are summed and divided by 60. The optional seven-day measure recomputes failed/total inspections over the last seven calendar days—it does not average daily percentages.

**Filter meaning matters:** Vehicle FPY is always across all three stations for the selected date/model/shift cohort. Station and defect selections affect inspection measures, not this vehicle cohort measure. The card title says “all stations.” The import audit describes the whole refresh and intentionally ignores report slicers. The rolling measure anchors to the latest selected calendar date; select an August date range for this August sample.

## Explain it in an interview

> I built a small quality reporting project using simulated inspection data. I used Power Query to standardize the records, separate invalid rows, and remove older duplicates. In DAX, I separated inspection defect rate from vehicle first-pass yield because they answer different questions. The dashboard lets me compare stations and follow the daily trend. I also added an import audit so a good-looking KPI does not hide missing or rejected data.

German:

> Ich habe ein kleines Qualitätsdashboard mit simulierten Prüfdaten aufgebaut. In Power Query habe ich die Daten vereinheitlicht, fehlerhafte Zeilen getrennt und ältere Duplikate entfernt. Mit DAX unterscheide ich zwischen der Fehlerquote einzelner Prüfungen und der Erstpassquote vollständiger Fahrzeuge. Im Bericht kann ich Stationen vergleichen und den Verlauf über die Zeit verfolgen. Eine zusätzliche Importprüfung macht sichtbar, welche Daten tatsächlich in die Auswertung eingehen.

Use this description after you have opened, refreshed, and reviewed the report yourself. Do not claim production deployment, employer use, or measured business improvements.

## Assumptions and limits

- This is a first-attempt snapshot, not a repair lifecycle or repeated-inspection tracking system.
- There is one defect category per failed inspection. The defect rate is failed inspections / inspections, not defects per unit.
- Rework time is synthetic time associated with failed inspections, not proof that repairs were completed.
- Incomplete or inconsistent vehicle cohorts are excluded from FPY. Production reporting needs an agreed completeness and time-window policy.
- The existing platform's PostgreSQL view is measurement-grained. `powerbi-quality-report/power-query/PostgreSQLSource.example.m` demonstrates a connection only; it cannot replace this inspection source without an inspection ID, attempt definition, and vehicle/station mapping.

## Reproduce the checks

Python 3, standard library only:

```sh
python powerbi-quality-report/scripts/generate_data.py
python powerbi-quality-report/scripts/validate_data.py
python powerbi-quality-report/scripts/build_project.py
python -m unittest discover -s powerbi-quality-report/tests -v
```

`powerbi-quality-report/power-query/` contains the editable M source; `powerbi-quality-report/dax/measures.dax` contains all eight measures. The builder embeds those queries into the semantic model and writes the report. Python checks validate the reference calculations and file/field consistency; they do not replace Desktop acceptance.

## Microsoft references

- [Power BI Projects](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [PBIR report format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)
- [CALCULATE](https://learn.microsoft.com/en-us/dax/calculate-function-dax)
- [DIVIDE](https://learn.microsoft.com/en-us/dax/divide-function-dax)
