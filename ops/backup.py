"""PostgreSQL custom zaxirasi: vaqtinchalik fayl, tekshiruv va SHA-256 dalili.

DB_* yoki libpq PG* muhit sozlamalarini ishlatadi; maxfiy qiymatlarni yozmaydi.
Retention kelishilmaguncha birorta eski zaxirani avtomatik o'chirmaydi.
"""

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path


def connection_env():
    """Django DB_* parametrlarini libpq muhitiga maxfiy tarzda ko'chiradi."""
    env = os.environ.copy()
    for suffix in ("HOST", "PORT", "USER", "PASSWORD"):
        if value := env.get(f"DB_{suffix}"):
            env.setdefault(f"PG{suffix}", value)
    if value := env.get("DB_NAME"):
        env.setdefault("PGDATABASE", value)
    if not env.get("PGDATABASE"):
        raise ValueError("PGDATABASE yoki DB_NAME belgilang.")
    return env


def backup(directory: Path):
    """Faqat to'liq va pg_restore tanigan arxivni yakuniy nom bilan e'lon qiladi."""
    env = connection_env()
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    target = directory / f"profur-{stamp}.dump"
    fd, temporary = tempfile.mkstemp(prefix=".backup-", dir=directory)
    os.close(fd)
    try:
        subprocess.run(
            [
                "pg_dump",
                "--format=custom",
                "--no-owner",
                "--no-acl",
                "--file",
                temporary,
            ],
            env=env,
            check=True,
        )
        subprocess.run(
            ["pg_restore", "--list", temporary],
            env=env,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        with open(temporary, "rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        os.replace(temporary, target)
        manifest = target.with_suffix(".json")
        with manifest.open("x") as stream:
            os.chmod(manifest, 0o600)
            json.dump(
                {
                    "created_at": stamp,
                    "archive": target.name,
                    "bytes": target.stat().st_size,
                    "sha256": digest,
                },
                stream,
                indent=2,
            )
        print(json.dumps({"archive": str(target), "sha256": digest}))
    finally:
        Path(temporary).unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    backup(parser.parse_args().directory)
