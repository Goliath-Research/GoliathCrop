-- GoliathCrop NavTree nodes (idempotent; does not mutate foundation menus)

CREATE OR REPLACE FUNCTION crop_core.sp_register_crop_nav_child(
  p_parent_id integer,
  p_caption text,
  p_seq smallint,
  p_info_name text,
  p_frame_key text
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  v_info integer;
  v_exists integer;
BEGIN
  SELECT ni."Id" INTO v_info FROM portal."NodeInfos" ni WHERE ni."Name" = p_info_name;
  IF v_info IS NULL THEN
    INSERT INTO portal."NodeInfos" ("Name", "Singleton", "TypeId", "FrameKey")
    VALUES (p_info_name, true, 1, p_frame_key)
    RETURNING "Id" INTO v_info;
  ELSE
    UPDATE portal."NodeInfos"
    SET "FrameKey" = p_frame_key
    WHERE "Id" = v_info AND "FrameKey" IS DISTINCT FROM p_frame_key;
  END IF;

  SELECT n."ID" INTO v_exists
  FROM portal."NavTree" n
  WHERE n."ParentID" = p_parent_id AND n."Caption" = p_caption;

  IF v_exists IS NULL THEN
    PERFORM portal.sp_nav_register_node(p_parent_id, p_caption, p_seq, v_info);
  END IF;
END;
$$;

CREATE OR REPLACE FUNCTION crop_core.sp_register_crop_nav()
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  v_root_info integer;
  v_root_id integer;
  v_info integer;
  v_node integer;
BEGIN
  SELECT ni."Id" INTO v_root_info FROM portal."NodeInfos" ni WHERE ni."Name" = 'crop_root';
  IF v_root_info IS NULL THEN
    INSERT INTO portal."NodeInfos" ("Name", "Singleton", "TypeId", "FrameKey")
    VALUES ('crop_root', true, 1, 'crop')
    RETURNING "Id" INTO v_root_info;
  END IF;

  SELECT n."ID" INTO v_root_id
  FROM portal."NavTree" n
  WHERE n."Caption" = 'Crop' AND n."ParentID" IS NULL;

  IF v_root_id IS NULL THEN
    SELECT node_id INTO v_root_id
    FROM portal.sp_nav_register_node(NULL, 'Crop', 20::smallint, v_root_info);
  END IF;

  PERFORM crop_core.sp_register_crop_nav_child(
    v_root_id, 'Farms & fields', 10, 'crop_farms_fields', 'crop.field.list_by_farm'
  );
  PERFORM crop_core.sp_register_crop_nav_child(
    v_root_id, 'Seasons & plantings', 20, 'crop_seasons', 'crop.planting.list_by_season'
  );
  PERFORM crop_core.sp_register_crop_nav_child(
    v_root_id, 'Operations', 30, 'crop_operations', 'crop.operation.list'
  );
  PERFORM crop_core.sp_register_crop_nav_child(
    v_root_id, 'Inventory', 35, 'crop_inventory', 'crop.input_lot.list_by_farm'
  );
  PERFORM crop_core.sp_register_crop_nav_child(
    v_root_id, 'Sensors & weather', 38, 'crop_sensors_weather', 'crop.reading.window'
  );
  PERFORM crop_core.sp_register_crop_nav_child(
    v_root_id, 'Imagery', 39, 'crop_imagery', 'crop.scene.list_by_field'
  );
  PERFORM crop_core.sp_register_crop_nav_child(
    v_root_id, 'Irrigation planner', 41, 'crop_irrigation', 'crop.irrigation.schedule_by_field'
  );
  PERFORM crop_core.sp_register_crop_nav_child(
    v_root_id, 'Scouting', 42, 'crop_scouting', 'crop.scouting.list_by_field'
  );
  PERFORM crop_core.sp_register_crop_nav_child(
    v_root_id, 'Field entry', 45, 'crop_field_entry', 'crop.field.entry'
  );
  PERFORM crop_core.sp_register_crop_nav_child(
    v_root_id, 'Trials', 40, 'crop_trials', 'crop.trial.list_by_season'
  );
END;
$$;

SELECT crop_core.sp_register_crop_nav();
