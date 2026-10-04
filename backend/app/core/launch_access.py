from __future__ import annotations

LIFETIME_FREE_EMAILS = frozenset({
    "spartamacrey@gmail.com",
    "teamnimoxglobal@gmail.com",
})

INITIAL_CREATOR_ACCOUNTS = {
    "youtube": (
        {"handle": "@projectn1mox", "status": "authorization_required"},
        {"handle": "@kiddybuddy-n1", "status": "authorization_required"},
    ),
    "instagram": (
        {"handle": "@raufy_dai", "status": "authorization_required"},
        {"handle": "@kiddy.buddyofficial.ai.si", "status": "authorization_required"},
    ),
}

def normalize_email(email: str | None) -> str:
    return (email or "").strip().lower()

def has_lifetime_free_access(email: str | None) -> bool:
    return normalize_email(email) in LIFETIME_FREE_EMAILS
