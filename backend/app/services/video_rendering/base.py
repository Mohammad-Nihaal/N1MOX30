from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RenderResult:
    """
    Provider-neutral result returned by a video renderer.
    """

    success: bool

    output_path: str | None = None

    duration_seconds: float = 0.0

    width: int = 0

    height: int = 0

    fps: float = 0.0

    file_size_bytes: int = 0

    mime_type: str = "video/mp4"

    error_message: str | None = None

    provider: str = "unknown"

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


class BaseVideoRenderer(ABC):
    """
    Provider-neutral video rendering interface.

    Future render providers can implement this interface
    without changing the higher-level N1MOX30 workflow.
    """

    provider_name: str = "base"

    @abstractmethod
    def render(
        self,
        timeline: dict[str, Any],
        output_path: str | Path,
    ) -> RenderResult:
        """
        Render a timeline into a video file.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_environment(self) -> dict[str, Any]:
        """
        Check whether the renderer is available.
        """
        raise NotImplementedError