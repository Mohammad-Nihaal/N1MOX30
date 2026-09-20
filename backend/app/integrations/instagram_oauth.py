from app.integrations.social_oauth import (
    instagram_authorization_url,
)
from app.core.config import settings

INSTAGRAM_AUTH_URL = f"https://www.facebook.com/{settings.instagram_graph_version}/dialog/oauth"

def instagram_oauth_configured() -> bool:
    return bool(settings.meta_app_id and settings.meta_app_secret)

def get_instagram_authorization_url(state: str) -> str:
    return instagram_authorization_url(state)
