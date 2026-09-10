let
    Grouped = Table.Group(CleanInspections, {"VehicleID"}, {
        {"Date", each List.Min([Date]), type date},
        {"Model", each List.Min([Model]), type text},
        {"Shift", each List.Min([Shift]), type text},
        {"InspectionCount", each Table.RowCount(_), Int64.Type},
        {"FailCount", each List.Count(List.Select([Result], (r) => r = "FAIL")), Int64.Type},
        {"Complete", each Table.RowCount(_) = 3 and List.Count(List.Distinct([Station])) = 3 and List.Count(List.Distinct([Date])) = 1 and List.Count(List.Distinct([Model])) = 1 and List.Count(List.Distinct([Shift])) = 1, type logical}}),
    FirstPass = Table.AddColumn(Grouped, "FirstPass", each [Complete] and [FailCount] = 0, type logical)
in
    FirstPass
