from __future__ import annotations

import shutil
from pathlib import Path

from app.services.media_providers.base import (
    MediaStorageProvider,
    StoredMediaResult,
)


class LocalMediaStorageProvider(
    MediaStorageProvider,
):
    """
    Local filesystem storage provider.

    Storage structure:

    storage/
        media/
            users/
                {user_id}/
                    {asset_id}/
                        filename.ext

    This provider is designed to be easily replaced
    later by S3, Cloudinary, or another provider.
    """

    provider_name = "local"

    def __init__(
        self,
        base_path: str = "storage/media",
    ) -> None:
        self.base_path = Path(
            base_path,
        )

        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _build_asset_directory(
        self,
        *,
        user_id: str,
        asset_id: str,
    ) -> Path:
        """
        Build the directory used by one asset.
        """

        asset_directory = (
            self.base_path
            / "users"
            / user_id
            / asset_id
        )

        asset_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return asset_directory

    def store_file(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        asset_id: str,
        content_type: str | None = None,
    ) -> StoredMediaResult:
        """
        Store uploaded bytes locally.
        """

        safe_filename = Path(
            filename,
        ).name

        asset_directory = (
            self._build_asset_directory(
                user_id=user_id,
                asset_id=asset_id,
            )
        )

        file_path = (
            asset_directory
            / safe_filename
        )

        file_path.write_bytes(
            file_bytes,
        )

        relative_path = str(
            file_path.resolve()
        )

        return StoredMediaResult(
            storage_provider=self.provider_name,
            storage_path=relative_path,
            public_url=None,
            file_size_bytes=len(
                file_bytes,
            ),
            original_filename=safe_filename,
        )

    def delete_file(
        self,
        *,
        storage_path: str,
    ) -> None:
        """
        Delete a local file and clean empty directories.
        """

        file_path = Path(
            storage_path,
        )

        if file_path.exists():
            file_path.unlink()

        current_directory = (
            file_path.parent
        )

        base_directory = (
            self.base_path.resolve()
        )

        while (
            current_directory.exists()
            and current_directory.resolve()
            != base_directory
        ):
            try:
                current_directory.rmdir()
            except OSError:
                break

            current_directory = (
                current_directory.parent
            )

    def file_exists(
        self,
        *,
        storage_path: str,
    ) -> bool:
        """
        Check local file existence.
        """

        return Path(
            storage_path,
        ).exists()

    def clear_user_assets(
        self,
        *,
        user_id: str,
    ) -> None:
        """
        Optional utility for future cleanup workflows.
        """

        user_directory = (
            self.base_path
            / "users"
            / user_id
        )

        if user_directory.exists():
            shutil.rmtree(
                user_directory,
            )