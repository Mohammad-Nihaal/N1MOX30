from app.services.media_providers.base import (
    MediaStorageProvider,
)

from app.services.media_providers.local import (
    LocalMediaStorageProvider,
)


class MediaProviderFactory:
    """
    Central provider factory.

    Future providers can be registered here:

    - local
    - s3
    - cloudinary
    - gcs
    - azure
    """

    _providers: dict[
        str,
        MediaStorageProvider,
    ] = {}

    @classmethod
    def get_provider(
        cls,
        provider_name: str = "local",
    ) -> MediaStorageProvider:
        """
        Return the requested storage provider.
        """

        normalized_name = (
            provider_name
            .strip()
            .lower()
        )

        if normalized_name in cls._providers:
            return cls._providers[
                normalized_name
            ]

        if normalized_name == "local":
            provider = (
                LocalMediaStorageProvider()
            )

            cls._providers[
                normalized_name
            ] = provider

            return provider

        raise ValueError(
            "Unsupported media storage provider: "
            f"{provider_name}"
        )