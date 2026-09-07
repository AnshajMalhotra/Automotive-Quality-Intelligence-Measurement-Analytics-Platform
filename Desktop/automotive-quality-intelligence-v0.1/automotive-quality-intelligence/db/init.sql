CREATE TABLE IF NOT EXISTS quality_measurement (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL,
    vehicle_id VARCHAR(64) NOT NULL,
    model VARCHAR(64) NOT NULL,
    station_code VARCHAR(32) NOT NULL,
    characteristic_code VARCHAR(64) NOT NULL,
    shift_code CHAR(1) NOT NULL CHECK (shift_code IN ('A','B','C')),
    target_value DOUBLE PRECISION NOT NULL,
    lower_spec_limit DOUBLE PRECISION NOT NULL,
    upper_spec_limit DOUBLE PRECISION NOT NULL,
    measured_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(16) NOT NULL,
    source VARCHAR(64) NOT NULL DEFAULT 'synthetic',
    batch_id VARCHAR(64),
    deviation DOUBLE PRECISION GENERATED ALWAYS AS (measured_value - target_value) STORED,
    is_within_spec BOOLEAN GENERATED ALWAYS AS (
        measured_value >= lower_spec_limit AND measured_value <= upper_spec_limit
    ) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_quality_event UNIQUE (event_time, vehicle_id, station_code, characteristic_code),
    CONSTRAINT chk_spec_limits CHECK (upper_spec_limit > lower_spec_limit)
);

CREATE INDEX IF NOT EXISTS idx_qm_event_time ON quality_measurement(event_time);
CREATE INDEX IF NOT EXISTS idx_qm_vehicle ON quality_measurement(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_qm_station ON quality_measurement(station_code);
CREATE INDEX IF NOT EXISTS idx_qm_characteristic ON quality_measurement(characteristic_code);
CREATE INDEX IF NOT EXISTS idx_qm_oos ON quality_measurement(is_within_spec) WHERE NOT is_within_spec;

CREATE OR REPLACE VIEW vw_quality_measurements AS
SELECT
    id,
    event_time,
    event_time::date AS production_date,
    EXTRACT(ISOWEEK FROM event_time)::int AS iso_week,
    vehicle_id,
    model,
    station_code,
    characteristic_code,
    shift_code,
    target_value,
    lower_spec_limit,
    upper_spec_limit,
    measured_value,
    unit,
    deviation,
    ABS(deviation) AS absolute_deviation,
    is_within_spec,
    CASE WHEN is_within_spec THEN 'PASS' ELSE 'FAIL' END AS inspection_status,
    source,
    batch_id
FROM quality_measurement;

CREATE OR REPLACE VIEW vw_vehicle_quality AS
SELECT
    vehicle_id,
    MIN(event_time) AS first_inspection_time,
    MAX(event_time) AS last_inspection_time,
    MAX(model) AS model,
    COUNT(*) AS measurements,
    COUNT(*) FILTER (WHERE NOT is_within_spec) AS defect_count,
    CASE
        WHEN COUNT(*) FILTER (WHERE NOT is_within_spec) = 0 THEN TRUE
        ELSE FALSE
    END AS first_pass
FROM quality_measurement
GROUP BY vehicle_id;

CREATE OR REPLACE VIEW vw_process_capability AS
SELECT
    station_code,
    characteristic_code,
    unit,
    COUNT(*) AS sample_size,
    AVG(measured_value) AS mean_value,
    STDDEV_SAMP(measured_value) AS sigma,
    MIN(lower_spec_limit) AS lsl,
    MAX(upper_spec_limit) AS usl,
    CASE
        WHEN STDDEV_SAMP(measured_value) > 0 THEN
            (MAX(upper_spec_limit) - MIN(lower_spec_limit)) / (6.0 * STDDEV_SAMP(measured_value))
    END AS cp,
    CASE
        WHEN STDDEV_SAMP(measured_value) > 0 THEN
            LEAST(
                (MAX(upper_spec_limit) - AVG(measured_value)) / (3.0 * STDDEV_SAMP(measured_value)),
                (AVG(measured_value) - MIN(lower_spec_limit)) / (3.0 * STDDEV_SAMP(measured_value))
            )
    END AS cpk
FROM quality_measurement
GROUP BY station_code, characteristic_code, unit;

CREATE OR REPLACE VIEW vw_process_capability_weekly AS
SELECT
    DATE_TRUNC('week', event_time)::date AS production_week,
    station_code,
    characteristic_code,
    unit,
    COUNT(*) AS sample_size,
    AVG(measured_value) AS mean_value,
    STDDEV_SAMP(measured_value) AS sigma,
    MIN(lower_spec_limit) AS lsl,
    MAX(upper_spec_limit) AS usl,
    CASE
        WHEN STDDEV_SAMP(measured_value) > 0 THEN
            (MAX(upper_spec_limit) - MIN(lower_spec_limit)) / (6.0 * STDDEV_SAMP(measured_value))
    END AS cp,
    CASE
        WHEN STDDEV_SAMP(measured_value) > 0 THEN
            LEAST(
                (MAX(upper_spec_limit) - AVG(measured_value)) / (3.0 * STDDEV_SAMP(measured_value)),
                (AVG(measured_value) - MIN(lower_spec_limit)) / (3.0 * STDDEV_SAMP(measured_value))
            )
    END AS cpk
FROM quality_measurement
GROUP BY
    DATE_TRUNC('week', event_time)::date,
    station_code,
    characteristic_code,
    unit;

CREATE OR REPLACE VIEW vw_defect_pareto AS
SELECT
    station_code,
    characteristic_code,
    COUNT(*) AS defect_count,
    ROUND(
        100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS defect_share_pct
FROM quality_measurement
WHERE NOT is_within_spec
GROUP BY station_code, characteristic_code
ORDER BY defect_count DESC;

