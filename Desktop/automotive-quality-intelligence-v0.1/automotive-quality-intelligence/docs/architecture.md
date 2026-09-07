# Architecture

```text
Synthetic / CSV / MQTT / Test Bench / Factory API
                    |
                    v
             Node-RED Gateway
         validation + transformation
               (JavaScript)
                    |
                    v
             FastAPI Ingestion
          validation + REST contract
                    |
                    v
               PostgreSQL
        raw measurements + BI views
                    |
          +---------+----------+
          |                    |
          v                    v
       Power BI            Python
     DAX + M Query      analytics / ML
```

## Why this is reusable

The central object is a generic `quality measurement event`:

- when
- what vehicle/product
- where it was measured
- what characteristic was measured
- target and specification limits
- measured value
- result derivation

That contract works beyond automotive production. It can be reused for:
- manufacturing QA
- laboratory measurements
- supplier incoming inspection
- end-of-line testing
- IoT sensor threshold monitoring
- prototype validation

## Design decisions

1. **PostgreSQL is the system of record.**
2. **Pass/fail is derived**, not trusted from the source.
3. **Specification limits travel with each measurement**, making historical analysis robust when limits change.
4. **Node-RED is an optional gateway**, not a hard dependency for batch ingestion.
5. **Power BI reads curated SQL views**, keeping dashboard logic simpler.
6. **Synthetic data simulates launch stabilization**, so the dashboard yields a visible trend rather than random noise.

## Future extensions

- MQTT input node for real sensor streams
- SPC control limits and Western Electric rules
- rework/repair event table
- supplier and component dimensions
- anomaly-detection service
- OpenTelemetry / ingestion monitoring
- authentication and role-based access
- CI tests and GitHub Actions
