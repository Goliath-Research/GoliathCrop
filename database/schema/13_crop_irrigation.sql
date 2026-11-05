-- GoliathCrop Phase 4 — FAO-56 irrigation scheduling + wakes on ET0 / soil moisture
SET client_min_messages = warning;

CREATE SCHEMA IF NOT EXISTS crop_irr;

CREATE TABLE IF NOT EXISTS crop_irr.field_balance (
  field_id integer NOT NULL REFERENCES crop_core.fields (id) ON DELETE CASCADE,
  balance_date date NOT NULL,
  depletion_mm double precision NOT NULL,
  etc_mm double precision NOT NULL,
  precip_mm double precision,
  irrigation_mm double precision NOT NULL DEFAULT 0,
  soil_moisture_pct double precision,
  recommended_irrigation_mm double precision NOT NULL DEFAULT 0,
  taw_mm double precision NOT NULL DEFAULT 150,
  kc double precision NOT NULL DEFAULT 1.0,
  computed_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (field_id, balance_date)
);

CREATE INDEX IF NOT EXISTS field_balance_field_date_idx
  ON crop_irr.field_balance (field_id, balance_date DESC);

CREATE OR REPLACE VIEW crop_irr.v_schedule AS
SELECT
  b.field_id,
  b.balance_date AS schedule_date,
  b.depletion_mm,
  b.soil_moisture_pct,
  b.recommended_irrigation_mm,
  b.etc_mm,
  b.precip_mm,
  b.irrigation_mm AS applied_irrigation_mm,
  b.computed_at
FROM crop_irr.field_balance b;

ALTER TABLE crop_irr.field_balance ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS field_balance_field_access ON crop_irr.field_balance;
CREATE POLICY field_balance_field_access ON crop_irr.field_balance
  FOR ALL
  USING (
    EXISTS (
      SELECT 1
      FROM crop_core.fields fld
      WHERE fld.id = field_id
        AND crop_core.fn_user_can_access_farm(
          NULLIF(current_setting('goliath.crop.user_id', true), '')::integer,
          fld.farm_id
        )
    )
  );

CREATE OR REPLACE FUNCTION crop_irr.fn_semantic_schedule_by_field(
  p_user_id integer,
  p_params jsonb,
  p_limit integer
)
RETURNS TABLE (
  field_id integer,
  schedule_date date,
  depletion_mm double precision,
  soil_moisture_pct double precision,
  recommended_irrigation_mm double precision,
  etc_mm double precision,
  precip_mm double precision,
  applied_irrigation_mm double precision,
  computed_at timestamptz
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = crop_irr, crop_core, portal, pg_temp
AS $$
DECLARE
  v_field_id integer;
  v_from date;
  v_to date;
  v_lim integer;
BEGIN
  IF p_user_id IS NULL THEN
    RETURN;
  END IF;
  v_field_id := (p_params->>'field_id')::integer;
  IF v_field_id IS NULL THEN
    PERFORM portal.fn_semantic_raise('GS501', 'field_id is required');
  END IF;
  IF NOT EXISTS (
    SELECT 1
    FROM crop_core.fields fld
    WHERE fld.id = v_field_id
      AND crop_core.fn_user_can_access_farm(p_user_id, fld.farm_id)
  ) THEN
    PERFORM portal.fn_semantic_raise('GS403', 'field scope denied');
  END IF;
  v_from := NULLIF(p_params->>'from', '')::date;
  v_to := NULLIF(p_params->>'to', '')::date;
  v_lim := GREATEST(0, COALESCE(p_limit, 500));
  RETURN QUERY
  SELECT
    v.field_id,
    v.schedule_date,
    v.depletion_mm,
    v.soil_moisture_pct,
    v.recommended_irrigation_mm,
    v.etc_mm,
    v.precip_mm,
    v.applied_irrigation_mm,
    v.computed_at
  FROM crop_irr.v_schedule v
  WHERE v.field_id = v_field_id
    AND (v_from IS NULL OR v.schedule_date >= v_from)
    AND (v_to IS NULL OR v.schedule_date <= v_to)
  ORDER BY v.schedule_date DESC
  LIMIT v_lim;
END;
$$;

CREATE OR REPLACE FUNCTION crop_irr.sp_store_balance(
  p_field_id integer,
  p_balance_date date,
  p_depletion_mm double precision,
  p_etc_mm double precision,
  p_precip_mm double precision,
  p_irrigation_mm double precision,
  p_soil_moisture_pct double precision,
  p_recommended_irrigation_mm double precision,
  p_taw_mm double precision DEFAULT 150,
  p_kc double precision DEFAULT 1.0
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = crop_irr, crop_core, pg_temp
AS $$
BEGIN
  INSERT INTO crop_irr.field_balance (
    field_id,
    balance_date,
    depletion_mm,
    etc_mm,
    precip_mm,
    irrigation_mm,
    soil_moisture_pct,
    recommended_irrigation_mm,
    taw_mm,
    kc,
    computed_at
  )
  VALUES (
    p_field_id,
    p_balance_date,
    p_depletion_mm,
    p_etc_mm,
    p_precip_mm,
    COALESCE(p_irrigation_mm, 0),
    p_soil_moisture_pct,
    COALESCE(p_recommended_irrigation_mm, 0),
    COALESCE(p_taw_mm, 150),
    COALESCE(p_kc, 1.0),
    now()
  )
  ON CONFLICT (field_id, balance_date) DO UPDATE SET
    depletion_mm = EXCLUDED.depletion_mm,
    etc_mm = EXCLUDED.etc_mm,
    precip_mm = EXCLUDED.precip_mm,
    irrigation_mm = EXCLUDED.irrigation_mm,
    soil_moisture_pct = EXCLUDED.soil_moisture_pct,
    recommended_irrigation_mm = EXCLUDED.recommended_irrigation_mm,
    taw_mm = EXCLUDED.taw_mm,
    kc = EXCLUDED.kc,
    computed_at = now();
END;
$$;

CREATE OR REPLACE FUNCTION crop_irr.sp_wake_schedule_for_field(
  p_field_id integer,
  p_balance_date date DEFAULT NULL,
  p_reason text DEFAULT 'irrigation_data_updated'
)
RETURNS bigint
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = crop_irr, crop_wf, pg_temp
AS $$
DECLARE
  v_date date;
BEGIN
  IF p_field_id IS NULL THEN
    RETURN NULL;
  END IF;
  v_date := COALESCE(p_balance_date, CURRENT_DATE);
  RETURN crop_wf.sp_enqueue_processing_task(
    'crop.irrigation.schedule',
    jsonb_build_object('field_id', p_field_id, 'balance_date', v_date),
    'crop.irrigation',
    COALESCE(p_reason, 'irrigation_data_updated'),
    'irr:field:' || p_field_id::text || ':' || v_date::text || ':' || gen_random_uuid()::text
  );
END;
$$;

CREATE OR REPLACE FUNCTION crop_irr.sp_enqueue_daily_backlog()
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = crop_irr, crop_core, crop_wf, pg_temp
AS $$
DECLARE
  v_field record;
  v_count integer := 0;
BEGIN
  FOR v_field IN
    SELECT f.id AS field_id
    FROM crop_core.fields f
    WHERE f.geom IS NOT NULL
    ORDER BY f.id
    LIMIT 500
  LOOP
    PERFORM crop_irr.sp_wake_schedule_for_field(v_field.field_id, CURRENT_DATE, 'daily_backlog');
    v_count := v_count + 1;
  END LOOP;
  RETURN v_count;
END;
$$;

-- Wake irrigation scheduling when daily ET0 / weather is upserted.
CREATE OR REPLACE FUNCTION crop_obs.sp_upsert_weather_daily(
  p_field_id integer,
  p_obs_date date,
  p_tmin_c double precision,
  p_tmax_c double precision,
  p_precip_mm double precision,
  p_gdd double precision,
  p_et0_mm double precision,
  p_source text DEFAULT 'open-meteo'
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = crop_obs, crop_irr, crop_core, pg_temp
AS $$
BEGIN
  INSERT INTO crop_obs.weather_daily (
    field_id,
    obs_date,
    tmin_c,
    tmax_c,
    precip_mm,
    gdd,
    et0_mm,
    source,
    updated_at
  )
  VALUES (
    p_field_id,
    p_obs_date,
    p_tmin_c,
    p_tmax_c,
    p_precip_mm,
    p_gdd,
    p_et0_mm,
    COALESCE(p_source, 'open-meteo'),
    now()
  )
  ON CONFLICT (field_id, obs_date) DO UPDATE SET
    tmin_c = EXCLUDED.tmin_c,
    tmax_c = EXCLUDED.tmax_c,
    precip_mm = EXCLUDED.precip_mm,
    gdd = EXCLUDED.gdd,
    et0_mm = EXCLUDED.et0_mm,
    source = EXCLUDED.source,
    updated_at = now();

  IF p_et0_mm IS NOT NULL THEN
    PERFORM crop_irr.sp_wake_schedule_for_field(p_field_id, p_obs_date, 'weather_et0_updated');
  END IF;
END;
$$;

-- Also wake irrigation when soil moisture readings arrive.
CREATE OR REPLACE FUNCTION crop_obs.sp_ingest_sensor_batch(
  p_device_id integer,
  p_readings jsonb
)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = crop_obs, crop_irr, crop_wf, pg_temp
AS $$
DECLARE
  v_row jsonb;
  v_inserted integer := 0;
  v_last timestamptz;
  v_field_id integer;
  v_has_moisture boolean := false;
BEGIN
  IF p_device_id IS NULL THEN
    RAISE EXCEPTION 'device_id is required';
  END IF;
  IF p_readings IS NULL OR jsonb_typeof(p_readings) <> 'array' THEN
    RAISE EXCEPTION 'readings must be a JSON array';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM crop_obs.devices d WHERE d.id = p_device_id) THEN
    RAISE EXCEPTION 'unknown device_id %', p_device_id;
  END IF;

  SELECT d.field_id INTO v_field_id FROM crop_obs.devices d WHERE d.id = p_device_id;

  FOR v_row IN SELECT value FROM jsonb_array_elements(p_readings)
  LOOP
    IF (v_row->>'metric') IN ('soil_moisture', 'soil_moisture_pct', 'vwc') THEN
      v_has_moisture := true;
    END IF;
    INSERT INTO crop_obs.sensor_readings (ts, device_id, metric, value, quality)
    VALUES (
      (v_row->>'ts')::timestamptz,
      p_device_id,
      v_row->>'metric',
      (v_row->>'value')::double precision,
      v_row->>'quality'
    )
    ON CONFLICT (device_id, ts, metric) DO UPDATE SET
      value = EXCLUDED.value,
      quality = EXCLUDED.quality;
    v_inserted := v_inserted + 1;
    IF v_last IS NULL OR (v_row->>'ts')::timestamptz > v_last THEN
      v_last := (v_row->>'ts')::timestamptz;
    END IF;
  END LOOP;

  IF v_last IS NOT NULL THEN
    UPDATE crop_obs.devices
    SET last_reading_at = GREATEST(COALESCE(last_reading_at, v_last), v_last)
    WHERE id = p_device_id;
  END IF;

  PERFORM crop_wf.sp_enqueue_processing_task(
    'crop.sensor.qc',
    jsonb_build_object('device_id', p_device_id, 'reading_count', v_inserted),
    'crop.ingest',
    'sensor_batch_ingested',
    'sensor:' || p_device_id::text || ':' || gen_random_uuid()::text
  );

  IF v_has_moisture AND v_field_id IS NOT NULL THEN
    PERFORM crop_irr.sp_wake_schedule_for_field(
      v_field_id,
      (
        v_last AT TIME ZONE COALESCE(
          (
            SELECT fm.timezone
            FROM crop_core.fields fld
            INNER JOIN crop_core.farms fm ON fm.id = fld.farm_id
            WHERE fld.id = v_field_id
          ),
          'UTC'
        )
      )::date,
      'soil_moisture_updated'
    );
  END IF;

  RETURN v_inserted;
END;
$$;
