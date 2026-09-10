let
    Source = Csv.Document(File.Contents(DataFolder & "/inspections_raw.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Required = Table.SelectColumns(Headers, {"InspectionID","VehicleID","Date","Model","Shift","Station","Result","Defect","ReworkMinutes","UpdatedAt"}),
    Indexed = Table.AddIndexColumn(Required, "_Row", 0, 1, Int64.Type)
in
    Indexed
