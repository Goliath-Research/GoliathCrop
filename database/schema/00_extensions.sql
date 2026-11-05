-- GoliathCrop Phase 1 — required extensions
SET client_min_messages = warning;

CREATE EXTENSION IF NOT EXISTS postgis;

-- TimescaleDB (Apache-2 on Neon: hypertables, time_bucket, drop_chunks only).
-- If unavailable, sensor_readings stays a plain Postgres table; see 09_crop_obs_sensors.sql.
DO $$
BEGIN
  CREATE EXTENSION IF NOT EXISTS timescaledb;
EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'timescaledb extension not available: %', SQLERRM;
END $$;
