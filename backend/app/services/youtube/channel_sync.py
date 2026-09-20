import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STORAGE = PROJECT_ROOT / "storage" / "youtube"
CHANNEL_STORAGE = STORAGE / "channels"
VIDEO_STORAGE = STORAGE / "videos"

CHANNEL_STORAGE.mkdir(parents=True, exist_ok=True)
VIDEO_STORAGE.mkdir(parents=True, exist_ok=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _channel_path(account_id):
    return CHANNEL_STORAGE / f"{account_id}.json"


def _video_path(account_id):
    return VIDEO_STORAGE / f"{account_id}.json"


def _request(url, access_token):
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def sync_channel(account_id, access_token=None):
    if not access_token:
        return {
            "status": "authorization_required",
            "account_id": account_id,
        }

    try:
        params = urllib.parse.urlencode({
            "part": "snippet,statistics,contentDetails",
            "mine": "true",
        })

        data = _request(
            f"https://www.googleapis.com/youtube/v3/channels?{params}",
            access_token,
        )

        items = data.get("items", [])

        if not items:
            return {
                "status": "not_found",
                "account_id": account_id,
            }

        item = items[0]
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        content_details = item.get("contentDetails", {})

        channel = {
            "account_id": account_id,
            "channel_id": item.get("id"),
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "custom_url": snippet.get("customUrl"),
            "published_at": snippet.get("publishedAt"),
            "thumbnail": (
                snippet.get("thumbnails", {})
                .get("default", {})
                .get("url")
            ),
            "country": snippet.get("country"),
            "view_count": int(statistics.get("viewCount", 0) or 0),
            "subscriber_count": int(
                statistics.get("subscriberCount", 0) or 0
            ),
            "video_count": int(statistics.get("videoCount", 0) or 0),
            "uploads_playlist": (
                content_details
                .get("relatedPlaylists", {})
                .get("uploads")
            ),
            "synced_at": _now(),
        }

        _channel_path(account_id).write_text(
            json.dumps(channel, indent=2),
            encoding="utf-8",
        )

        return {
            "status": "synced",
            "channel": channel,
        }

    except Exception as exc:
        return {
            "status": "failed",
            "account_id": account_id,
            "error": str(exc),
        }


def get_channel(account_id):
    path = _channel_path(account_id)

    if not path.exists():
        return {
            "status": "not_found",
            "account_id": account_id,
        }

    return {
        "status": "available",
        "channel": json.loads(path.read_text(encoding="utf-8")),
    }


def save_channel_videos(account_id, videos):
    payload = {
        "account_id": account_id,
        "videos": videos,
        "updated_at": _now(),
    }

    _video_path(account_id).write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    return payload


def get_channel_videos(account_id):
    path = _video_path(account_id)

    if not path.exists():
        return {
            "status": "not_found",
            "account_id": account_id,
            "videos": [],
        }

    return json.loads(path.read_text(encoding="utf-8"))