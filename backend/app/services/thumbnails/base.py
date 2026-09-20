from dataclasses import dataclass
from typing import Optional


@dataclass
class ThumbnailProviderRequest:
    prompt: str
    width: int
    height: int
    output_path: str


@dataclass
class ThumbnailProviderResult:
    success: bool
    image_path: Optional[str]
    provider: str
    error: Optional[str] = None


class BaseThumbnailProvider:
    name = "base"

    def generate(
        self,
        request: ThumbnailProviderRequest,
    ) -> ThumbnailProviderResult:
        raise NotImplementedError