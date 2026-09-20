from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any


class LocalVisualAssetGenerator:
    """
    Generates real local PNG visual assets using FFmpeg.
    """

    def __init__(self, output_dir: str | Path = "storage/visuals"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_asset(
        self,
        *,
        scene_id: str,
        topic: str,
        prompt: str,
        width: int = 1920,
        height: int = 1080,
    ) -> dict[str, Any]:

        seed = hashlib.sha256(
            f"{scene_id}|{topic}|{prompt}".encode("utf-8")
        ).hexdigest()

        scene_dir = self.output_dir / seed
        scene_dir.mkdir(parents=True, exist_ok=True)

        image_path = scene_dir / f"{scene_id}.png"

        r = int(seed[0:2], 16)
        g = int(seed[2:4], 16)
        b = int(seed[4:6], 16)

        color = f"0x{r:02x}{g:02x}{b:02x}"

        command = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c={color}:s={width}x{height}:d=1",
            "-frames:v",
            "1",
            "-f",
            "image2",
            str(image_path),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "FFmpeg visual generation failed:\n"
                + result.stderr[-4000:]
            )

        if not image_path.exists():
            raise RuntimeError(
                "FFmpeg completed but did not create the visual asset."
            )

        if image_path.stat().st_size == 0:
            raise RuntimeError(
                "FFmpeg created an empty visual asset."
            )

        resolved = str(image_path.resolve())

        return {
            "scene_id": scene_id,
            "asset_type": "generated_image",
            "provider": "local_ffmpeg",
            "provider_status": "generated",
            "file_path": resolved,
            "asset_path": resolved,
            "file_url": None,
            "mime_type": "image/png",
            "ready_for_video": True,
            "width": width,
            "height": height,
        }
