from __future__ import annotations

import json
from typing import Any

from app.core.config import settings


class BedrockProvider:
    """
    AI provider for Amazon Bedrock.

    This provider uses the Bedrock Runtime API and
    normalizes the response into plain text.
    """

    name = "bedrock"

    def is_available(self) -> bool:
        """
        Check whether Bedrock is configured.

        A real API request is intentionally not made here
        to avoid unnecessary model usage.
        """

        return bool(
            settings.bedrock_enabled
            and settings.bedrock_model_id
        )

    def generate(
        self,
        *,
        prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """
        Run text inference through Amazon Bedrock.
        """

        if not settings.bedrock_enabled:
            raise RuntimeError(
                "Amazon Bedrock provider is disabled."
            )

        if not settings.bedrock_model_id:
            raise RuntimeError(
                "BEDROCK_MODEL_ID is not configured."
            )

        try:
            import boto3

        except ImportError as exc:
            raise RuntimeError(
                "boto3 is not installed. "
                "Run: pip install boto3"
            ) from exc

        try:
            session_kwargs: dict[str, Any] = {
                "region_name": settings.aws_region,
            }

            if settings.aws_profile:
                session_kwargs["profile_name"] = settings.aws_profile

            if settings.aws_access_key_id and settings.aws_secret_access_key:
                session_kwargs.update(
                    {
                        "aws_access_key_id": settings.aws_access_key_id,
                        "aws_secret_access_key": settings.aws_secret_access_key,
                    }
                )

                if settings.aws_session_token:
                    session_kwargs["aws_session_token"] = settings.aws_session_token

            session = boto3.Session(**session_kwargs)
            client = session.client("bedrock-runtime")

            response = client.converse(
                modelId=settings.bedrock_model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt,
                            }
                        ],
                    }
                ],
                inferenceConfig={
                    "temperature": temperature,
                    "maxTokens": settings.bedrock_max_tokens,
                },
            )

        except Exception as exc:
            raise RuntimeError(
                f"Bedrock inference failed: {exc}"
            ) from exc

        return self._extract_response(
            response
        )

    @staticmethod
    def _extract_response(
        response: dict[str, Any],
    ) -> str:
        """
        Extract text from a Bedrock Converse API response.
        """

        try:
            content = (
                response["output"]
                ["message"]
                ["content"]
            )

        except (
            KeyError,
            TypeError,
        ) as exc:
            raise RuntimeError(
                "Bedrock returned an unexpected response."
            ) from exc

        text_parts: list[str] = []

        for item in content:
            if isinstance(
                item,
                dict,
            ):
                text = item.get("text")

                if text:
                    text_parts.append(
                        str(text)
                    )

        result = "\n".join(
            text_parts
        ).strip()

        if not result:
            raise RuntimeError(
                "Bedrock returned an empty response."
            )

        return result


bedrock_provider = BedrockProvider()