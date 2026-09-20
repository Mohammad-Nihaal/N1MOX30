"""
N1MOX30 production persistence contracts.

These are intentionally independent contracts so the existing
SQLAlchemy models can remain unchanged while production storage
is migrated safely.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreatorRecord:
    creator_id: str
    user_id: str
    display_name: Optional[str] = None
    workspace_id: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class WorkspaceRecord:
    workspace_id: str
    owner_user_id: str
    name: str
    created_at: Optional[datetime] = None


@dataclass
class SubscriptionRecord:
    subscription_id: str
    user_id: str
    plan: str
    status: str
    provider: Optional[str] = None
    provider_subscription_id: Optional[str] = None
    current_period_end: Optional[datetime] = None


@dataclass
class TransactionRecord:
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    status: str
    provider: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class AutomationRecord:
    automation_id: str
    user_id: str
    workflow_id: str
    status: str
    current_stage: Optional[str] = None
    progress: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AnalyticsEventRecord:
    event_id: str
    user_id: Optional[str]
    event_name: str
    source: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None


@dataclass
class AuditLogRecord:
    audit_id: str
    user_id: Optional[str]
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None
