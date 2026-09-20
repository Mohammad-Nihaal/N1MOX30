from __future__ import annotations

import os

from app.core.config import settings
from app.services.ai.provider_router import ai_provider_router


def main() -> None:
    print("N1MOX30 AI ROUTER")
    print(f"mode={settings.ai_provider}")
    print(f"primary={settings.ai_primary_provider}")
    print(f"fallback={settings.ai_fallback_provider}")
    print(f"bedrock_enabled={settings.bedrock_enabled}")
    print(f"bedrock_model={settings.bedrock_model_id}")
    print(f"openclaw_available={ai_provider_router.providers['openclaw'].is_available()}")
    print(f"bedrock_available={ai_provider_router.providers['bedrock'].is_available()}")
    print("")
    print("No provider request is made by this script.")
    print("Use an actual AI generation request to test live failover.")


if __name__ == "__main__":
    main()
