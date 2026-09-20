from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


YOUTUBE_API="https://www.googleapis.com/youtube/v3"


def _request(
    url: str,
    access_token: str,
    method: str="GET",
    body: dict | None=None,
) -> dict[str, Any]:

    data=None

    if body is not None:
        data=json.dumps(body).encode("utf-8")

    request=urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request,timeout=30) as response:
            raw=response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except Exception as exc:
        return {
            "status":"failed",
            "error":str(exc),
        }


def get_channel(
    access_token: str,
) -> dict[str,Any]:

    query=urllib.parse.urlencode({
        "part":"snippet,statistics,contentDetails",
        "mine":"true",
    })

    result=_request(
        f"{YOUTUBE_API}/channels?{query}",
        access_token,
    )

    if "error" in result:
        return result

    items=result.get("items",[])

    if not items:
        return {
            "status":"not_found",
            "channel":None,
        }

    item=items[0]

    return {
        "status":"connected",
        "channel":{
            "id":item.get("id"),
            "title":item.get("snippet",{}).get("title"),
            "description":item.get("snippet",{}).get("description"),
            "thumbnail":item.get("snippet",{}).get("thumbnails",{}).get("default",{}).get("url"),
            "statistics":item.get("statistics",{}),
            "uploads_playlist":item.get("contentDetails",{}).get("relatedPlaylists",{}).get("uploads"),
        },
    }


def get_recent_videos(
    access_token: str,
    uploads_playlist: str | None=None,
    max_results: int=10,
) -> dict[str,Any]:

    if not uploads_playlist:
        channel=get_channel(access_token)

        if channel.get("status")!="connected":
            return channel

        uploads_playlist=(
            channel.get("channel",{})
            .get("uploads_playlist")
        )

    if not uploads_playlist:
        return {
            "status":"not_found",
            "videos":[],
        }

    query=urllib.parse.urlencode({
        "part":"snippet,contentDetails",
        "playlistId":uploads_playlist,
        "maxResults":max_results,
    })

    result=_request(
        f"{YOUTUBE_API}/playlistItems?{query}",
        access_token,
    )

    if "error" in result:
        return result

    videos=[]

    for item in result.get("items",[]):
        snippet=item.get("snippet",{})
        resource=item.get("contentDetails",{})

        videos.append({
            "video_id":resource.get("videoId"),
            "title":snippet.get("title"),
            "description":snippet.get("description"),
            "published_at":snippet.get("publishedAt"),
            "thumbnail":snippet.get("thumbnails",{}).get("high",{}).get("url"),
        })

    return {
        "status":"ready",
        "videos":videos,
    }


def get_video_analytics(
    access_token: str,
    video_ids: list[str],
) -> dict[str,Any]:

    if not video_ids:
        return {
            "status":"ready",
            "videos":[],
        }

    query=urllib.parse.urlencode({
        "part":"statistics,snippet",
        "id":",".join(video_ids),
    })

    result=_request(
        f"{YOUTUBE_API}/videos?{query}",
        access_token,
    )

    if "error" in result:
        return result

    videos=[]

    for item in result.get("items",[]):
        stats=item.get("statistics",{})
        snippet=item.get("snippet",{})

        videos.append({
            "video_id":item.get("id"),
            "title":snippet.get("title"),
            "views":int(stats.get("viewCount",0)),
            "likes":int(stats.get("likeCount",0)),
            "comments":int(stats.get("commentCount",0)),
            "favorites":int(stats.get("favoriteCount",0)),
        })

    return {
        "status":"ready",
        "videos":videos,
    }