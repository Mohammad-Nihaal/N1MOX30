from typing import Any

from pydantic import BaseModel


class ContentVersionCreate(BaseModel):
    changes: dict[str, Any]
    reason: str | None = None


class ContentVersionResponse(BaseModel):
    version: int
    created_at: str
    created_by: str
    reason: str | None = None
    changes: dict[str, Any]
    snapshot: dict[str, Any]


class ContentVersionListResponse(BaseModel):
    content_id: str
    current_version: int
    versions: list[ContentVersionResponse]


class ContentVersionCompareResponse(BaseModel):
    content_id: str
    first_version: int
    second_version: int
    differences: dict[str, dict[str, Any]]


class ContentVersionRestoreResponse(BaseModel):
    content_id: str
    restored_from_version: int
    new_version: ContentVersionResponse
