# DAX Measures

Assume these tables are loaded from PostgreSQL:

- `vw_quality_measurements`
- `vw_vehicle_quality`
- `vw_process_capability`

Create these measures in Power BI.

```DAX
Total Measurements =
COUNTROWS(vw_quality_measurements)
```

```DAX
Total Vehicles =
DISTINCTCOUNT(vw_quality_measurements[vehicle_id])
```

```DAX
Out of Spec Measurements =
CALCULATE(
    [Total Measurements],
    vw_quality_measurements[is_within_spec] = FALSE()
)
```

```DAX
Measurement Pass Rate % =
DIVIDE(
    [Total Measurements] - [Out of Spec Measurements],
    [Total Measurements],
    0
)
```

```DAX
Vehicles First Pass =
CALCULATE(
    COUNTROWS(vw_vehicle_quality),
    vw_vehicle_quality[first_pass] = TRUE()
)
```

```DAX
First Pass Yield % =
DIVIDE(
    [Vehicles First Pass],
    COUNTROWS(vw_vehicle_quality),
    0
)
```

```DAX
Defects per 100 Vehicles =
DIVIDE(
    SUM(vw_vehicle_quality[defect_count]) * 100,
    COUNTROWS(vw_vehicle_quality),
    0
)
```

```DAX
Average Absolute Deviation =
AVERAGE(vw_quality_measurements[absolute_deviation])
```

```DAX
Cpk Average =
AVERAGE(vw_process_capability[cpk])
```

```DAX
Launch Week =
"Week " & FORMAT(MAX(vw_quality_measurements[iso_week]), "0")
```

## Suggested KPI thresholds

These are demonstration thresholds, not Mercedes-Benz production acceptance criteria:

- FPY >= 98%: green
- FPY 95–98%: amber
- FPY < 95%: red
- Cpk >= 1.33: capable
- Cpk 1.00–1.33: monitor
- Cpk < 1.00: investigate

Always label these as project/demo thresholds.
