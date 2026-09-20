from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PlatformType = Literal["youtube", "instagram"]


class ConnectedAccountCreate(BaseModel):
    platform: PlatformType

    platform_account_id: str = Field(
        min_length=1,
        max_length=255,
    )

    account_name: str = Field(
        min_length=1,
        max_length=255,
    )


class ConnectedAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str

    platform: str
    platform_account_id: str
    account_name: str

    is_active: bool
    is_authorized: bool

    token_expires_at: datetime | None

    created_at: datetime
    updated_at: datetime