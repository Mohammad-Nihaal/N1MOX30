from __future__ import annotations

import base64
import hashlib
import secrets
from urllib.parse import urlencode

import httpx

from app.core.config import settings


def _get(url: str, params: dict):
    response = httpx.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _post(url: str, data: dict):
    response = httpx.post(url, data=data, timeout=30)
    response.raise_for_status()
    return response.json()


# ---------------- Instagram / Meta ----------------

def instagram_authorization_url(state: str) -> str:
    if not settings.meta_app_id or not settings.meta_app_secret:
        raise ValueError("Meta/Instagram OAuth is not configured.")
    params = {
        "client_id": settings.meta_app_id,
        "redirect_uri": settings.instagram_redirect_uri,
        "response_type": "code",
        "scope": "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement",
        "state": state,
    }
    return "https://www.facebook.com/{}/dialog/oauth?{}".format(
        settings.instagram_graph_version,
        urlencode(params),
    )


def instagram_exchange_code(code: str) -> dict:
    version = settings.instagram_graph_version
    token = _get(
        f"https://graph.facebook.com/{version}/oauth/access_token",
        {
            "client_id": settings.meta_app_id,
            "client_secret": settings.meta_app_secret,
            "redirect_uri": settings.instagram_redirect_uri,
            "code": code,
        },
    )
    short_token = token["access_token"]
    long_token = _get(
        f"https://graph.facebook.com/{version}/oauth/access_token",
        {
            "grant_type": "fb_exchange_token",
            "client_id": settings.meta_app_id,
            "client_secret": settings.meta_app_secret,
            "fb_exchange_token": short_token,
        },
    )
    access_token = long_token.get("access_token", short_token)
    pages = _get(
        f"https://graph.facebook.com/{version}/me/accounts",
        {
            "fields": "id,name,access_token,instagram_business_account{id,username,name}",
            "access_token": access_token,
        },
    )
    ig = None
    page = None
    for item in pages.get("data", []):
        if item.get("instagram_business_account"):
            page = item
            ig = item["instagram_business_account"]
            break
    if not ig:
        raise ValueError(
            "No Instagram professional account linked to a Facebook Page was found."
        )
    return {
        "access_token": access_token,
        "platform_account_id": ig["id"],
        "account_name": ig.get("username") or ig.get("name") or "Instagram",
        "page_id": page.get("id") if page else None,
        "page_access_token": page.get("access_token") if page else None,
        "expires_in": long_token.get("expires_in"),
    }


# ---------------- X / Twitter OAuth 2 PKCE ----------------

def create_x_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    return verifier, challenge


def x_authorization_url(state: str, code_challenge: str) -> str:
    if not settings.x_client_id or not settings.x_client_secret:
        raise ValueError("X OAuth is not configured.")
    params = {
        "response_type": "code",
        "client_id": settings.x_client_id,
        "redirect_uri": settings.x_redirect_uri,
        "scope": "users.read tweet.read tweet.write media.write offline.access",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return "https://twitter.com/i/oauth2/authorize?" + urlencode(params)


def x_exchange_code(code: str, code_verifier: str) -> dict:
    basic = base64.b64encode(
        f"{settings.x_client_id}:{settings.x_client_secret}".encode()
    ).decode()
    response = httpx.post(
        "https://api.x.com/2/oauth2/token",
        data={
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.x_redirect_uri,
            "code_verifier": code_verifier,
        },
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=30,
    )
    response.raise_for_status()
    token = response.json()
    profile = httpx.get(
        "https://api.x.com/2/users/me",
        params={"user.fields": "id,name,username,public_metrics"},
        headers={"Authorization": f"Bearer {token['access_token']}"},
        timeout=30,
    )
    profile.raise_for_status()
    user = profile.json()["data"]
    token.update({
        "platform_account_id": user["id"],
        "account_name": user.get("username") or user.get("name") or "X",
    })
    return token


# ---------------- TikTok OAuth ----------------

def tiktok_authorization_url(state: str) -> str:
    if not settings.tiktok_client_key or not settings.tiktok_client_secret:
        raise ValueError("TikTok OAuth is not configured.")
    params = {
        "client_key": settings.tiktok_client_key,
        "response_type": "code",
        "scope": "user.info.basic,user.info.profile,user.info.stats,video.publish,video.list",
        "redirect_uri": settings.tiktok_redirect_uri,
        "state": state,
    }
    return "https://www.tiktok.com/v2/auth/authorize/?" + urlencode(params)


def tiktok_exchange_code(code: str) -> dict:
    token = _post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        {
            "client_key": settings.tiktok_client_key,
            "client_secret": settings.tiktok_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.tiktok_redirect_uri,
        },
    )
    access_token = token["access_token"]
    profile = httpx.get(
        "https://open.tiktokapis.com/v2/user/info/",
        params={
            "fields": "open_id,union_id,avatar_url,display_name,profile_deep_link,follower_count,following_count,likes_count,video_count"
        },
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    profile.raise_for_status()
    user = profile.json().get("data", {}).get("user", {})
    token.update({
        "platform_account_id": user.get("open_id") or token.get("open_id"),
        "account_name": user.get("display_name") or "TikTok",
    })
    return token
