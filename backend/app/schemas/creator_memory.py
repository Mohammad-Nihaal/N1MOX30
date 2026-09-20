from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateCreatorMemoryRequest(BaseModel):
    memory_type: str = Field(min_length=1, max_length=100)
    memory_key: str = Field(min_length=1, max_length=255)
    memory_value: str = Field(min_length=1)
    source: str = Field(default="user", min_length=1, max_length=100)
    importance_score: int = Field(default=5, ge=1, le=10)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)


class UpdateCreatorMemoryRequest(BaseModel):
    memory_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    memory_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    memory_value: str | None = Field(
        default=None,
        min_length=1,
    )

    source: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    importance_score: int | None = Field(
        default=None,
        ge=1,
        le=10,
    )

    confidence_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    is_active: bool | None = None


class CreatorMemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    memory_type: str
    memory_key: str
    memory_value: str
    source: str
    importance_score: int
    confidence_score: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CreatorMemoryListResponse(BaseModel):
    total: int
    memories: list[CreatorMemoryResponse]


class CreatorMemoryContextItem(BaseModel):
    id: str
    memory_type: str
    memory_key: str
    memory_value: str
    source: str
    importance_score: int
    confidence_score: float


class CreatorMemoryContextResponse(BaseModel):
    total: int
    memories: list[CreatorMemoryContextItem]


class CreatorMemorySearchResponse(BaseModel):
    total: int
    query: str
    memories: list[CreatorMemoryResponse]