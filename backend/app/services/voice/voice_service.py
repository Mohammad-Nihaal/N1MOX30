from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path
from typing import Any

import httpx
import pyttsx3

from app.core.config import settings


class VoiceService:
    """
    Voice generation service for the N1MOX30 automation pipeline.

    Responsibilities:
        - Accept the completed Script stage output.
        - Extract production-ready narration.
        - Normalize narration text.
        - Select a voice configuration.
        - Support provider abstraction.
        - Generate deterministic demo voice metadata.
        - Prepare a provider-neutral audio contract.

    The current implementation intentionally uses a DEMO provider.
    A real TTS provider can be added later without changing the
    automation workflow contract.
    """

    DEFAULT_PROVIDER = "demo"
    DEFAULT_VOICE = "n1mox-neutral"
    DEFAULT_LANGUAGE = "en-US"

    SUPPORTED_PROVIDERS = {
        "demo",
        "local",
        "openai",
        "elevenlabs",
        "google",
        "azure",
    }

    def __init__(
        self,
        provider: str | None = None,
    ):
        self.provider = (
            str(
                provider
                or getattr(settings, "voice_provider", self.DEFAULT_PROVIDER)
            )
            .strip()
            .lower()
        )
        if self.provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported voice provider: {self.provider}"
            )
    def generate_voice(
        self,
        *,
        topic: str,
        platform: str,
        command: str,
        script: dict[str, Any] | str,
    ) -> dict[str, Any]:
        """
        Generate voice output from the completed Script stage.

        The returned structure is provider-neutral so downstream
        Visuals and Video stages do not need to know which TTS
        provider was used.
        """

        topic = str(topic or "").strip()
        platform = str(platform or "youtube").strip().lower()
        command = str(command or "").strip()

        if not topic:
            raise ValueError("Voice generation requires a topic.")

        script_data = self._normalize_script_input(script)

        narration_sections = self._extract_narration_sections(
            script_data
        )

        if not narration_sections:
            raise ValueError(
                "Voice generation requires narration sections "
                "from the completed Script stage."
            )

        narration = self._combine_narration(
            narration_sections
        )

        if not narration:
            raise ValueError(
                "Voice generation requires non-empty narration."
            )

        voice_config = self._build_voice_config(
            script_data=script_data,
            platform=platform,
        )

        if self.provider == "demo":
            result = self._generate_demo_voice(
                topic=topic,
                platform=platform,
                command=command,
                script_data=script_data,
                narration_sections=narration_sections,
                narration=narration,
                voice_config=voice_config,
            )
        else:
            result = self._generate_provider_voice(
                topic=topic,
                platform=platform,
                command=command,
                script_data=script_data,
                narration_sections=narration_sections,
                narration=narration,
                voice_config=voice_config,
            )

        return self._normalize_result(result)

    # ---------------------------------------------------------
    # Script Input
    # ---------------------------------------------------------

    def _normalize_script_input(
        self,
        script: dict[str, Any] | str,
    ) -> dict[str, Any]:
        """
        Normalize the Script stage payload.

        The workflow engine may pass previously persisted output
        as JSON text, so the service accepts both dictionaries
        and strings.
        """

        if isinstance(script, dict):
            data = script
        elif isinstance(script, str):
            data = self._parse_json_string(script)
        else:
            raise ValueError(
                "Voice stage received an unsupported script format."
            )

        # The Script handler normally returns:
        #
        # {
        #     "stage": "script",
        #     "status": "completed",
        #     "execution": "script_service",
        #     "script": {...}
        # }
        #
        # Accept both the wrapper and the inner script object.

        if isinstance(data.get("script"), dict):
            return data["script"]

        return data

    def _parse_json_string(
        self,
        value: str,
    ) -> dict[str, Any]:
        """
        Parse persisted JSON safely.
        """

        import json

        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                "Voice stage received an empty script payload."
            )

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Voice stage received invalid JSON script output."
            ) from exc

        if not isinstance(parsed, dict):
            raise ValueError(
                "Voice stage script JSON must contain an object."
            )

        return parsed

    # ---------------------------------------------------------
    # Narration Extraction
    # ---------------------------------------------------------

    def _extract_narration_sections(
        self,
        script_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Extract narration from the structured Script sections.

        Each section retains its identity and timing so downstream
        audio/video stages can synchronize against the script.
        """

        raw_sections = script_data.get("sections", [])

        if not isinstance(raw_sections, list):
            raw_sections = []

        sections: list[dict[str, Any]] = []

        for index, raw_section in enumerate(raw_sections, start=1):
            if not isinstance(raw_section, dict):
                continue

            narration = self._clean_narration(
                raw_section.get("narration", "")
            )

            if not narration:
                continue

            section_name = str(
                raw_section.get(
                    "section",
                    f"section_{index}",
                )
            ).strip()

            duration = str(
                raw_section.get(
                    "duration",
                    "",
                )
            ).strip()

            purpose = str(
                raw_section.get(
                    "purpose",
                    "",
                )
            ).strip()

            visual_direction = str(
                raw_section.get(
                    "visual_direction",
                    "",
                )
            ).strip()

            sections.append(
                {
                    "index": index,
                    "section": section_name,
                    "duration": duration,
                    "purpose": purpose,
                    "narration": narration,
                    "visual_direction": visual_direction,
                    "estimated_word_count": self._word_count(
                        narration
                    ),
                }
            )

        # Some future providers/services may provide only a
        # complete script string. Preserve compatibility with that
        # format as a fallback.
        if not sections:
            complete_script = self._clean_narration(
                script_data.get("script", "")
            )

            if complete_script:
                sections.append(
                    {
                        "index": 1,
                        "section": "full_script",
                        "duration": "",
                        "purpose": "Complete narration",
                        "narration": complete_script,
                        "visual_direction": "",
                        "estimated_word_count": self._word_count(
                            complete_script
                        ),
                    }
                )

        return sections

    def _combine_narration(
        self,
        sections: list[dict[str, Any]],
    ) -> str:
        """
        Combine section narration while preserving readable
        paragraph boundaries.
        """

        return "\n\n".join(
            section["narration"]
            for section in sections
            if section.get("narration")
        ).strip()

    def _clean_narration(
        self,
        text: Any,
    ) -> str:
        """
        Clean common formatting artifacts without rewriting the
        creator's actual narration.
        """

        if text is None:
            return ""

        value = str(text)

        replacements = {
            "\r\n": "\n",
            "\r": "\n",
            "\u00a0": " ",
            "realquestion": "real question",
            "watchnext": "watch next",
            "futurewith": "future with",
            "matters": "matters",
        }

        for old, new in replacements.items():
            value = value.replace(old, new)

        value = re.sub(
            r"[ \t]+",
            " ",
            value,
        )

        value = re.sub(
            r"\n{3,}",
            "\n\n",
            value,
        )

        return value.strip()

    # ---------------------------------------------------------
    # Voice Configuration
    # ---------------------------------------------------------

    def _build_voice_config(
        self,
        *,
        script_data: dict[str, Any],
        platform: str,
    ) -> dict[str, Any]:
        """
        Build provider-neutral voice settings.

        These values can later be supplied by creator preferences,
        project settings, or an AI voice configuration UI.
        """

        production_notes = script_data.get(
            "production_notes",
            {},
        )

        if not isinstance(production_notes, dict):
            production_notes = {}

        delivery_style = str(
            production_notes.get(
                "delivery_style",
                "natural, confident, conversational",
            )
        ).strip()

        pacing = str(
            production_notes.get(
                "pacing",
                "dynamic",
            )
        ).strip()

        language = str(
            script_data.get(
                "language",
                self.DEFAULT_LANGUAGE,
            )
        ).strip()

        return {
            "voice_id": self.DEFAULT_VOICE,
            "language": language or self.DEFAULT_LANGUAGE,
            "delivery_style": delivery_style,
            "pacing": pacing,
            "platform": platform,
            "emotion": "natural",
            "stability": 0.75,
            "clarity": 0.85,
        }

    # ---------------------------------------------------------
    # Demo Provider
    # ---------------------------------------------------------

    def _generate_demo_voice(
        self,
        *,
        topic: str,
        platform: str,
        command: str,
        script_data: dict[str, Any],
        narration_sections: list[dict[str, Any]],
        narration: str,
        voice_config: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Produce a deterministic provider-neutral voice result.

        No audio API is called.

        This is intentionally useful for development because the
        downstream stages can consume the same contract that a
        real TTS provider will eventually produce.
        """

        word_count = self._word_count(narration)

        estimated_duration_seconds = self._estimate_duration(
            word_count=word_count,
            pacing=voice_config.get("pacing", ""),
        )

        audio_fingerprint = hashlib.sha256(
            narration.encode("utf-8")
        ).hexdigest()[:16]

        section_outputs = []

        elapsed_seconds = 0.0

        for section in narration_sections:
            section_words = int(
                section.get(
                    "estimated_word_count",
                    0,
                )
            )

            section_duration = self._estimate_duration(
                word_count=section_words,
                pacing=voice_config.get("pacing", ""),
            )

            start_time = elapsed_seconds
            end_time = start_time + section_duration

            section_outputs.append(
                {
                    "index": section["index"],
                    "section": section["section"],
                    "duration": section["duration"],
                    "narration": section["narration"],
                    "word_count": section_words,
                    "estimated_audio_start": self._format_seconds(
                        start_time
                    ),
                    "estimated_audio_end": self._format_seconds(
                        end_time
                    ),
                    "estimated_duration_seconds": round(
                        section_duration,
                        2,
                    ),
                    "audio_status": "planned",
                }
            )

            elapsed_seconds = end_time

        return {
            "stage": "voice",
            "status": "completed",
            "execution": "voice_service",
            "provider": "demo",
            "voice_status": "planned",
            "topic": topic,
            "platform": platform,
            "command": command,
            "voice": voice_config,
            "narration": {
                "text": narration,
                "word_count": word_count,
                "section_count": len(narration_sections),
            },
            "estimated_duration_seconds": round(
                estimated_duration_seconds,
                2,
            ),
            "audio": {
                "status": "not_rendered",
                "asset_type": "audio",
                "format": "wav",
                "sample_rate": 48000,
                "channels": 2,
                "duration_seconds": round(
                    estimated_duration_seconds,
                    2,
                ),
                "provider_asset_id": None,
                "file_path": None,
                "url": None,
                "content_hash": audio_fingerprint,
            },
            "timeline": section_outputs,
            "production": {
                "ready_for_tts_provider": True,
                "ready_for_visual_sync": True,
                "ready_for_video_pipeline": False,
            },
            "quality_controls": [
                "Narration extracted from completed Script stage.",
                "Narration is non-empty.",
                "Voice configuration is provider-neutral.",
                "Audio timing metadata is available.",
                "No fabricated audio URL or file path is returned.",
                "Demo provider does not claim that audio was rendered.",
            ],
        }

    # ---------------------------------------------------------
    # Real Provider Placeholder
    # ---------------------------------------------------------

    def _generate_provider_voice(
        self,
        *,
        topic: str,
        platform: str,
        command: str,
        script_data: dict[str, Any],
        narration_sections: list[dict[str, Any]],
        narration: str,
        voice_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate real audio using a configured production TTS provider."""
        provider = self.provider
        if provider == "local":
            return self._generate_local_voice(
                topic=topic,
                platform=platform,
                command=command,
                narration_sections=narration_sections,
                narration=narration,
                voice_config=voice_config,
            )
        if provider == "elevenlabs":
            return self._generate_elevenlabs_voice(
                topic=topic, platform=platform, command=command,
                narration_sections=narration_sections, narration=narration,
                voice_config=voice_config,
            )
        if provider == "openai":
            return self._generate_openai_voice(
                topic=topic, platform=platform, command=command,
                narration_sections=narration_sections, narration=narration,
                voice_config=voice_config,
            )
        raise ValueError(f"Voice provider '{provider}' is not configured for production output.")

    def _build_real_voice_result(
        self, *, topic: str, platform: str, command: str,
        narration_sections: list[dict[str, Any]], narration: str,
        voice_config: dict[str, Any], provider: str, file_path: Path,
        audio_format: str,
    ) -> dict[str, Any]:
        word_count = self._word_count(narration)
        estimated_duration = self._estimate_duration(word_count=word_count, pacing=voice_config.get("pacing", ""))
        section_outputs=[]
        elapsed=0.0
        for section in narration_sections:
            d=self._estimate_duration(word_count=int(section.get("estimated_word_count",0)), pacing=voice_config.get("pacing", ""))
            section_outputs.append({
                "index": section["index"], "section": section["section"],
                "duration": section["duration"], "narration": section["narration"],
                "word_count": int(section.get("estimated_word_count",0)),
                "estimated_audio_start": self._format_seconds(elapsed),
                "estimated_audio_end": self._format_seconds(elapsed+d),
                "estimated_duration_seconds": round(d,2),
                "audio_status": "generated",
            })
            elapsed += d
        return {
            "stage":"voice", "status":"completed", "execution":"voice_service",
            "provider":"local", "voice_status":"rendered", "topic":topic, "ready_for_video_pipeline":True,
            "platform":platform, "command":command, "voice":voice_config,
            "narration":{"text":narration,"word_count":word_count,"section_count":len(narration_sections)},
            "estimated_duration_seconds":round(estimated_duration,2),
            "audio":{
                "status":"rendered", "asset_type":"audio", "format":audio_format,
                "sample_rate":48000, "channels":2, "duration_seconds":round(estimated_duration,2),
                "provider_asset_id":None, "file_path":str(file_path.resolve()),
                "url":None, "content_hash":hashlib.sha256(file_path.read_bytes()).hexdigest(),
            },
            "timeline":section_outputs,
            "production":{"ready_for_tts_provider":True,"ready_for_visual_sync":True,"ready_for_video_pipeline":True},
            "quality_controls":["Narration extracted from completed Script stage.","Real provider audio generated.","Audio file exists and is non-empty.","Provider-neutral timing metadata generated."],
        }

    def _generate_elevenlabs_voice(self, **kwargs) -> dict[str, Any]:
        if not settings.elevenlabs_api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is required for production voice generation.")
        narration=kwargs["narration"]
        voice_id=settings.elevenlabs_voice_id
        response=httpx.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            params={"output_format":"mp3_44100_128"},
            headers={"xi-api-key":settings.elevenlabs_api_key,"Content-Type":"application/json"},
            json={"text":narration,"model_id":settings.elevenlabs_model},
            timeout=180,
        )
        response.raise_for_status()
        digest=hashlib.sha256(narration.encode()).hexdigest()
        out=Path(settings.voice_output_dir) / f"{digest}.mp3"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(response.content)
        if out.stat().st_size == 0:
            raise RuntimeError("ElevenLabs returned an empty audio file.")
        return self._build_real_voice_result(provider="elevenlabs", file_path=out, audio_format="mp3", **kwargs)

    def _generate_openai_voice(self, **kwargs) -> dict[str, Any]:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for production voice generation.")
        from openai import OpenAI
        narration=kwargs["narration"]
        client=OpenAI(api_key=settings.openai_api_key)
        response=client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=narration,
            response_format="mp3",
        )
        digest=hashlib.sha256(narration.encode()).hexdigest()
        out=Path(settings.voice_output_dir) / f"{digest}.mp3"
        out.parent.mkdir(parents=True, exist_ok=True)
        response.write_to_file(str(out))
        if out.stat().st_size == 0:
            raise RuntimeError("OpenAI returned an empty audio file.")
        return self._build_real_voice_result(provider="openai", file_path=out, audio_format="mp3", **kwargs)

    # ---------------------------------------------------------
    def _generate_local_voice(self, **kwargs) -> dict[str, Any]:
        """Generate local WAV audio using the Windows speech engine."""
        narration = kwargs["narration"]

        if not narration.strip():
            raise ValueError("Narration cannot be empty for local voice generation.")

        engine = pyttsx3.init()

        try:
            engine.setProperty("rate", 175)
            engine.setProperty("volume", 1.0)

            voices = engine.getProperty("voices")
            if voices:
                preferred = None

                for voice in voices:
                    voice_text = (
                        f"{getattr(voice, 'id', '')} "
                        f"{getattr(voice, 'name', '')}"
                    ).lower()

                    if "english" in voice_text or "zira" in voice_text:
                        preferred = voice
                        break

                if preferred is None:
                    preferred = voices[0]

                engine.setProperty("voice", preferred.id)

            digest = hashlib.sha256(narration.encode("utf-8")).hexdigest()
            out = Path(settings.voice_output_dir) / f"{digest}.wav"
            out.parent.mkdir(parents=True, exist_ok=True)

            engine.save_to_file(narration, str(out))
            engine.runAndWait()

        finally:
            engine.stop()

        if not out.exists():
            raise RuntimeError("Local TTS did not create an audio file.")

        if out.stat().st_size == 0:
            raise RuntimeError("Local TTS created an empty audio file.")

        return self._build_real_voice_result(
            provider="local",
            file_path=out,
            audio_format="wav",
            **kwargs,
        )
    # Validation / Normalization
    # ---------------------------------------------------------

    def _normalize_result(
        self,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ensure the public Voice service contract remains stable.
        """

        if not isinstance(result, dict):
            raise ValueError(
                "Voice service returned an invalid result."
            )

        if not result.get("stage"):
            result["stage"] = "voice"

        if not result.get("status"):
            result["status"] = "completed"

        if not result.get("provider"):
            result["provider"] = self.provider

        if not result.get("voice_status"):
            result["voice_status"] = "planned"

        return result

    # ---------------------------------------------------------
    # Timing Helpers
    # ---------------------------------------------------------

    def _word_count(
        self,
        text: str,
    ) -> int:
        if not text:
            return 0

        return len(
            re.findall(
                r"\b[\w'-]+\b",
                text,
                flags=re.UNICODE,
            )
        )

    def _estimate_duration(
        self,
        *,
        word_count: int,
        pacing: str,
    ) -> float:
        """
        Estimate narration duration.

        The value is intentionally only an estimate until a real
        TTS provider returns actual audio duration.
        """

        if word_count <= 0:
            return 0.0

        pacing_lower = str(
            pacing or ""
        ).lower()

        if "slow" in pacing_lower:
            words_per_minute = 125
        elif "fast" in pacing_lower:
            words_per_minute = 175
        elif "dynamic" in pacing_lower:
            words_per_minute = 155
        else:
            words_per_minute = 145

        return (
            word_count / words_per_minute
        ) * 60.0

    def _format_seconds(
        self,
        seconds: float,
    ) -> str:
        """
        Format seconds as MM:SS.ss.
        """

        total_seconds = max(
            0.0,
            float(seconds),
        )

        minutes = int(
            total_seconds // 60
        )

        remaining = total_seconds - (
            minutes * 60
        )

        return (
            f"{minutes:02d}:"
            f"{remaining:05.2f}"
        )


voice_service = VoiceService()








