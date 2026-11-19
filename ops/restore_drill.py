"""Zaxirani yangi alohida bazaga tiklaydi va qoldiq invariantini tekshiradi.

Asl bazaga yozmaydi. Faqat o'zi yaratgan profur_drill_* vaqtinchalik bazani tozalaydi.
"""

import argparse
import hashlib
import json
import subprocess
import time
import uuid
from pathlib import Path

from backup import connection_env, pg_tool


def drill(archive: Path):
    env = connection_env()
    manifest = json.loads(archive.with_suffix(".json").read_text())
    with archive.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != manifest["sha256"]:
            raise ValueError("Zaxira nazorat summasi mos emas.")
    target = "profur_drill_" + uuid.uuid4().hex
    started = time.monotonic()
    created = False
    try:
        subprocess.run(
            [pg_tool("createdb"), "--maintenance-db", env["PGDATABASE"], target],
            env=env,
            check=True,
        )
        created = True
        subprocess.run(
            [
                pg_tool("pg_restore"),
                "--exit-on-error",
                "--no-owner",
                "--no-acl",
                "--dbname",
                target,
                str(archive),
            ],
            env=env,
            check=True,
        )
        sql = """
        SELECT count(*) FROM catalog_material material
        LEFT JOIN inventory_stockbalance s ON s.material_id=material.id
        WHERE COALESCE(s.quantity_on_hand,0) < 0
           OR COALESCE(s.quantity_on_hand,0) <> COALESCE((SELECT sum(b.quantity_remaining) FROM inventory_batch b WHERE b.material_id=material.id),0)
           OR COALESCE(s.quantity_on_hand,0) <> COALESCE((SELECT sum(m.quantity) FROM inventory_stockmovement m WHERE m.material_id=material.id),0);
        """
        check = subprocess.run(
            [
                pg_tool("psql"),
                "--no-psqlrc",
                "--set",
                "ON_ERROR_STOP=1",
                "--dbname",
                target,
                "--tuples-only",
                "--no-align",
                "--command",
                sql,
            ],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        if check.stdout.strip() != "0":
            raise ValueError("Tiklangan qoldiq, partiya va tarix summalari mos emas.")
        counts = subprocess.run(
            [
                pg_tool("psql"),
                "--no-psqlrc",
                "--set",
                "ON_ERROR_STOP=1",
                "--dbname",
                target,
                "--tuples-only",
                "--no-align",
                "--command",
                "SELECT json_build_object('materials',(SELECT count(*) FROM catalog_material),'batches',(SELECT count(*) FROM inventory_batch),'movements',(SELECT count(*) FROM inventory_stockmovement),'expenses',(SELECT count(*) FROM expenses_expense));",
            ],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        print(
            json.dumps(
                {
                    "verified": True,
                    "elapsed_seconds": round(time.monotonic() - started, 2),
                    "rows": json.loads(counts.stdout),
                }
            )
        )
    finally:
        if created:
            subprocess.run(
                [pg_tool("dropdb"), "--maintenance-db", env["PGDATABASE"], target],
                env=env,
                check=True,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    drill(parser.parse_args().archive)
