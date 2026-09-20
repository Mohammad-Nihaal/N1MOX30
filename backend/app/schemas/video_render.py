from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class RenderEnvironmentResponse(BaseModel):
    provider: str

    available: bool

    ffmpeg: str | None = None

    ffprobe: str | None = None


class VideoRenderRequest(BaseModel):
    renderer: str = "ffmpeg"


class VideoRenderResponse(BaseModel):
    success: bool

    timeline_id: str

    asset_id: str | None = None

    output_path: str | None = None

    duration_seconds: float = 0.0

    width: int = 0

    height: int = 0

    fps: float = 0.0

    file_size_bytes: int = 0

    mime_type: str = "video/mp4"

    provider: str = "unknown"

    error_message: str | None = None

    metadata: dict[str, Any] = {}


class RenderedAssetResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    user_id: str

    content_id: str | None

    asset_type: str

    media_type: str

    name: str

    storage_provider: str

    storage_path: str | None

    mime_type: str | None

    file_extension: str | None

    file_size_bytes: int | None

    width: int | None

    height: int | None

    duration_seconds: float | None

    frame_rate: float | None

    asset_role: str | None

    status: str

    created_at: datetime