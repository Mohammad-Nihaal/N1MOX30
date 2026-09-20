"""
N1MOX30 infrastructure health aggregation.
"""

from .database_config import get_database_config
from .cache.backend import cache
from .backup.service import backup_configuration


def infrastructure_health() -> dict:
    db = get_database_config()

    return {
        "database": {
            "configured": bool(db.url),
            "url_scheme": db.url.split(":", 1)[0] if ":" in db.url else "unknown",
        },
        "cache": cache.health(),
        "backup": backup_configuration(),
    }
