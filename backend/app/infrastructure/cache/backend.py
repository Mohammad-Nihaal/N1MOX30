"""
N1MOX30 cache infrastructure.

Redis is optional for local development. The application continues
to work when Redis is unavailable.
"""

import os
from typing import Optional


class CacheBackend:
    def __init__(self):
        self.url = os.getenv("REDIS_URL", "").strip()
        self.enabled = bool(self.url)

        self._redis = None

        if self.enabled:
            try:
                import redis

                self._redis = redis.Redis.from_url(
                    self.url,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
            except Exception:
                self._redis = None

    def health(self) -> dict:
        if not self.enabled:
            return {
                "enabled": False,
                "status": "disabled",
            }

        if self._redis is None:
            return {
                "enabled": True,
                "status": "unavailable",
            }

        try:
            self._redis.ping()
            return {
                "enabled": True,
                "status": "healthy",
            }
        except Exception:
            return {
                "enabled": True,
                "status": "unavailable",
            }

    def get(self, key: str) -> Optional[str]:
        if self._redis is None:
            return None

        try:
            return self._redis.get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ttl: int = 300) -> bool:
        if self._redis is None:
            return False

        try:
            return bool(self._redis.set(key, value, ex=ttl))
        except Exception:
            return False


cache = CacheBackend()
