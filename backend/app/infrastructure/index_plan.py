"""
Recommended production database indexes for N1MOX30.

The existing database models remain the source of truth.
This file documents the indexes that should exist in the
production migration layer.
"""

RECOMMENDED_INDEXES = {
    "users": [
        ("email", "unique"),
    ],
    "workflows": [
        ("user_id", "normal"),
        ("status", "normal"),
        ("created_at", "normal"),
        ("user_id", "status"),
    ],
    "workflow_steps": [
        ("workflow_id", "normal"),
        ("workflow_id", "step_order"),
        ("status", "normal"),
    ],
    "connected_accounts": [
        ("user_id", "normal"),
        ("platform", "normal"),
        ("user_id", "platform"),
    ],
    "subscriptions": [
        ("user_id", "normal"),
        ("status", "normal"),
        ("provider_subscription_id", "normal"),
    ],
    "transactions": [
        ("user_id", "normal"),
        ("status", "normal"),
        ("created_at", "normal"),
    ],
    "analytics_events": [
        ("user_id", "normal"),
        ("event_name", "normal"),
        ("created_at", "normal"),
    ],
    "audit_logs": [
        ("user_id", "normal"),
        ("action", "normal"),
        ("created_at", "normal"),
    ],
}
