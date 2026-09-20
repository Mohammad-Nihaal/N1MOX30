"""
N1MOX30 backup/recovery configuration.
"""

import os
from pathlib import Path


def get_backup_directory() -> Path:
    configured = os.getenv("N1MOX_BACKUP_DIR", "").strip()

    if configured:
        path = Path(configured)
    else:
        path = Path("./backups")

    path.mkdir(parents=True, exist_ok=True)
    return path


def backup_configuration() -> dict:
    return {
        "directory": str(get_backup_directory()),
        "database_url_configured": bool(
            os.getenv("DATABASE_URL", "").strip()
        ),
        "redis_configured": bool(
            os.getenv("REDIS_URL", "").strip()
        ),
    }
