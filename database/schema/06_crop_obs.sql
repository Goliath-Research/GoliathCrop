-- GoliathCrop Phase 2 — crop_obs schema (weather; sensor hypertables in Phase 3)
SET client_min_messages = warning;

CREATE SCHEMA IF NOT EXISTS crop_obs;

CREATE TABLE IF NOT EXISTS crop_obs.weather_daily (
  field_id integer NOT NULL REFERENCES crop_core.fields (id) ON DELETE CASCADE,
  obs_date date NOT NULL,
  tmin_c double precision,
  tmax_c double precision,
  precip_mm double precision,
  gdd double precision,
  et0_mm double precision,
  source text NOT NULL DEFAULT 'open-meteo',
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (field_id, obs_date)
);

CREATE INDEX IF NOT EXISTS weather_daily_field_date_idx
  ON crop_obs.weather_daily (field_id, obs_date DESC);

CREATE OR REPLACE VIEW crop_obs.v_weather_daily AS
SELECT
  w.field_id,
  w.obs_date AS date,
  w.tmin_c AS tmin,
  w.tmax_c AS tmax,
  w.precip_mm AS precip,
  w.gdd,
  w.et0_mm AS et0,
  w.source
FROM crop_obs.weather_daily w;

ALTER TABLE crop_obs.weather_daily ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS weather_daily_field_access ON crop_obs.weather_daily;
CREATE POLICY weather_daily_field_access ON crop_obs.weather_daily
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

CREATE OR REPLACE FUNCTION crop_obs.fn_field_centroid_wgs84(p_field_id integer)
RETURNS TABLE (latitude double precision, longitude double precision)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = crop_obs, crop_core, pg_temp
AS $$
  SELECT
    ST_Y(ST_Centroid(fld.geom))::double precision,
    ST_X(ST_Centroid(fld.geom))::double precision
  FROM crop_core.fields fld
  WHERE fld.id = p_field_id AND fld.geom IS NOT NULL;
$$;

CREATE OR REPLACE FUNCTION crop_obs.fn_semantic_weather_daily(
  p_user_id integer,
  p_params jsonb,
  p_limit integer
)
RETURNS TABLE (
  field_id integer,
  date date,
  tmin double precision,
  tmax double precision,
  precip double precision,
  gdd double precision,
  et0 double precision,
  source text
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = crop_obs, crop_core, portal, pg_temp
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
    v.date,
    v.tmin,
    v.tmax,
    v.precip,
    v.gdd,
    v.et0,
    v.source
  FROM crop_obs.v_weather_daily v
  WHERE v.field_id = v_field_id
    AND (v_from IS NULL OR v.date >= v_from)
    AND (v_to IS NULL OR v.date <= v_to)
  ORDER BY v.date DESC
  LIMIT v_lim;
END;
$$;

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
SET search_path = crop_obs, crop_core, pg_temp
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
END;
$$;
