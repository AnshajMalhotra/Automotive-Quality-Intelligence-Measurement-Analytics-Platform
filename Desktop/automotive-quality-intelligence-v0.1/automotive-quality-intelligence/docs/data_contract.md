# Quality Measurement Event Contract

Example:

```json
{
  "event_time": "2026-09-07T08:30:00Z",
  "vehicle_id": "VH0001234",
  "model": "Compact-A",
  "station_code": "BODY",
  "characteristic_code": "DOOR_GAP_FL",
  "shift_code": "A",
  "target_value": 4.0,
  "lower_spec_limit": 3.5,
  "upper_spec_limit": 4.5,
  "measured_value": 4.23,
  "unit": "mm",
  "source": "synthetic-launch-simulator",
  "batch_id": "LAUNCH-2026-08-01"
}
```

## Rules

- `upper_spec_limit > lower_spec_limit`
- `shift_code` is A, B or C
- pass/fail is derived from the measured value and specification limits
- event identity is unique on:
  `event_time + vehicle_id + station_code + characteristic_code`
- repeated sends are therefore idempotent at the database layer
