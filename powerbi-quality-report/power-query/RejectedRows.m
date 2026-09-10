let
    Rejected = Table.SelectRows(ParsedInspections, each [Issue] <> null),
    Selected = Table.SelectColumns(Rejected,{"InspectionID","VehicleID","Date","Station","Result","ReworkMinutes","Issue"})
in
    Selected
