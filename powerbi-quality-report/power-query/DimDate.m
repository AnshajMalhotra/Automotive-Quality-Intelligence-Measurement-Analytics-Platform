let
    MinDate = if Table.IsEmpty(CleanInspections) then #date(2026,1,1) else Date.StartOfYear(List.Min(CleanInspections[Date])),
    MaxDate = if Table.IsEmpty(CleanInspections) then #date(2026,12,31) else Date.EndOfYear(List.Max(CleanInspections[Date])),
    Dates = Table.FromList(List.Dates(MinDate,Duration.Days(MaxDate-MinDate)+1,#duration(1,0,0,0)),Splitter.SplitByNothing(),{"Date"}),
    Typed = Table.TransformColumnTypes(Dates, {{"Date",type date}}),
    Year = Table.AddColumn(Typed,"Year",each Date.Year([Date]),Int64.Type),
    Month = Table.AddColumn(Year,"Month",each Date.ToText([Date],"yyyy-MM","en-US"),type text),
    WeekStart = Table.AddColumn(Month,"WeekStart",each Date.StartOfWeek([Date],Day.Monday),type date)
in
    WeekStart
