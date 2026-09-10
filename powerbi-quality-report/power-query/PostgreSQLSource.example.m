// Optional adapter, not used by the self-contained demo model.
// This existing v0.1 view has measurement grain, not first-attempt inspection grain.
// Do not substitute it into FactInspection without an explicit inspection/attempt contract.
let
    Source = PostgreSQL.Database("localhost:5432", "qualitydb", [CreateNavigationProperties=false]),
    Measurements = Source{[Schema="public",Item="vw_quality_measurements"]}[Data],
    Selected = Table.SelectColumns(Measurements,{"event_time","vehicle_id","station_code","characteristic_code","measured_value","lower_spec_limit","upper_spec_limit","is_within_spec"}),
    Typed = Table.TransformColumnTypes(Selected,{{"event_time",type datetimezone},{"measured_value",type number},{"lower_spec_limit",type number},{"upper_spec_limit",type number}})
in
    Typed
