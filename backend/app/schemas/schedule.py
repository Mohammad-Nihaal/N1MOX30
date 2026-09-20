from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ScheduleStatus = Literal[
    "pending",
    "processing",
    "published",
    "failed",
    "cancelled",
]


class ScheduleCreate(BaseModel):
    content_id: str = Field(min_length=1)

    scheduled_for: datetime

    connected_account_id: str | None = None


class ScheduleUpdate(BaseModel):
    scheduled_for: datetime | None = None

    connected_account_id: str | None = None

    status: ScheduleStatus | None = None


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    content_id: str
    connected_account_id: str | None
    scheduled_for: datetime
    status: str
    created_at: datetime
    updated_at: datetime