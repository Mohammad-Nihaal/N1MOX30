from pathlib import Path
from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """N1MOX30 application configuration."""

    # Application
    app_name: str = "N1MOX30"
    app_version: str = "1.0.0"
    environment: str = Field("development", validation_alias=AliasChoices("ENVIRONMENT", "APP_ENV"))

    # Database
    database_url: str = "sqlite:///./n1mox30.db"
    auto_create_tables: bool = True

    # Security
    secret_key: str = (
        "n1mox30-development-change-this-before-production"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Encryption
    encryption_key: str = Field("", validation_alias=AliasChoices("ENCRYPTION_KEY", "N1MOX_BYOK_ENCRYPTION_KEY"))

    # CORS
    cors_origins: str = ""
    allowed_hosts: str = "*"

    # Rate limiting
    enable_rate_limit: bool = True
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    # AI Provider Router
    ai_provider: str = "auto"
    ai_primary_provider: str = "openclaw"
    ai_fallback_provider: str = "openclaw"
    ai_enable_demo_fallback: bool = True

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    # Gemini
    gemini_api_key: str = ""

    # AWS Bedrock
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_session_token: str = ""
    aws_bearer_token_bedrock: str = ""
    aws_region: str = "us-east-1"
    aws_profile: str = ""
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    bedrock_max_tokens: int = 4096
    bedrock_enabled: bool = True

    # OpenClaw
    openclaw_enabled: bool = True
    openclaw_command: str = "openclaw"
    openclaw_model: str = "omniroute/auto"
    openclaw_timeout_seconds: int = 120

    # AI Reliability
    ai_timeout_seconds: int = 120
    ai_max_retries: int = 1

    # Voice
    voice_provider: str = "local"
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "JBFqnCBsd6RMkjVDRZzb"
    elevenlabs_model: str = "eleven_multilingual_v2"
    voice_output_dir: str = "storage/voice"

    # Google / YouTube
    google_client_id: str = ""
    google_client_secret: str = ""
    youtube_redirect_uri: str = (
        "http://127.0.0.1:8000/oauth/youtube/callback"
    )
    google_redirect_uri: str = (
        "http://127.0.0.1:8000/oauth/youtube/callback"
    )

    # Meta / Instagram
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_redirect_uri: str = (
        "http://127.0.0.1:8000/oauth/instagram/callback"
    )
    instagram_redirect_uri: str = (
        "http://127.0.0.1:8000/oauth/instagram/callback"
    )
    instagram_graph_version: str = "v24.0"

    # X
    x_client_id: str = ""
    x_client_secret: str = ""
    x_redirect_uri: str = (
        "http://127.0.0.1:8000/oauth/x/callback"
    )

    # TikTok
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    tiktok_redirect_uri: str = (
        "http://127.0.0.1:8000/oauth/tiktok/callback"
    )

    # Public media / mobile
    public_media_base_url: str = ""
    mobile_deep_link: str = "n1mox30://"

    # Frontend
    frontend_url: str = "http://localhost:5173"

    # Billing
    default_plan: str = "free"
    billing_currency: str = "INR"

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_token_expiry(cls, value: int) -> int:
        if value < 5:
            raise ValueError(
                "access_token_expire_minutes must be >= 5"
            )
        return value

    def cors_origin_list(self) -> list[str]:
        origins = set()

        if self.frontend_url:
            origins.add(
                self.frontend_url.rstrip("/")
            )

        if self.cors_origins:
            origins.update(
                origin.strip().rstrip("/")
                for origin in self.cors_origins.split(",")
                if origin.strip()
            )

        if self.environment.lower() != "production":
            origins.update(
                {
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                    "http://localhost:5174",
                    "http://127.0.0.1:5174",
                }
            )

        return sorted(origins)

    def validate_production_security(self) -> None:
        if self.environment.lower() != "production":
            return

        if len(self.secret_key) < 32:
            raise RuntimeError(
                "Production SECRET_KEY must contain at least 32 characters."
            )

        if self.secret_key.startswith(
            "n1mox30-development-change-this"
        ):
            raise RuntimeError(
                "Production SECRET_KEY must not use the development default."
            )

        if not self.encryption_key:
            raise RuntimeError(
                "Production ENCRYPTION_KEY is required."
            )

        if not self.cors_origin_list():
            raise RuntimeError(
                "Production CORS origins must be configured."
            )

    model_config = SettingsConfigDict(
       env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    instance = Settings()
    instance.validate_production_security()
    return instance


settings = get_settings()
