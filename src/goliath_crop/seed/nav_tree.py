"""Idempotent Crop NavTree registration via portal.sp_nav_register_node."""

from __future__ import annotations

import os
import sys


def _connect():
    import psycopg

    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ.get("PGPASSWORD"),
    )


NAV_SPEC = (
    ("Crop", None, 20, "crop_root", "crop"),
    ("Farms & fields", "Crop", 10, "crop_farms_fields", "crop.field.list_by_farm"),
    ("Seasons & plantings", "Crop", 20, "crop_seasons", "crop.planting.list_by_season"),
    ("Operations", "Crop", 30, "crop_operations", "crop.operation.list"),
    ("Inventory", "Crop", 35, "crop_inventory", "crop.input_lot.list_by_farm"),
    ("Sensors & weather", "Crop", 38, "crop_sensors_weather", "crop.reading.window"),
    ("Imagery", "Crop", 39, "crop_imagery", "crop.scene.list_by_field"),
    ("Trials", "Crop", 40, "crop_trials", "crop.trial.list_by_season"),
)


def _ensure_node_info(cur, name: str, frame_key: str) -> int:
    cur.execute(
        """
        SELECT "Id" FROM portal."NodeInfos" WHERE "Name" = %s
        """,
        (name,),
    )
    row = cur.fetchone()
    if row:
        info_id = int(row[0])
        cur.execute(
            """
            UPDATE portal."NodeInfos"
            SET "FrameKey" = %s
            WHERE "Id" = %s AND "FrameKey" IS DISTINCT FROM %s
            """,
            (frame_key, info_id, frame_key),
        )
        return info_id
    cur.execute(
        """
        INSERT INTO portal."NodeInfos" ("Name", "Singleton", "TypeId", "FrameKey")
        VALUES (%s, true, 1, %s)
        RETURNING "Id"
        """,
        (name, frame_key),
    )
    return int(cur.fetchone()[0])


def _find_node(cur, caption: str, parent_id: int | None) -> int | None:
    if parent_id is None:
        cur.execute(
            """
            SELECT "ID" FROM portal."NavTree"
            WHERE "Caption" = %s AND "ParentID" IS NULL
            """,
            (caption,),
        )
    else:
        cur.execute(
            """
            SELECT "ID" FROM portal."NavTree"
            WHERE "Caption" = %s AND "ParentID" = %s
            """,
            (caption, parent_id),
        )
    row = cur.fetchone()
    return int(row[0]) if row else None


def seed(conn) -> int:
    created = 0
    node_ids: dict[str, int] = {}
    with conn.cursor() as cur:
        for caption, parent_caption, seq, info_name, frame_key in NAV_SPEC:
            parent_id = node_ids.get(parent_caption) if parent_caption else None
            info_id = _ensure_node_info(cur, info_name, frame_key or info_name)
            existing = _find_node(cur, caption, parent_id)
            if existing is not None:
                node_ids[caption] = existing
                continue
            cur.execute(
                """
                SELECT node_id FROM portal.sp_nav_register_node(%s, %s, %s::smallint, %s)
                """,
                (parent_id, caption, seq, info_id),
            )
            node_ids[caption] = int(cur.fetchone()[0])
            created += 1
    conn.commit()
    return created


def main() -> int:
    if not os.environ.get("PGHOST"):
        print("Set PGHOST/PGDATABASE/PGUSER for goliath-crop-seed-nav", file=sys.stderr)
        return 2
    with _connect() as conn:
        n = seed(conn)
    print(f"Registered {n} new Crop NavTree nodes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
