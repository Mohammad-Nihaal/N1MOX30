from __future__ import annotations

import json
import mimetypes
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.media_asset import (
    MediaAsset,
)

from app.services.media_provider_factory import (
    MediaProviderFactory,
)


class MediaAssetService:
    """
    Central Media Asset Service.

    Responsibilities:

    - create assets
    - upload assets
    - track asset status
    - manage metadata
    - manage durations
    - retry failed assets
    - delete assets
    - connect VisualService output
    - support multiple providers
    """

    VALID_ASSET_TYPES = {
        "image",
        "video",
        "audio",
        "overlay",
        "thumbnail",
        "subtitle",
    }

    VALID_STATUSES = {
        "pending",
        "processing",
        "ready",
        "failed",
        "retrying",
        "deleted",
    }

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # =================================================
    # SERIALIZATION
    # =================================================

    def serialize_metadata(
        self,
        metadata: dict | None,
    ) -> str | None:
        """
        Convert metadata to database JSON text.
        """

        if metadata is None:
            return None

        return json.dumps(
            metadata,
            ensure_ascii=False,
        )

    def deserialize_metadata(
        self,
        metadata_json: str | None,
    ) -> dict:
        """
        Convert database JSON text to metadata.
        """

        if not metadata_json:
            return {}

        try:
            metadata = json.loads(
                metadata_json,
            )

            if isinstance(
                metadata,
                dict,
            ):
                return metadata

        except (
            json.JSONDecodeError,
            TypeError,
        ):
            pass

        return {}

    # =================================================
    # VALIDATION
    # =================================================

    def validate_asset_type(
        self,
        asset_type: str,
    ) -> str:
        """
        Validate and normalize asset type.
        """

        normalized_type = (
            asset_type
            .strip()
            .lower()
        )

        if (
            normalized_type
            not in self.VALID_ASSET_TYPES
        ):
            raise ValueError(
                "Unsupported asset type. "
                f"Supported types: "
                f"{', '.join(sorted(self.VALID_ASSET_TYPES))}"
            )

        return normalized_type

    def validate_status(
        self,
        status: str,
    ) -> str:
        """
        Validate asset status.
        """

        normalized_status = (
            status
            .strip()
            .lower()
        )

        if (
            normalized_status
            not in self.VALID_STATUSES
        ):
            raise ValueError(
                "Unsupported asset status. "
                f"Supported statuses: "
                f"{', '.join(sorted(self.VALID_STATUSES))}"
            )

        return normalized_status

    # =================================================
    # CREATE
    # =================================================

    def create_asset(
        self,
        *,
        user_id: str,
        project_id: str | None,
        content_id: str | None,
        asset_type: str,
        media_type: str,
        name: str,
        description: str | None,
        original_filename: str | None,
        storage_provider: str,
        storage_path: str | None,
        public_url: str | None,
        provider_asset_id: str | None,
        mime_type: str | None,
        file_extension: str | None,
        file_size_bytes: int | None,
        width: int | None,
        height: int | None,
        duration_seconds: float | None,
        frame_rate: float | None,
        scene_number: int | None,
        asset_role: str | None,
        metadata: dict | None,
        max_retries: int,
    ) -> MediaAsset:
        """
        Register a new media asset.
        """

        normalized_asset_type = (
            self.validate_asset_type(
                asset_type,
            )
        )

        asset = MediaAsset(
            user_id=user_id,
            project_id=project_id,
            content_id=content_id,
            asset_type=normalized_asset_type,
            media_type=media_type,
            name=name,
            description=description,
            original_filename=original_filename,
            storage_provider=storage_provider,
            storage_path=storage_path,
            public_url=public_url,
            provider_asset_id=provider_asset_id,
            mime_type=mime_type,
            file_extension=file_extension,
            file_size_bytes=file_size_bytes,
            width=width,
            height=height,
            duration_seconds=duration_seconds,
            frame_rate=frame_rate,
            scene_number=scene_number,
            asset_role=asset_role,
            status="pending",
            max_retries=max_retries,
            metadata_json=(
                self.serialize_metadata(
                    metadata,
                )
            ),
        )

        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        return asset

    # =================================================
    # UPLOAD
    # =================================================

    async def upload_asset(
        self,
        *,
        user_id: str,
        file: UploadFile,
        asset_type: str,
        name: str | None = None,
        project_id: str | None = None,
        content_id: str | None = None,
        scene_number: int | None = None,
        asset_role: str | None = None,
        description: str | None = None,
        metadata: dict | None = None,
        duration_seconds: float | None = None,
        storage_provider: str = "local",
    ) -> MediaAsset:
        """
        Upload and store a media asset.
        """

        normalized_asset_type = (
            self.validate_asset_type(
                asset_type,
            )
        )

        filename = (
            file.filename
            or "uploaded_asset"
        )

        file_extension = (
            Path(filename)
            .suffix
            .replace(".", "")
            .lower()
            or None
        )

        mime_type = (
            file.content_type
            or mimetypes.guess_type(
                filename,
            )[0]
            or "application/octet-stream"
        )

        asset_name = (
            name
            or Path(filename).stem
        )

        asset = MediaAsset(
            user_id=user_id,
            project_id=project_id,
            content_id=content_id,
            asset_type=normalized_asset_type,
            media_type=mime_type,
            name=asset_name,
            description=description,
            original_filename=filename,
            storage_provider=storage_provider,
            mime_type=mime_type,
            file_extension=file_extension,
            duration_seconds=duration_seconds,
            scene_number=scene_number,
            asset_role=asset_role,
            status="processing",
            metadata_json=(
                self.serialize_metadata(
                    metadata,
                )
            ),
        )

        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        try:
            file_bytes = await file.read()

            provider = (
                MediaProviderFactory.get_provider(
                    storage_provider,
                )
            )

            storage_result = (
                provider.store_file(
                    file_bytes=file_bytes,
                    filename=filename,
                    user_id=user_id,
                    asset_id=asset.id,
                    content_type=mime_type,
                )
            )

            asset.storage_provider = (
                storage_result.storage_provider
            )

            asset.storage_path = (
                storage_result.storage_path
            )

            asset.public_url = (
                storage_result.public_url
            )

            asset.file_size_bytes = (
                storage_result.file_size_bytes
            )

            asset.original_filename = (
                storage_result.original_filename
            )

            asset.status = "ready"

            asset.processed_at = (
                datetime.utcnow()
            )

            asset.error_message = None

            self.db.commit()
            self.db.refresh(asset)

            return asset

        except Exception as error:

            asset.status = "failed"

            asset.error_message = str(
                error,
            )

            self.db.commit()
            self.db.refresh(asset)

            raise

    # =================================================
    # GET
    # =================================================

    def get_asset(
        self,
        *,
        asset_id: str,
        user_id: str,
    ) -> MediaAsset | None:
        """
        Get one asset belonging to the user.
        """

        return (
            self.db.query(MediaAsset)
            .filter(
                MediaAsset.id == asset_id,
                MediaAsset.user_id == user_id,
            )
            .first()
        )

    def get_assets(
        self,
        *,
        user_id: str,
        project_id: str | None = None,
        content_id: str | None = None,
        asset_type: str | None = None,
        status: str | None = None,
        scene_number: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[MediaAsset], int]:
        """
        Get media assets with filtering.
        """

        query = (
            self.db.query(MediaAsset)
            .filter(
                MediaAsset.user_id == user_id,
                MediaAsset.status != "deleted",
            )
        )

        if project_id is not None:
            query = query.filter(
                MediaAsset.project_id
                == project_id,
            )

        if content_id is not None:
            query = query.filter(
                MediaAsset.content_id
                == content_id,
            )

        if asset_type is not None:

            normalized_asset_type = (
                self.validate_asset_type(
                    asset_type,
                )
            )

            query = query.filter(
                MediaAsset.asset_type
                == normalized_asset_type,
            )

        if status is not None:

            normalized_status = (
                self.validate_status(
                    status,
                )
            )

            query = query.filter(
                MediaAsset.status
                == normalized_status,
            )

        if scene_number is not None:
            query = query.filter(
                MediaAsset.scene_number
                == scene_number,
            )

        total = query.count()

        assets = (
            query
            .order_by(
                MediaAsset.created_at.desc(),
            )
            .offset(offset)
            .limit(
                min(
                    max(limit, 1),
                    500,
                )
            )
            .all()
        )

        return assets, total

    # =================================================
    # UPDATE
    # =================================================

    def update_asset(
        self,
        *,
        asset: MediaAsset,
        data: dict,
    ) -> MediaAsset:
        """
        Update asset information.
        """

        for field_name, value in data.items():

            if value is None:
                continue

            if field_name == "metadata":

                asset.metadata_json = (
                    self.serialize_metadata(
                        value,
                    )
                )

                continue

            if hasattr(
                asset,
                field_name,
            ):
                setattr(
                    asset,
                    field_name,
                    value,
                )

        self.db.commit()
        self.db.refresh(asset)

        return asset

    # =================================================
    # STATUS
    # =================================================

    def update_asset_status(
        self,
        *,
        asset: MediaAsset,
        status: str,
        error_message: str | None = None,
    ) -> MediaAsset:
        """
        Update media asset processing status.
        """

        normalized_status = (
            self.validate_status(
                status,
            )
        )

        asset.status = (
            normalized_status
        )

        asset.error_message = (
            error_message
        )

        if normalized_status == "ready":

            asset.processed_at = (
                datetime.utcnow()
            )

            asset.error_message = None

        self.db.commit()
        self.db.refresh(asset)

        return asset

    # =================================================
    # RETRY
    # =================================================

    def retry_asset(
        self,
        *,
        asset: MediaAsset,
    ) -> MediaAsset:
        """
        Mark a failed asset as retrying.

        Actual provider retry execution can later
        be handled by a background worker.
        """

        if (
            asset.retry_count
            >= asset.max_retries
        ):
            raise ValueError(
                "Maximum retry count reached."
            )

        if asset.status not in {
            "failed",
            "pending",
        }:
            raise ValueError(
                "Only failed or pending assets "
                "can be retried."
            )

        asset.retry_count += 1

        asset.status = "retrying"

        asset.error_message = None

        self.db.commit()
        self.db.refresh(asset)

        return asset

    # =================================================
    # MARK PROCESSING
    # =================================================

    def mark_processing(
        self,
        *,
        asset: MediaAsset,
    ) -> MediaAsset:
        """
        Mark an asset as currently processing.
        """

        asset.status = "processing"

        asset.error_message = None

        self.db.commit()
        self.db.refresh(asset)

        return asset

    # =================================================
    # PROVIDER FILE CHECK
    # =================================================

    def verify_asset_file(
        self,
        *,
        asset: MediaAsset,
    ) -> bool:
        """
        Verify the underlying stored file.
        """

        if not asset.storage_path:
            return False

        try:
            provider = (
                MediaProviderFactory.get_provider(
                    asset.storage_provider,
                )
            )

            return provider.file_exists(
                storage_path=asset.storage_path,
            )

        except Exception:
            return False

    # =================================================
    # DELETE
    # =================================================

    def delete_asset(
        self,
        *,
        asset: MediaAsset,
        delete_file: bool = True,
    ) -> None:
        """
        Delete an asset.

        Stored files are deleted when possible.
        """

        if (
            delete_file
            and asset.storage_path
        ):
            try:
                provider = (
                    MediaProviderFactory.get_provider(
                        asset.storage_provider,
                    )
                )

                provider.delete_file(
                    storage_path=asset.storage_path,
                )

            except Exception:
                pass

        self.db.delete(asset)
        self.db.commit()

    # =================================================
    # RESPONSE
    # =================================================

    def asset_to_response(
        self,
        asset: MediaAsset,
    ) -> dict:
        """
        Convert asset into API-safe response.
        """

        return {
            "id": asset.id,
            "user_id": asset.user_id,
            "project_id": asset.project_id,
            "content_id": asset.content_id,
            "asset_type": asset.asset_type,
            "media_type": asset.media_type,
            "name": asset.name,
            "description": asset.description,
            "original_filename": (
                asset.original_filename
            ),
            "storage_provider": (
                asset.storage_provider
            ),
            "storage_path": (
                asset.storage_path
            ),
            "public_url": (
                asset.public_url
            ),
            "provider_asset_id": (
                asset.provider_asset_id
            ),
            "mime_type": asset.mime_type,
            "file_extension": (
                asset.file_extension
            ),
            "file_size_bytes": (
                asset.file_size_bytes
            ),
            "width": asset.width,
            "height": asset.height,
            "duration_seconds": (
                asset.duration_seconds
            ),
            "frame_rate": asset.frame_rate,
            "scene_number": (
                asset.scene_number
            ),
            "asset_role": asset.asset_role,
            "status": asset.status,
            "retry_count": asset.retry_count,
            "max_retries": asset.max_retries,
            "error_message": (
                asset.error_message
            ),
            "metadata": (
                self.deserialize_metadata(
                    asset.metadata_json,
                )
            ),
            "created_at": asset.created_at,
            "updated_at": asset.updated_at,
            "processed_at": asset.processed_at,
        }