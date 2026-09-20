from __future__ import annotations

import re
from typing import Any, Callable

from app.core.config import settings
from app.services.ai.bedrock_provider import bedrock_provider
from app.services.ai.openclaw_provider import openclaw_provider


Validator = Callable[[str], bool]


class AIProviderRouter:

    def __init__(self) -> None:
        self.providers = {
            "openclaw": openclaw_provider,
            "bedrock": bedrock_provider,
        }

    @staticmethod
    def _clean_provider_output(text: Any) -> str:
        if text is None:
            return ""

        text = str(text)

        text = re.sub(
            r"\x1B\[[0-?]*[ -/]*[@-~]",
            "",
            text,
        )

        lines = []

        ignored = (
            "[provider-transport-fetch]",
            "[model-fetch]",
            "model.run via",
            "provider:",
            "model:",
            "outputs:",
        )

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            lower = line.lower()

            if any(x in lower for x in ignored):
                continue

            if re.match(r"^\d{2}:\d{2}:\d{2}\s+\[", line):
                continue

            # Normalize Markdown section headings so downstream
            # N1MOX30 parsers can consume model output reliably.
            line = re.sub(
                r"^#{1,6}\s+(TITLES|SCRIPT|CAPTION|HASHTAGS)\s*:\s*$",
                r"\1:",
                line,
                flags=re.IGNORECASE,
            )

            # Remove surrounding Markdown bold markers.
            line = re.sub(
                r"^\*\*(TITLES|SCRIPT|CAPTION|HASHTAGS)\s*:\s*\**$",
                r"\1:",
                line,
                flags=re.IGNORECASE,
            )

            lines.append(line)

        result = "\n".join(lines).strip()

        replacements = {
            "â€™": "'",
            "â€˜": "'",
            "â€œ": '"',
            "â€": '"',
            "â€“": "-",
            "â€”": "-",
            "â€¦": "...",
            "Â": "",
            "\u00a0": " ",
        }

        for old, new in replacements.items():
            result = result.replace(old, new)

        return result.strip()

    @staticmethod
    def _prepare_prompt(prompt: str) -> str:
        """
        Preserve N1MOX30's production prompt exactly.

        OpenClaw/OmniRoute can handle the creator prompt directly.
        Avoid rewriting or stripping creator instructions because doing
        so can change the model's intended behavior.
        """
        return prompt.strip()

    def generate(
        self,
        *,
        prompt: str,
        temperature: float = 0.7,
        validator: Validator | None = None,
    ) -> dict[str, Any]:

        if not prompt or not prompt.strip():
            raise ValueError("AI prompt cannot be empty.")

        mode = (
            getattr(settings, "ai_provider", "auto")
            or "auto"
        ).lower().strip()

        if mode == "demo":
            raise RuntimeError(
                "Demo mode does not use an external AI provider."
            )

        if mode in ("openclaw", "bedrock"):
            return self._generate_with_provider(
                mode,
                prompt=prompt,
                temperature=temperature,
                validator=validator,
                attempted=[mode],
                fallback=False,
            )

        if mode != "auto":
            raise ValueError(
                f"Unsupported router mode: {mode}"
            )

        return self._generate_auto(
            prompt=prompt,
            temperature=temperature,
            validator=validator,
        )

    def _generate_auto(
        self,
        *,
        prompt: str,
        temperature: float,
        validator: Validator | None,
    ) -> dict[str, Any]:

        primary = (
            getattr(settings, "ai_primary_provider", "")
            or ""
        ).lower().strip()

        fallback = (
            getattr(settings, "ai_fallback_provider", "")
            or ""
        ).lower().strip()

        route = []

        for provider in (primary, fallback):
            if (
                provider in self.providers
                and provider not in route
            ):
                route.append(provider)

        if not route:
            route = ["openclaw"]

        errors = []
        attempted = []

        for provider_name in route:

            attempted.append(provider_name)

            try:
                return self._generate_with_provider(
                    provider_name,
                    prompt=prompt,
                    temperature=temperature,
                    validator=validator,
                    attempted=attempted.copy(),
                    fallback=len(attempted) > 1,
                )

            except Exception as exc:
                errors.append(
                    f"{provider_name}: {exc}"
                )

        raise RuntimeError(
            "All configured AI providers failed. "
            + " | ".join(errors)
        )

    def _generate_with_provider(
        self,
        provider_name: str,
        *,
        prompt: str,
        temperature: float,
        validator: Validator | None,
        attempted: list[str],
        fallback: bool,
    ) -> dict[str, Any]:

        provider = self.providers.get(provider_name)

        if provider is None:
            raise RuntimeError(
                f"Unknown provider: {provider_name}"
            )

        if not provider.is_available():
            raise RuntimeError(
                f"Provider '{provider_name}' is not available."
            )

        prepared_prompt = self._prepare_prompt(prompt)

        raw = provider.generate(
            prompt=prepared_prompt,
            temperature=temperature,
        )

        text = self._clean_provider_output(raw)

        if not text:
            raise RuntimeError(
                f"Provider '{provider_name}' returned empty output."
            )

        # Provider availability and content-format validation are separate
        # concerns. OpenClaw may return valid creator content with minor
        # formatting differences, which the creator service can normalize.
        # Do not fail over to another provider merely because the optional
        # structured validator rejects formatting.
        if validator is not None:
            try:
                valid = bool(validator(text))
            except Exception:
                valid = False

            if not valid:
                # Preserve the real OpenClaw response for the higher-level
                # creator parser instead of triggering provider failover.
                pass

        return {
            "provider": provider_name,
            "text": text,
            "attempted_providers": attempted,
            "fallback_used": fallback,
        }


ai_provider_router = AIProviderRouter()

