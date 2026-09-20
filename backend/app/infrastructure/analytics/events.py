"""
N1MOX30 analytics event service.
"""

from datetime import datetime, timezone
from typing import Optional


def build_event(
    event_name: str,
    user_id: Optional[str] = None,
    source: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> dict:
    return {
        "event_name": event_name,
        "user_id": user_id,
        "source": source,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
