-- GoliathCrop Phase 2 — additional semantic read functions and domain write procs
SET client_min_messages = warning;

CREATE OR REPLACE FUNCTION crop_core.fn_semantic_farm_list(
  p_user_id integer,
  p_params jsonb,
  p_limit integer
)
RETURNS TABLE (
  farm_id integer,
  organization_id integer,
  name text,
  location text,
  timezone text,
  units text
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = crop_core, portal, pg_temp
AS $$
DECLARE
  v_org_id integer;
  v_lim integer;
BEGIN
  IF p_user_id IS NULL THEN
    RETURN;
  END IF;
  v_org_id := NULLIF(p_params->>'organization_id', '')::integer;
  v_lim := GREATEST(0, COALESCE(p_limit, 500));
  RETURN QUERY
  SELECT
    f.id,
    f.organization_id,
    f.name,
    f.location,
    f.timezone,
    f.units
  FROM crop_core.v_farm f
  WHERE crop_core.fn_user_can_access_farm(p_user_id, f.id)
    AND (
      v_org_id IS NULL
      OR f.organization_id = v_org_id
    )
  ORDER BY f.name
  LIMIT v_lim;
END;
$$;

CREATE OR REPLACE FUNCTION crop_core.fn_semantic_season_list_by_farm(
  p_user_id integer,
  p_params jsonb,
  p_limit integer
)
RETURNS TABLE (
  season_id integer,
  farm_id integer,
  year integer,
  campaign text,
  status text
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = crop_core, portal, pg_temp
AS $$
DECLARE
  v_farm_id integer;
  v_lim integer;
BEGIN
  IF p_user_id IS NULL THEN
    RETURN;
  END IF;
  v_farm_id := (p_params->>'farm_id')::integer;
  IF v_farm_id IS NULL THEN
    PERFORM portal.fn_semantic_raise('GS501', 'farm_id is required');
  END IF;
  IF NOT crop_core.fn_user_can_access_farm(p_user_id, v_farm_id) THEN
    PERFORM portal.fn_semantic_raise('GS403', 'farm scope denied');
  END IF;
  v_lim := GREATEST(0, COALESCE(p_limit, 500));
  RETURN QUERY
  SELECT
    s.id,
    s.farm_id,
    s.year,
    s.campaign,
    s.status
  FROM crop_core.v_season s
  WHERE s.farm_id = v_farm_id
  ORDER BY s.year DESC, s.campaign NULLS LAST
  LIMIT v_lim;
END;
$$;

CREATE OR REPLACE FUNCTION crop_ops.fn_semantic_input_lot_list_by_farm(
  p_user_id integer,
  p_params jsonb,
  p_limit integer
)
RETURNS TABLE (
  input_lot_id integer,
  item_id integer,
  item_name text,
  lot text,
  on_hand double precision,
  unit text
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = crop_ops, crop_core, portal, pg_temp
AS $$
DECLARE
  v_farm_id integer;
  v_lim integer;
BEGIN
  IF p_user_id IS NULL THEN
    RETURN;
  END IF;
  v_farm_id := (p_params->>'farm_id')::integer;
  IF v_farm_id IS NULL THEN
    PERFORM portal.fn_semantic_raise('GS501', 'farm_id is required');
  END IF;
  IF NOT crop_core.fn_user_can_access_farm(p_user_id, v_farm_id) THEN
    PERFORM portal.fn_semantic_raise('GS403', 'farm scope denied');
  END IF;
  v_lim := GREATEST(0, COALESCE(p_limit, 500));
  RETURN QUERY
  SELECT
    l.id,
    l.item_id,
    l.item_name,
    l.lot,
    l.on_hand,
    l.unit
  FROM crop_ops.v_input_lot l
  INNER JOIN crop_ops.inventory_items i ON i.id = l.item_id
  WHERE i.farm_id = v_farm_id
  ORDER BY l.item_name, l.lot
  LIMIT v_lim;
END;
$$;

CREATE OR REPLACE FUNCTION crop_trial.fn_semantic_trial_list_by_season(
  p_user_id integer,
  p_params jsonb,
  p_limit integer
)
RETURNS TABLE (
  trial_id integer,
  season_id integer,
  name text,
  design text,
  treatment_count integer,
  replicate_count integer
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = crop_trial, crop_core, portal, pg_temp
AS $$
DECLARE
  v_season_id integer;
  v_farm_id integer;
  v_lim integer;
BEGIN
  IF p_user_id IS NULL THEN
    RETURN;
  END IF;
  v_season_id := (p_params->>'season_id')::integer;
  IF v_season_id IS NULL THEN
    PERFORM portal.fn_semantic_raise('GS501', 'season_id is required');
  END IF;
  SELECT s.farm_id INTO v_farm_id FROM crop_core.seasons s WHERE s.id = v_season_id;
  IF v_farm_id IS NULL OR NOT crop_core.fn_user_can_access_farm(p_user_id, v_farm_id) THEN
    PERFORM portal.fn_semantic_raise('GS403', 'season scope denied');
  END IF;
  v_lim := GREATEST(0, COALESCE(p_limit, 500));
  RETURN QUERY
  SELECT
    t.id,
    t.season_id,
    t.name,
    t.design,
    t.treatment_count,
    t.replicate_count
  FROM crop_trial.v_trial t
  WHERE t.season_id = v_season_id
  ORDER BY t.name
  LIMIT v_lim;
END;
$$;

CREATE OR REPLACE FUNCTION crop_ops.sp_record_operation(
  p_user_id integer,
  p_planting_id integer,
  p_kind text,
  p_performed_on timestamptz,
  p_rate double precision DEFAULT NULL,
  p_rate_unit text DEFAULT NULL,
  p_equipment text DEFAULT NULL,
  p_operator text DEFAULT NULL,
  p_notes text DEFAULT NULL
)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = crop_ops, crop_core, portal, pg_temp
AS $$
DECLARE
  v_farm_id integer;
  v_operation_id integer;
BEGIN
  IF p_user_id IS NULL THEN
    PERFORM portal.fn_semantic_raise('GS401', 'user required');
  END IF;
  SELECT fld.farm_id INTO v_farm_id
  FROM crop_core.plantings pl
  INNER JOIN crop_core.fields fld ON fld.id = pl.field_id
  WHERE pl.id = p_planting_id;
  IF v_farm_id IS NULL OR NOT crop_core.fn_user_can_access_farm(p_user_id, v_farm_id) THEN
    PERFORM portal.fn_semantic_raise('GS403', 'planting scope denied');
  END IF;
  PERFORM set_config('goliath.crop.user_id', p_user_id::text, true);
  INSERT INTO crop_ops.operations (
    planting_id,
    kind,
    performed_on,
    rate,
    rate_unit,
    equipment,
    operator,
    notes
  )
  VALUES (
    p_planting_id,
    p_kind,
    p_performed_on,
    p_rate,
    p_rate_unit,
    p_equipment,
    p_operator,
    p_notes
  )
  RETURNING id INTO v_operation_id;
  RETURN v_operation_id;
END;
$$;

CREATE OR REPLACE FUNCTION crop_trial.sp_record_plot_observation(
  p_user_id integer,
  p_plot_id integer,
  p_metric text,
  p_value double precision,
  p_measured_on date DEFAULT CURRENT_DATE
)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = crop_trial, crop_core, portal, pg_temp
AS $$
DECLARE
  v_farm_id integer;
  v_measurement_id integer;
BEGIN
  IF p_user_id IS NULL THEN
    PERFORM portal.fn_semantic_raise('GS401', 'user required');
  END IF;
  SELECT fld.farm_id INTO v_farm_id
  FROM crop_core.plots p
  INNER JOIN crop_core.fields fld ON fld.id = p.field_id
  WHERE p.id = p_plot_id;
  IF v_farm_id IS NULL OR NOT crop_core.fn_user_can_access_farm(p_user_id, v_farm_id) THEN
    PERFORM portal.fn_semantic_raise('GS403', 'plot scope denied');
  END IF;
  PERFORM set_config('goliath.crop.user_id', p_user_id::text, true);
  INSERT INTO crop_trial.plot_measurements (plot_id, metric, value, measured_on)
  VALUES (p_plot_id, p_metric, p_value, COALESCE(p_measured_on, CURRENT_DATE))
  RETURNING id INTO v_measurement_id;
  RETURN v_measurement_id;
END;
$$;
