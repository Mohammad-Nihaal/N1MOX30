import os


def publishing_gate():
    environment = os.getenv(
        "N1MOX_ENV",
        "development",
    )

    real_publish = os.getenv(
        "N1MOX_ALLOW_REAL_PUBLISH",
        "false",
    ).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    encryption_ready = bool(
        os.getenv(
            "N1MOX_TOKEN_ENCRYPTION_KEY"
        )
    )

    youtube_ready = bool(
        os.getenv("YOUTUBE_CLIENT_ID")
        and os.getenv("YOUTUBE_CLIENT_SECRET")
    )

    return {
        "environment": environment,
        "real_publish_enabled": real_publish,
        "youtube_configured": youtube_ready,
        "token_security_ready": encryption_ready,
        "allowed": (
            real_publish
            and youtube_ready
            and encryption_ready
        ),
    }


def authorize_real_publish():
    gate = publishing_gate()

    if not gate["allowed"]:
        return {
            "status": "authorization_required",
            "reason": (
                "Real publishing is protected until "
                "production configuration and "
                "YouTube authorization are available."
            ),
            "gate": gate,
        }

    return {
        "status": "authorized",
        "gate": gate,
    }