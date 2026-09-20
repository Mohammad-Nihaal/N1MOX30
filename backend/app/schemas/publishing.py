from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PublishRequest(BaseModel):
    platform: str = "youtube"
    video_path: str
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    privacy_status: str = "private"
    category_id: str = "22"
    thumbnail_path: str | None = None
    publish_at: str | None = None
    account_id: str | None = None
    content_id: str | None = None
    media_url: str | None = None
    media_type: str = "video"
    platform_options: dict[str, Any] = Field(default_factory=dict)


class PublishResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: str
    status: str
    external_id: str | None = None
    url: str | None = None
    account_id: str | None = None
    account_name: str | None = None
    content_id: str | None = None
    media_url: str | None = None
    media_type: str = "video"
    platform_options: dict[str, Any] = Field(default_factory=dict)
    response: dict[str, Any] | None = None
    error: str | None = None


class PublishPreviewResponse(BaseModel):
    platform: str
    account_id: str
    account_name: str | None = None
    authorized: bool
    video: dict[str, Any]
    metadata: dict[str, Any]
    thumbnail: dict[str, Any]
    ready: bool
