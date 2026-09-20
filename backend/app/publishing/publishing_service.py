from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models.connected_account import ConnectedAccount
from app.models.content import Content
from app.publishing.providers.base import PublishRequest
from app.publishing.providers.factory import PublishingProviderFactory
from app.core.config import settings
from app.services.youtube_service import (
    is_token_expired,
    refresh_youtube_access_token,
)


class PublishingService:
    """
    Central publishing service.

    Responsibilities:
    - Resolve authorized platform accounts.
    - Refresh expired YouTube tokens.
    - Validate publish assets.
    - Delegate publishing to platform adapters.
    - Persist content publishing state.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_account(
        self,
        *,
        user_id: str,
        platform: str,
        account_id: str | None = None,
    ) -> ConnectedAccount:
        query = (
            self.db.query(ConnectedAccount)
            .filter(
                ConnectedAccount.user_id == user_id,
                ConnectedAccount.platform == platform,
                ConnectedAccount.is_active.is_(True),
                ConnectedAccount.is_authorized.is_(True),
            )
        )

        if account_id:
            query = query.filter(
                ConnectedAccount.id == account_id
            )

        account = query.first()

        if not account:
            raise ValueError(
                f"No authorized {platform} account is connected."
            )

        if not account.access_token:
            raise ValueError(
                f"{platform} access token is missing."
            )

        return account

    def get_valid_access_token(
        self,
        account: ConnectedAccount,
    ) -> str:
        if account.platform != "youtube":
            if not account.access_token:
                raise ValueError(
                    "Connected account access token is missing."
                )

            return account.access_token

        if not is_token_expired(
            account.token_expires_at
        ):
            return account.access_token

        if not account.refresh_token:
            account.is_authorized = False
            self.db.commit()

            raise ValueError(
                "YouTube refresh token is missing. "
                "Please reconnect the account."
            )

        try:
            refreshed = refresh_youtube_access_token(
                account.refresh_token
            )
        except ValueError as error:
            account.is_authorized = False
            self.db.commit()
            raise ValueError(
                f"YouTube token refresh failed: {error}"
            ) from error

        account.access_token = refreshed["access_token"]
        account.token_expires_at = (
            refreshed["token_expires_at"]
        )
        account.is_active = True
        account.is_authorized = True

        self.db.commit()
        self.db.refresh(account)

        return account.access_token

    def publish(
        self,
        *,
        user_id: str,
        platform: str,
        video_path: str,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        privacy_status: str = "private",
        category_id: str = "22",
        thumbnail_path: str | None = None,
        publish_at: str | None = None,
        account_id: str | None = None,
        content_id: str | None = None,
        media_url: str | None = None,
        media_type: str = "video",
        platform_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        platform = str(platform or "").strip().lower()

        if not video_path:
            raise ValueError(
                "A rendered video path is required."
            )

        if not Path(video_path).exists():
            raise ValueError(
                f"Video file does not exist: {video_path}"
            )

        account = self.get_account(
            user_id=user_id,
            platform=platform,
            account_id=account_id,
        )

        access_token = self.get_valid_access_token(
            account
        )

        provider = PublishingProviderFactory.get(
            platform
        )

        # Automatically derive a public media URL from the rendered local asset
        # when a public media base URL is configured. This removes the need for
        # the creator to paste a URL into the Publishing Center.
        if platform in {"instagram", "tiktok"} and not media_url and settings.public_media_base_url:
            resolved = Path(video_path).resolve()
            storage_root = Path("storage/media").resolve()
            try:
                relative = resolved.relative_to(storage_root)
                media_url = settings.public_media_base_url.rstrip("/") + "/media/" + relative.as_posix()
            except ValueError:
                pass

        request = PublishRequest(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags or [],
            privacy_status=privacy_status,
            category_id=category_id,
            thumbnail_path=thumbnail_path,
            publish_at=publish_at,
            media_url=media_url,
            media_type=media_type,
            platform_options=platform_options or {},
        )

        result = provider.publish(
            access_token=access_token,
            request=request,
        )

        content = None

        if content_id:
            content = (
                self.db.query(Content)
                .filter(
                    Content.id == content_id,
                    Content.user_id == user_id,
                )
                .first()
            )

        if content:
            content.status = (
                "published"
                if result.status == "published"
                else result.status
            )

            self.db.commit()
            self.db.refresh(content)

        return {
            "platform": result.platform,
            "status": result.status,
            "external_id": result.external_id,
            "url": result.url,
            "account_id": account.id,
            "account_name": account.account_name,
            "content_id": content.id if content else content_id,
            "response": result.response,
            "error": result.error,
        }

    def preview(
        self,
        *,
        user_id: str,
        platform: str,
        video_path: str,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        privacy_status: str = "private",
        category_id: str = "22",
        thumbnail_path: str | None = None,
        account_id: str | None = None,
        media_url: str | None = None,
        media_type: str = "video",
        platform_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        account = self.get_account(
            user_id=user_id,
            platform=platform,
            account_id=account_id,
        )

        video = Path(video_path)

        thumbnail = (
            Path(thumbnail_path)
            if thumbnail_path
            else None
        )

        return {
            "platform": platform,
            "account_id": account.id,
            "account_name": account.account_name,
            "authorized": account.is_authorized,
            "video": {
                "path": str(video),
                "exists": video.exists(),
                "size_bytes": (
                    video.stat().st_size
                    if video.exists()
                    else 0
                ),
            },
            "metadata": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "privacy_status": privacy_status,
                "category_id": category_id,
            },
            "thumbnail": {
                "path": str(thumbnail)
                if thumbnail
                else None,
                "exists": (
                    thumbnail.exists()
                    if thumbnail
                    else False
                ),
            },
            "media_url": media_url,
            "media_type": media_type,
            "platform_options": platform_options or {},
            "ready": (
                (media_url if platform in {"instagram", "tiktok"} else True)
                and video.exists()
                and video.is_file()
                and (
                    not thumbnail
                    or thumbnail.exists()
                )
            ),
        }
