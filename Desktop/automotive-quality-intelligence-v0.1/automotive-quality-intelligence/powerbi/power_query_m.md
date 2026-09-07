# Power Query M starter query

Power BI Desktop can connect to PostgreSQL directly. For local development, the database is exposed on `localhost:5432`.

Create a blank query and use the Advanced Editor:

```powerquery
let
    Source = PostgreSQL.Database(
        "localhost:5432",
        "qualitydb",
        [CreateNavigationProperties=false]
    ),
    QualityView = Source{[Schema="public", Item="vw_quality_measurements"]}[Data],
    Typed = Table.TransformColumnTypes(
        QualityView,
        {
            {"event_time", type datetimezone},
            {"production_date", type date},
            {"iso_week", Int64.Type},
            {"target_value", type number},
            {"lower_spec_limit", type number},
            {"upper_spec_limit", type number},
            {"measured_value", type number},
            {"deviation", type number},
            {"absolute_deviation", type number},
            {"is_within_spec", type logical}
        }
    ),
    CleanStation = Table.TransformColumns(
        Typed,
        {{"station_code", Text.Upper, type text}}
    )
in
    CleanStation
```

Create two additional queries from:

- `vw_vehicle_quality`
- `vw_process_capability`
- `vw_process_capability_weekly`
- `vw_defect_pareto`

## Recommended Power BI model

For MVP, the views are intentionally BI-friendly and can be used directly.

For a larger production implementation, evolve toward a star schema:

- FactQualityMeasurement
- DimDate
- DimVehicle
- DimStation
- DimCharacteristic
- DimShift
- DimModel
