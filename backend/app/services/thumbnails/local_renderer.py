from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


class LocalThumbnailRenderer:
    def __init__(self) -> None:
        self.name = "local"

    def render(
        self,
        *,
        title: str,
        concept: str,
        width: int,
        height: int,
        output_path: str,
        background_path: Optional[str] = None,
        foreground_path: Optional[str] = None,
    ) -> str:
        output = Path(output_path)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image = self._create_background(
            width=width,
            height=height,
            background_path=background_path,
        )

        draw = ImageDraw.Draw(image)

        font = self._get_font(
            size=max(
                42,
                int(min(width, height) * 0.085),
            )
        )

        small_font = self._get_font(
            size=max(
                24,
                int(min(width, height) * 0.035),
            )
        )

        # Visual focal area.
        focal_x = int(width * 0.72)
        focal_y = int(height * 0.50)

        if foreground_path:
            self._paste_foreground(
                image=image,
                foreground_path=foreground_path,
                center_x=focal_x,
                center_y=focal_y,
                max_width=int(width * 0.45),
                max_height=int(height * 0.80),
            )
        else:
            self._draw_focal_placeholder(
                draw=draw,
                center_x=focal_x,
                center_y=focal_y,
                width=int(width * 0.28),
                height=int(height * 0.58),
            )

        text = self._shorten_title(title)

        text_x = int(width * 0.06)
        text_y = int(height * 0.15)
        max_text_width = int(width * 0.52)

        lines = self._wrap_text(
            draw=draw,
            text=text,
            font=font,
            max_width=max_text_width,
        )

        line_height = int(font.size * 1.05)

        # Text shadow / outline.
        for index, line in enumerate(lines[:4]):
            y = text_y + index * line_height

            draw.text(
                (text_x + 5, y + 5),
                line,
                font=font,
                fill="black",
            )

            draw.text(
                (text_x, y),
                line,
                font=font,
                fill="white",
                stroke_width=3,
                stroke_fill="black",
            )

        concept_text = concept.strip()

        if concept_text:
            concept_text = concept_text[:90]

            draw.text(
                (
                    int(width * 0.06),
                    int(height * 0.88),
                ),
                concept_text,
                font=small_font,
                fill="white",
                stroke_width=2,
                stroke_fill="black",
            )

        image.save(
            output,
            format="PNG",
            optimize=True,
        )

        return str(output)

    def _create_background(
        self,
        *,
        width: int,
        height: int,
        background_path: Optional[str],
    ) -> Image.Image:
        if background_path:
            path = Path(background_path)

            if path.exists():
                image = Image.open(path).convert("RGB")

                return self._cover_resize(
                    image,
                    width,
                    height,
                )

        # Neutral fallback background.
        image = Image.new(
            "RGB",
            (width, height),
            (30, 30, 35),
        )

        draw = ImageDraw.Draw(image)

        # Subtle geometric background.
        step = max(40, min(width, height) // 8)

        for x in range(0, width, step):
            draw.line(
                (x, 0, x, height),
                fill=(55, 55, 65),
                width=2,
            )

        for y in range(0, height, step):
            draw.line(
                (0, y, width, y),
                fill=(55, 55, 65),
                width=2,
            )

        return image

    def _cover_resize(
        self,
        image: Image.Image,
        width: int,
        height: int,
    ) -> Image.Image:
        source_ratio = image.width / image.height
        target_ratio = width / height

        if source_ratio > target_ratio:
            new_height = height
            new_width = int(height * source_ratio)
        else:
            new_width = width
            new_height = int(width / source_ratio)

        image = image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS,
        )

        left = max(0, (new_width - width) // 2)
        top = max(0, (new_height - height) // 2)

        return image.crop(
            (
                left,
                top,
                left + width,
                top + height,
            )
        )

    def _paste_foreground(
        self,
        *,
        image: Image.Image,
        foreground_path: str,
        center_x: int,
        center_y: int,
        max_width: int,
        max_height: int,
    ) -> None:
        path = Path(foreground_path)

        if not path.exists():
            return

        foreground = Image.open(path).convert("RGBA")

        ratio = min(
            max_width / foreground.width,
            max_height / foreground.height,
        )

        new_size = (
            max(1, int(foreground.width * ratio)),
            max(1, int(foreground.height * ratio)),
        )

        foreground = foreground.resize(
            new_size,
            Image.Resampling.LANCZOS,
        )

        x = center_x - foreground.width // 2
        y = center_y - foreground.height // 2

        image.paste(
            foreground,
            (x, y),
            foreground,
        )

    def _draw_focal_placeholder(
        self,
        *,
        draw: ImageDraw.ImageDraw,
        center_x: int,
        center_y: int,
        width: int,
        height: int,
    ) -> None:
        left = center_x - width // 2
        top = center_y - height // 2
        right = center_x + width // 2
        bottom = center_y + height // 2

        draw.ellipse(
            (
                left + width // 4,
                top,
                right - width // 4,
                top + height // 3,
            ),
            fill=(220, 220, 225),
            outline=(10, 10, 10),
            width=4,
        )

        draw.rounded_rectangle(
            (
                left,
                top + height // 4,
                right,
                bottom,
            ),
            radius=max(10, width // 12),
            fill=(190, 190, 200),
            outline=(10, 10, 10),
            width=4,
        )

    def _get_font(self, size: int):
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
        ]

        for candidate in candidates:
            path = Path(candidate)

            if path.exists():
                return ImageFont.truetype(
                    str(path),
                    size=size,
                )

        return ImageFont.load_default()

    def _shorten_title(
        self,
        title: str,
        max_chars: int = 55,
    ) -> str:
        title = " ".join(title.split())

        if len(title) <= max_chars:
            return title

        return title[: max_chars - 3].rstrip() + "..."

    def _wrap_text(
        self,
        *,
        draw: ImageDraw.ImageDraw,
        text: str,
        font,
        max_width: int,
    ) -> list[str]:
        words = text.split()

        lines: list[str] = []
        current = ""

        for word in words:
            candidate = (
                word
                if not current
                else f"{current} {word}"
            )

            bbox = draw.textbbox(
                (0, 0),
                candidate,
                font=font,
            )

            if bbox[2] - bbox[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)

                current = word

        if current:
            lines.append(current)

        return lines