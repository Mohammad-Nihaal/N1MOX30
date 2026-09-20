from pathlib import Path
from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.thumbnail import Thumbnail
from app.services.thumbnails.local_renderer import (
    LocalThumbnailRenderer,
)


PLATFORM_DIMENSIONS = {
    "youtube": (1280, 720),
    "youtube_shorts": (1080, 1920),
    "instagram": (1080, 1350),
    "instagram_reels": (1080, 1920),
    "square": (1080, 1080),
}


class ThumbnailService:
    def __init__(self) -> None:
        self.renderer = LocalThumbnailRenderer()
    def generate_thumbnail(
        self,
        db: Session | None = None,
        *,
        user_id: str = "",
        title: str = "",
        topic: Optional[str] = None,
        content_id: Optional[str] = None,
        platform: str = "youtube",
        concept_count: int = 4,
        style: str = "high_ctr",
        visual_subject: Optional[str] = None,
        additional_context: Optional[str] = None,
        command: str = "",
        research: Optional[dict] = None,
        strategy: Optional[dict] = None,
        hooks: Optional[dict] = None,
        script: Optional[dict] = None,
        voice: Optional[dict] = None,
        visuals: Optional[dict] = None,
        video: Optional[dict] = None,
        captions: Optional[dict] = None,
    ) -> dict:
        """
        Workflow-compatible thumbnail generation.

        Generates multiple thumbnail concepts, selects the highest-scoring
        concept, renders it locally, verifies the rendered asset, and
        returns a fully serializable workflow result.
        
        if db is None:
            raise ValueError(
                "Thumbnail generation requires a database session."
            )

        if not user_id:
            raise ValueError(
                "Thumbnail generation requires a user_id."
            )

        if not title:
            title = topic or command or "N1MOX30 Creator Video"

        if additional_context is None:
            context_parts = [
                command,
                str(research or ""),
                str(strategy or ""),
                str(hooks or ""),
                str(script or ""),
                str(voice or ""),
                str(visuals or ""),
                str(video or ""),
                str(captions or ""),
            ]
            additional_context = " ".join(
                part.strip()
                for part in context_parts
                if part and part.strip()
            )

        """

        thumbnails, selected_id = self.generate_concepts(
            db,
            user_id=user_id,
            title=title,
            topic=topic,
            content_id=content_id,
            platform=platform,
            concept_count=concept_count,
            style=style,
            visual_subject=visual_subject,
            additional_context=additional_context,
        )

        if not thumbnails:
            raise RuntimeError(
                "Thumbnail generation produced no concepts."
            )

        if not selected_id:
            raise RuntimeError(
                "Thumbnail generation could not select a concept."
            )

        selected = self.render(
            db,
            thumbnail_id=selected_id,
            user_id=user_id,
        )

        if not selected.image_path:
            raise RuntimeError(
                "Thumbnail renderer returned no image path."
            )

        rendered_path = Path(str(selected.image_path))

        if not rendered_path.exists():
            raise RuntimeError(
                f"Thumbnail renderer reported success but the image "
                f"does not exist: {rendered_path}"
            )

        if rendered_path.stat().st_size <= 0:
            raise RuntimeError(
                f"Thumbnail renderer created an empty image: "
                f"{rendered_path}"
            )

        return {
            "stage": "thumbnail",
            "status": "completed",
            "execution": "thumbnail_service",
            "provider": "local",
            "thumbnail_status": "rendered",

            "thumbnail": {
                "id": selected.id,
                "name": selected.name,
                "title_text": selected.title_text,
                "concept": selected.concept,
                "image_path": str(rendered_path.resolve()),
                "width": selected.width,
                "height": selected.height,
                "platform": selected.platform,
                "status": selected.status,
                "is_selected": selected.is_selected,
                "overall_score": selected.overall_score,
                "ctr_score": selected.ctr_score,
                "readability_score": selected.readability_score,
                "curiosity_score": selected.curiosity_score,
                "visual_score": selected.visual_score,
            },

            "concept_count": len(thumbnails),
            "selected_thumbnail_id": selected.id,

            "asset": {
                "asset_type": "thumbnail",
                "format": "png",
                "file_path": str(rendered_path.resolve()),
                "file_size_bytes": rendered_path.stat().st_size,
                "width": selected.width,
                "height": selected.height,
                "ready": True,
            },

            "ready_for_upload": True,

            "production": {
                "rendered": True,
                "render_provider": "local",
                "concepts_generated": len(thumbnails),
                "selected": True,
                "asset_verified": True,
                "ready_for_metadata": True,
                "ready_for_publishing": True,
            },
        }
    def generate_concepts(
        self,
        db: Session,
        *,
        user_id: str,
        title: str,
        topic: Optional[str] = None,
        content_id: Optional[str] = None,
        platform: str = "youtube",
        concept_count: int = 4,
        style: str = "high_ctr",
        visual_subject: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> tuple[list[Thumbnail], Optional[str]]:
        width, height = PLATFORM_DIMENSIONS.get(
            platform.lower(),
            PLATFORM_DIMENSIONS["youtube"],
        )

        concepts = self._build_concepts(
            title=title,
            topic=topic,
            style=style,
            visual_subject=visual_subject,
            additional_context=additional_context,
            count=concept_count,
        )

        thumbnails: list[Thumbnail] = []

        for index, concept in enumerate(concepts):
            thumbnail = Thumbnail(
                id=str(uuid4()),
                user_id=user_id,
                content_id=content_id,
                name=f"Thumbnail Concept {index + 1}",
                platform=platform,
                width=width,
                height=height,
                title_text=concept["title_text"],
                concept=concept["concept"],
                visual_direction=concept["visual_direction"],
                background_prompt=concept["background_prompt"],
                foreground_prompt=concept["foreground_prompt"],
                text_style=concept["text_style"],
                composition=concept["composition"],
                curiosity_score=concept["curiosity_score"],
                readability_score=concept["readability_score"],
                visual_score=concept["visual_score"],
                ctr_score=concept["ctr_score"],
                overall_score=concept["overall_score"],
                provider="local",
                status="planned",
                is_selected=False,
            )

            db.add(thumbnail)
            thumbnails.append(thumbnail)

        db.commit()

        for thumbnail in thumbnails:
            db.refresh(thumbnail)

        best = max(
            thumbnails,
            key=lambda item: item.overall_score,
            default=None,
        )

        return thumbnails, (
            best.id
            if best
            else None
        )

    def render(
        self,
        db: Session,
        *,
        thumbnail_id: str,
        user_id: str,
        background_path: Optional[str] = None,
        foreground_path: Optional[str] = None,
    ) -> Thumbnail:
        thumbnail = (
            db.query(Thumbnail)
            .filter(
                Thumbnail.id == thumbnail_id,
                Thumbnail.user_id == user_id,
            )
            .first()
        )

        if thumbnail is None:
            raise ValueError("Thumbnail not found")

        output_directory = (
            Path("storage")
            / "thumbnails"
            / user_id
        )

        output_path = (
            output_directory
            / f"{thumbnail.id}.png"
        )

        rendered_path = self.renderer.render(
            title=thumbnail.title_text or "",
            concept=thumbnail.concept or "",
            width=thumbnail.width,
            height=thumbnail.height,
            output_path=str(output_path),
            background_path=background_path,
            foreground_path=foreground_path,
        )

        thumbnail.image_path = rendered_path
        thumbnail.status = "rendered"
        thumbnail.provider = "local"

        db.commit()
        db.refresh(thumbnail)

        return thumbnail

    def select(
        self,
        db: Session,
        *,
        thumbnail_id: str,
        user_id: str,
    ) -> Thumbnail:
        thumbnail = (
            db.query(Thumbnail)
            .filter(
                Thumbnail.id == thumbnail_id,
                Thumbnail.user_id == user_id,
            )
            .first()
        )

        if thumbnail is None:
            raise ValueError("Thumbnail not found")

        (
            db.query(Thumbnail)
            .filter(
                Thumbnail.user_id == user_id,
                Thumbnail.content_id == thumbnail.content_id,
            )
            .update(
                {
                    Thumbnail.is_selected: False,
                },
                synchronize_session=False,
            )
        )

        thumbnail.is_selected = True
        thumbnail.status = "selected"

        db.commit()
        db.refresh(thumbnail)

        return thumbnail

    def list_for_content(
        self,
        db: Session,
        *,
        user_id: str,
        content_id: str,
    ) -> list[Thumbnail]:
        return (
            db.query(Thumbnail)
            .filter(
                Thumbnail.user_id == user_id,
                Thumbnail.content_id == content_id,
            )
            .order_by(
                Thumbnail.overall_score.desc(),
                Thumbnail.created_at.desc(),
            )
            .all()
        )

    def _build_concepts(
        self,
        *,
        title: str,
        topic: Optional[str],
        style: str,
        visual_subject: Optional[str],
        additional_context: Optional[str],
        count: int,
    ) -> list[dict]:
        subject = (
            visual_subject
            or topic
            or title
        )

        context = (
            additional_context
            or ""
        ).strip()

        templates = [
            {
                "concept": "Curiosity gap",
                "visual_direction": (
                    "Show the main subject with one "
                    "unexpected visual element that "
                    "creates an unanswered question."
                ),
                "composition": "subject_right_text_left",
                "text_style": "bold_minimal",
            },
            {
                "concept": "Big transformation",
                "visual_direction": (
                    "Use a clear before-versus-after "
                    "visual structure with a strong "
                    "central transformation."
                ),
                "composition": "split_screen",
                "text_style": "bold_contrast",
            },
            {
                "concept": "Emotional reaction",
                "visual_direction": (
                    "Make the central subject visually "
                    "expressive while keeping the "
                    "headline extremely short."
                ),
                "composition": "face_right_text_left",
                "text_style": "large_emotional",
            },
            {
                "concept": "Contrarian",
                "visual_direction": (
                    "Present an unexpected interpretation "
                    "of the topic using a dominant focal "
                    "element and minimal text."
                ),
                "composition": "center_focus",
                "text_style": "high_contrast",
            },
            {
                "concept": "Information reveal",
                "visual_direction": (
                    "Use a partially revealed visual "
                    "element to create an information gap."
                ),
                "composition": "reveal",
                "text_style": "mystery",
            },
            {
                "concept": "Problem versus solution",
                "visual_direction": (
                    "Show the problem prominently and "
                    "visually hint at the solution."
                ),
                "composition": "problem_solution",
                "text_style": "bold_action",
            },
        ]

        concepts: list[dict] = []

        for index in range(count):
            template = templates[
                index % len(templates)
            ]

            title_text = self._thumbnail_text(
                title,
                template["concept"],
            )

            curiosity = self._curiosity_score(
                title_text,
                template["concept"],
            )

            readability = self._readability_score(
                title_text,
            )

            visual = self._visual_score(
                template["visual_direction"],
            )

            ctr = round(
                (
                    curiosity * 0.40
                    + readability * 0.20
                    + visual * 0.20
                    + 8.0 * 0.20
                ),
                2,
            )

            overall = round(
                (
                    curiosity * 0.35
                    + readability * 0.25
                    + visual * 0.20
                    + ctr * 0.20
                ),
                2,
            )

            concepts.append(
                {
                    "title_text": title_text,
                    "concept": template["concept"],
                    "visual_direction": (
                        f"{template['visual_direction']} "
                        f"Primary subject: {subject}."
                    ),
                    "background_prompt": (
                        f"Create a visually striking "
                        f"thumbnail background for {subject}. "
                        f"Style: {style}. "
                        f"Concept: {template['concept']}."
                    ),
                    "foreground_prompt": (
                        f"Create the main foreground subject "
                        f"representing {subject}. "
                        f"Composition: "
                        f"{template['composition']}."
                    ),
                    "text_style": template["text_style"],
                    "composition": template["composition"],
                    "curiosity_score": curiosity,
                    "readability_score": readability,
                    "visual_score": visual,
                    "ctr_score": ctr,
                    "overall_score": overall,
                }
            )

        return concepts

    def _thumbnail_text(
        self,
        title: str,
        concept: str,
    ) -> str:
        words = [
            word.strip(".,!?;:()[]{}")
            for word in title.split()
        ]

        words = [
            word
            for word in words
            if word
        ]

        if not words:
            return "WATCH THIS"

        if concept == "Curiosity gap":
            selected = words[:5]

        elif concept == "Big transformation":
            selected = words[:4]

        elif concept == "Emotional reaction":
            selected = words[:4]

        elif concept == "Contrarian":
            selected = words[:5]

        elif concept == "Information reveal":
            selected = words[:4]

        else:
            selected = words[:5]

        result = " ".join(selected)

        if len(result) > 32:
            result = result[:29].rstrip() + "..."

        return result.upper()

    def _curiosity_score(
        self,
        text: str,
        concept: str,
    ) -> float:
        score = 6.0

        curiosity_words = [
            "why",
            "secret",
            "truth",
            "really",
            "hidden",
            "mistake",
            "nobody",
            "never",
            "actually",
            "before",
            "after",
            "revealed",
        ]

        lowered = text.lower()

        for word in curiosity_words:
            if word in lowered:
                score += 0.8

        if concept in {
            "Curiosity gap",
            "Information reveal",
            "Contrarian",
        }:
            score += 1.0

        return round(
            min(score, 10.0),
            2,
        )

    def _readability_score(
        self,
        text: str,
    ) -> float:
        length = len(text)

        if length <= 18:
            score = 10.0
        elif length <= 25:
            score = 9.2
        elif length <= 32:
            score = 8.5
        elif length <= 40:
            score = 7.2
        else:
            score = 6.0

        return round(
            score,
            2,
        )

    def _visual_score(
        self,
        visual_direction: str,
    ) -> float:
        score = 8.0

        if "central" in visual_direction.lower():
            score += 0.5

        if "unexpected" in visual_direction.lower():
            score += 0.5

        return round(
            min(score, 10.0),
            2,
        )