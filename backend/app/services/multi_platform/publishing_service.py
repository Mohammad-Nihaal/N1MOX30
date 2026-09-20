from __future__ import annotations

from datetime import datetime
from typing import Any


class MultiPlatformPublishingService:
    """Provider-neutral multi-platform publishing coordinator.

    The demo adapters intentionally simulate the handoff. Real adapters can be
    enabled independently once credentials and platform APIs are configured.
    """

    SUPPORTED = ("youtube", "instagram", "tiktok", "facebook", "x")

    def preview(self, platforms: list[str], payload: dict[str, Any]) -> dict[str, Any]:
        normalized = []
        for platform in platforms:
            p = str(platform).strip().lower()
            if p in self.SUPPORTED and p not in normalized:
                normalized.append(p)
        return {
            "status": "ready",
            "platforms": normalized,
            "payload": payload,
            "adapters": {p: {"provider": "demo", "external_credentials_required": p != "youtube" or True} for p in normalized},
        }

    def publish_demo(self, platforms: list[str], payload: dict[str, Any]) -> dict[str, Any]:
        preview = self.preview(platforms, payload)
        now = datetime.utcnow().isoformat() + "Z"
        return {
            "status": "simulated",
            "published": False,
            "message": "Demo mode prepared every selected platform without making external uploads.",
            "created_at": now,
            "results": [{"platform": p, "status": "simulated", "provider": "demo"} for p in preview["platforms"]],
        }
