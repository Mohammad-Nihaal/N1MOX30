from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class MediaAssetCreate(BaseModel):
    """Create or register a media asset."""

    project_id: str | None = None
    content_id: str | None = None

    asset_type: str = Field(
        min_length=2,
        max_length=50,
    )

    media_type: str = Field(
        default="unknown",
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    original_filename: str | None = Field(
        default=None,
        max_length=500,
    )

    storage_provider: str = Field(
        default="local",
        max_length=100,
    )

    storage_path: str | None = Field(
        default=None,
        max_length=1000,
    )

    public_url: str | None = Field(
        default=None,
        max_length=2000,
    )

    provider_asset_id: str | None = Field(
        default=None,
        max_length=500,
    )

    mime_type: str | None = Field(
        default=None,
        max_length=255,
    )

    file_extension: str | None = Field(
        default=None,
        max_length=50,
    )

    file_size_bytes: int | None = Field(
        default=None,
        ge=0,
    )

    width: int | None = Field(
        default=None,
        ge=1,
    )

    height: int | None = Field(
        default=None,
        ge=1,
    )

    duration_seconds: float | None = Field(
        default=None,
        ge=0,
    )

    frame_rate: float | None = Field(
        default=None,
        gt=0,
    )

    scene_number: int | None = Field(
        default=None,
        ge=1,
    )

    asset_role: str | None = Field(
        default=None,
        max_length=100,
    )

    metadata: dict[str, Any] | None = None

    max_retries: int = Field(
        default=3,
        ge=0,
        le=20,
    )


class MediaAssetUpdate(BaseModel):
    """Update editable media asset information."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    project_id: str | None = None
    content_id: str | None = None

    public_url: str | None = Field(
        default=None,
        max_length=2000,
    )

    provider_asset_id: str | None = Field(
        default=None,
        max_length=500,
    )

    width: int | None = Field(
        default=None,
        ge=1,
    )

    height: int | None = Field(
        default=None,
        ge=1,
    )

    duration_seconds: float | None = Field(
        default=None,
        ge=0,
    )

    frame_rate: float | None = Field(
        default=None,
        gt=0,
    )

    scene_number: int | None = Field(
        default=None,
        ge=1,
    )

    asset_role: str | None = Field(
        default=None,
        max_length=100,
    )

    metadata: dict[str, Any] | None = None


class MediaAssetStatusUpdate(BaseModel):
    """Update the processing state of an asset."""

    status: str = Field(
        min_length=2,
        max_length=50,
    )

    error_message: str | None = None


class MediaAssetResponse(BaseModel):
    """API response for one media asset."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    user_id: str

    project_id: str | None
    content_id: str | None

    asset_type: str
    media_type: str

    name: str
    description: str | None

    original_filename: str | None

    storage_provider: str
    storage_path: str | None
    public_url: str | None
    provider_asset_id: str | None

    mime_type: str | None
    file_extension: str | None
    file_size_bytes: int | None

    width: int | None
    height: int | None

    duration_seconds: float | None
    frame_rate: float | None

    scene_number: int | None
    asset_role: str | None

    status: str

    retry_count: int
    max_retries: int

    error_message: str | None

    metadata: dict[str, Any]

    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None


class MediaAssetListResponse(BaseModel):
    """Response containing media assets."""

    total: int

    assets: list[MediaAssetResponse]