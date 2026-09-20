"""
N1MOX30 audit event service.
"""

from datetime import datetime, timezone
from typing import Optional


def build_audit_event(
    action: str,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> dict:
    return {
        "action": action,
        "user_id": user_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "ip_address": ip_address,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
