"""
N1MOX30 Production Database Configuration.

This module provides configuration helpers without replacing
the existing application database implementation.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 1800
    echo: bool = False


def get_database_config() -> DatabaseConfig:
    url = os.getenv("DATABASE_URL", "").strip()

    if not url:
        # Preserve the existing local SQLite development default.
        url = "sqlite:///./n1mox.db"

    return DatabaseConfig(
        url=url,
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
    )
