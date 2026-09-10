let
    Trimmed = Table.TransformColumns(RawInspections, List.Transform({"InspectionID","VehicleID","Date","Model","Shift","Station","Result","Defect","ReworkMinutes","UpdatedAt"}, (c) => {c, each if _ = null then "" else Text.Trim(Text.From(_)), type text})),
    Normalized = Table.TransformColumns(Trimmed, {{"Station",Text.Proper,type text},{"Result",Text.Upper,type text},{"Shift",Text.Upper,type text}}),
    DateParsed = Table.AddColumn(Normalized, "ParsedDate", each try Date.FromText([Date], [Format="yyyy-MM-dd", Culture="en-US"]) otherwise null, type nullable date),
    MinutesParsed = Table.AddColumn(DateParsed, "ParsedMinutes", each try Number.FromText([ReworkMinutes], "en-US") otherwise null, type nullable number),
    UpdatedParsed = Table.AddColumn(MinutesParsed, "ParsedUpdated", each try DateTime.FromText([UpdatedAt], [Format="yyyy-MM-dd'T'HH:mm:ss", Culture="en-US"]) otherwise null, type nullable datetime),
    Validation = Table.AddColumn(UpdatedParsed, "Issue", each
        if [InspectionID] = "" or [VehicleID] = "" then "Missing ID"
        else if [ParsedDate] = null or [ParsedUpdated] = null then "Invalid date"
        else if not List.Contains({"Body","Paint","Final"}, [Station]) then "Unknown station"
        else if not List.Contains({"Compact A","Compact B"}, [Model]) then "Unknown model"
        else if not List.Contains({"A","B","C"}, [Shift]) then "Unknown shift"
        else if not List.Contains({"PASS","FAIL"}, [Result]) then "Unknown result"
        else if [ParsedMinutes] = null or [ParsedMinutes] < 0 then "Invalid rework minutes"
        else if [Result] = "PASS" and ([Defect] <> "None" or [ParsedMinutes] <> 0) then "Inconsistent pass row"
        else if [Result] = "FAIL" and not List.Contains({"Panel gap","Weld appearance","Surface inclusion","Paint finish","Fit and finish","Function check"},[Defect]) then "Invalid failure category"
        else null, type nullable text)
in
    Validation
