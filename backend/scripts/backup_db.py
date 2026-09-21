from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from app.core.config import settings


def main() -> None:
    if not settings.database_url.startswith("sqlite:///"):
        raise SystemExit("This helper currently backs up local SQLite databases only.")
    source = Path(settings.database_url.removeprefix("sqlite:///"))
    if not source.exists():
        raise SystemExit(f"Database not found: {source}")
    target_dir = Path("backups")
    target_dir.mkdir(exist_ok=True)
    target = target_dir / f"n1mox30-{datetime.utcnow():%Y%m%d-%H%M%S}.db"
    shutil.copy2(source, target)
    print(f"Backup created: {target}")


if __name__ == "__main__":
    main()
