import os
from dataclasses import dataclass


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ProductionConfig:
    environment: str
    debug: bool
    youtube_client_id: str | None
    youtube_client_secret: str | None
    encryption_key: str | None
    allow_real_publish: bool

    @property
    def youtube_configured(self) -> bool:
        return bool(
            self.youtube_client_id
            and self.youtube_client_secret
        )

    @property
    def token_security_ready(self) -> bool:
        key = self.encryption_key
        return bool(key and len(key) >= 32)

    @property
    def publishing_ready(self) -> bool:
        return (
            self.allow_real_publish
            and self.youtube_configured
            and self.token_security_ready
        )


def get_production_config() -> ProductionConfig:
    return ProductionConfig(
        environment=os.getenv(
            "N1MOX_ENV",
            "development",
        ),
        debug=_bool("N1MOX_DEBUG", False),
        youtube_client_id=os.getenv(
            "YOUTUBE_CLIENT_ID"
        ),
        youtube_client_secret=os.getenv(
            "YOUTUBE_CLIENT_SECRET"
        ),
        encryption_key=os.getenv(
            "N1MOX_TOKEN_ENCRYPTION_KEY"
        ),
        allow_real_publish=_bool(
            "N1MOX_ALLOW_REAL_PUBLISH",
            False,
        ),
    )