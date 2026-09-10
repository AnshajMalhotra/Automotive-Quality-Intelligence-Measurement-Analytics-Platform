let
    RawCount = Table.RowCount(RawInspections),
    RejectedCount = Table.RowCount(Table.SelectRows(ParsedInspections,each [Issue] <> null)),
    CleanCount = Table.RowCount(CleanInspections),
    Output = #table(type table [RawRows=Int64.Type,RejectedRows=Int64.Type,DuplicateRows=Int64.Type,CleanRows=Int64.Type],{{RawCount,RejectedCount,RawCount-RejectedCount-CleanCount,CleanCount}})
in
    Output
