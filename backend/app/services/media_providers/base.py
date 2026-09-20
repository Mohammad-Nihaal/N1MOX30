from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass
class StoredMediaResult:
    """
    Standard result returned by every
    media storage provider.
    """

    storage_provider: str

    storage_path: str

    public_url: str | None

    file_size_bytes: int

    original_filename: str


class MediaStorageProvider(ABC):
    """
    Base contract for media storage providers.

    Future implementations can include:

    - AWS S3
    - Cloudinary
    - Google Cloud Storage
    - Azure Blob Storage
    - Supabase Storage
    - Custom provider
    """

    provider_name: str

    @abstractmethod
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
        Store a media file and return
        a standard storage result.
        """

        raise NotImplementedError

    @abstractmethod
    def delete_file(
        self,
        *,
        storage_path: str,
    ) -> None:
        """
        Delete a stored media file.
        """

        raise NotImplementedError

    @abstractmethod
    def file_exists(
        self,
        *,
        storage_path: str,
    ) -> bool:
        """
        Check whether a stored file exists.
        """

        raise NotImplementedError