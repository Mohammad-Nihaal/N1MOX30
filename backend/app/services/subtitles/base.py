from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SubtitleSegment:
    """
    Provider-neutral subtitle segment.
    """

    id: str

    start_time: float

    end_time: float

    text: str

    confidence: float | None = None

    words: list[dict[str, Any]] = field(
        default_factory=list,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


class BaseSubtitleProvider(ABC):
    """
    Provider-neutral subtitle generation interface.
    """

    provider_name: str = "base"

    @abstractmethod
    def generate(
        self,
        text: str,
        duration_seconds: float,
    ) -> list[SubtitleSegment]:
        """
        Generate timed subtitle segments.
        """
        raise NotImplementedError