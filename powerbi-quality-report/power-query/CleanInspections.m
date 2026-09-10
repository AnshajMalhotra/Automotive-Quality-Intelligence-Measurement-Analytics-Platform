let
    Valid = Table.SelectRows(ParsedInspections, each [Issue] = null),
    // Buffer after sorting: keep the latest update, then the last input row for timestamp ties.
    Sorted = Table.Buffer(Table.Sort(Valid, {{"ParsedUpdated",Order.Descending},{"_Row",Order.Descending}})),
    Latest = Table.Distinct(Sorted, {"InspectionID"}),
    Selected = Table.SelectColumns(Latest, {"InspectionID","VehicleID","ParsedDate","Model","Shift","Station","Result","Defect","ParsedMinutes"}),
    Renamed = Table.RenameColumns(Selected, {{"ParsedDate","Date"},{"ParsedMinutes","ReworkMinutes"}}),
    Typed = Table.TransformColumnTypes(Renamed, {{"InspectionID",type text},{"VehicleID",type text},{"Date",type date},{"Model",type text},{"Shift",type text},{"Station",type text},{"Result",type text},{"Defect",type text},{"ReworkMinutes",type number}}, "en-US")
in
    Typed
