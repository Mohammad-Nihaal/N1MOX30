import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.video_timeline import VideoTimeline
from app.schemas.video_timeline import (
    TimelineClip,
    TimelineClipCreate,
    TimelineTrack,
    TimelineTrackCreate,
    VideoTimelineCreate,
    VideoTimelineDocument,
    VideoTimelineUpdate,
)


ASPECT_RATIOS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
}


class VideoTimelineService:
    """
    Core timeline orchestration service.

    The service deliberately keeps timeline data provider-neutral.
    Rendering providers consume the resulting timeline later.
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Timeline creation
    # ------------------------------------------------------------------

    def create_timeline(
        self,
        user_id: str,
        payload: VideoTimelineCreate,
    ) -> VideoTimeline:

        width, height = ASPECT_RATIOS[payload.aspect_ratio]

        document = VideoTimelineDocument(
            version=1,
            aspect_ratio=payload.aspect_ratio,
            width=width,
            height=height,
            fps=payload.fps,
            duration_seconds=0.0,
            background_color=payload.background_color,
            tracks=[],
            metadata=payload.metadata,
        )

        timeline = VideoTimeline(
            user_id=user_id,
            content_id=payload.content_id,
            name=payload.name,
            aspect_ratio=payload.aspect_ratio,
            width=width,
            height=height,
            duration_seconds=0.0,
            fps=payload.fps,
            background_color=payload.background_color,
            status="draft",
            version=1,
            is_locked=False,
            timeline_json=document.model_dump_json(),
        )

        self.db.add(timeline)
        self.db.commit()
        self.db.refresh(timeline)

        return timeline

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def get_document(
        self,
        timeline: VideoTimeline,
    ) -> VideoTimelineDocument:

        try:
            data = json.loads(timeline.timeline_json or "{}")
        except json.JSONDecodeError:
            data = {}

        if not data:
            data = {
                "version": timeline.version,
                "aspect_ratio": timeline.aspect_ratio,
                "width": timeline.width,
                "height": timeline.height,
                "fps": timeline.fps,
                "duration_seconds": timeline.duration_seconds,
                "background_color": timeline.background_color,
                "tracks": [],
                "metadata": {},
            }

        return VideoTimelineDocument.model_validate(data)

    def save_document(
        self,
        timeline: VideoTimeline,
        document: VideoTimelineDocument,
    ) -> VideoTimeline:

        duration = self.calculate_duration(document)

        document.duration_seconds = duration
        document.version = timeline.version

        timeline.timeline_json = document.model_dump_json()
        timeline.duration_seconds = duration
        timeline.aspect_ratio = document.aspect_ratio
        timeline.width = document.width
        timeline.height = document.height
        timeline.fps = document.fps
        timeline.background_color = document.background_color

        self.db.add(timeline)
        self.db.commit()
        self.db.refresh(timeline)

        return timeline

    # ------------------------------------------------------------------
    # Timeline update
    # ------------------------------------------------------------------

    def update_timeline(
        self,
        timeline: VideoTimeline,
        payload: VideoTimelineUpdate,
    ) -> VideoTimeline:

        if timeline.is_locked:
            raise ValueError("Timeline is locked and cannot be modified")

        document = self.get_document(timeline)

        if payload.name is not None:
            timeline.name = payload.name

        if payload.aspect_ratio is not None:
            width, height = ASPECT_RATIOS[payload.aspect_ratio]

            timeline.aspect_ratio = payload.aspect_ratio
            timeline.width = width
            timeline.height = height

            document.aspect_ratio = payload.aspect_ratio
            document.width = width
            document.height = height

        if payload.fps is not None:
            timeline.fps = payload.fps
            document.fps = payload.fps

        if payload.background_color is not None:
            timeline.background_color = payload.background_color
            document.background_color = payload.background_color

        if payload.status is not None:
            timeline.status = payload.status

        if payload.metadata is not None:
            document.metadata.update(payload.metadata)

        if payload.timeline is not None:
            document = payload.timeline

        timeline.version += 1
        document.version = timeline.version

        self.save_document(timeline, document)

        return timeline

    # ------------------------------------------------------------------
    # Tracks
    # ------------------------------------------------------------------

    def add_track(
        self,
        timeline: VideoTimeline,
        payload: TimelineTrackCreate,
    ) -> VideoTimeline:

        self.ensure_editable(timeline)

        document = self.get_document(timeline)

        track = TimelineTrack(
            id=str(uuid4()),
            name=payload.name,
            track_type=payload.track_type,
            order=payload.order,
            muted=payload.muted,
            locked=payload.locked,
            visible=payload.visible,
            clips=[],
        )

        document.tracks.append(track)

        timeline.version += 1
        document.version = timeline.version

        return self.save_document(timeline, document)

    def remove_track(
        self,
        timeline: VideoTimeline,
        track_id: str,
    ) -> VideoTimeline:

        self.ensure_editable(timeline)

        document = self.get_document(timeline)

        original_count = len(document.tracks)

        document.tracks = [
            track
            for track in document.tracks
            if track.id != track_id
        ]

        if len(document.tracks) == original_count:
            raise ValueError("Timeline track not found")

        timeline.version += 1
        document.version = timeline.version

        return self.save_document(timeline, document)

    # ------------------------------------------------------------------
    # Clips
    # ------------------------------------------------------------------

    def add_clip(
        self,
        timeline: VideoTimeline,
        payload: TimelineClipCreate,
    ) -> VideoTimeline:

        self.ensure_editable(timeline)

        document = self.get_document(timeline)

        track = next(
            (
                item
                for item in document.tracks
                if item.id == payload.track_id
            ),
            None,
        )

        if track is None:
            raise ValueError("Timeline track not found")

        if track.locked:
            raise ValueError("Timeline track is locked")

        if payload.end_time < payload.start_time:
            raise ValueError(
                "Clip end_time must be greater than or equal to start_time"
            )

        clip = TimelineClip(
            id=str(uuid4()),
            **payload.model_dump(),
        )

        track.clips.append(clip)

        self.sort_track_clips(track)

        timeline.version += 1
        document.version = timeline.version

        return self.save_document(timeline, document)

    def remove_clip(
        self,
        timeline: VideoTimeline,
        clip_id: str,
    ) -> VideoTimeline:

        self.ensure_editable(timeline)

        document = self.get_document(timeline)

        found = False

        for track in document.tracks:
            original_count = len(track.clips)

            track.clips = [
                clip
                for clip in track.clips
                if clip.id != clip_id
            ]

            if len(track.clips) != original_count:
                found = True

        if not found:
            raise ValueError("Timeline clip not found")

        timeline.version += 1
        document.version = timeline.version

        return self.save_document(timeline, document)

    # ------------------------------------------------------------------
    # Duration
    # ------------------------------------------------------------------

    def calculate_duration(
        self,
        document: VideoTimelineDocument,
    ) -> float:

        maximum = 0.0

        for track in document.tracks:
            for clip in track.clips:
                if clip.end_time > maximum:
                    maximum = clip.end_time

        return round(maximum, 3)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_timeline(
        self,
        timeline: VideoTimeline,
    ) -> dict:

        document = self.get_document(timeline)

        errors: list[str] = []
        warnings: list[str] = []

        track_ids = set()

        for track in document.tracks:

            if track.id in track_ids:
                errors.append(
                    f"Duplicate track id: {track.id}"
                )

            track_ids.add(track.id)

            clip_ids = set()

            for clip in track.clips:

                if clip.id in clip_ids:
                    errors.append(
                        f"Duplicate clip id: {clip.id}"
                    )

                clip_ids.add(clip.id)

                if clip.start_time < 0:
                    errors.append(
                        f"Clip {clip.id} has a negative start time"
                    )

                if clip.end_time < clip.start_time:
                    errors.append(
                        f"Clip {clip.id} ends before it starts"
                    )

                if clip.playback_rate <= 0:
                    errors.append(
                        f"Clip {clip.id} has invalid playback rate"
                    )

                if track.track_type == "voice" and clip.volume > 1.5:
                    warnings.append(
                        f"Voice clip {clip.id} has unusually high volume"
                    )

        calculated_duration = self.calculate_duration(document)

        if abs(
            calculated_duration - document.duration_seconds
        ) > 0.01:
            warnings.append(
                "Stored timeline duration differs from calculated duration"
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "duration_seconds": calculated_duration,
            "track_count": len(document.tracks),
            "clip_count": sum(
                len(track.clips)
                for track in document.tracks
            ),
        }

    # ------------------------------------------------------------------
    # Locking
    # ------------------------------------------------------------------

    def lock_timeline(
        self,
        timeline: VideoTimeline,
    ) -> VideoTimeline:

        timeline.is_locked = True
        timeline.status = "locked"

        self.db.add(timeline)
        self.db.commit()
        self.db.refresh(timeline)

        return timeline

    def unlock_timeline(
        self,
        timeline: VideoTimeline,
    ) -> VideoTimeline:

        timeline.is_locked = False
        timeline.status = "draft"

        self.db.add(timeline)
        self.db.commit()
        self.db.refresh(timeline)

        return timeline

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def sort_track_clips(
        track: TimelineTrack,
    ) -> None:

        track.clips.sort(
            key=lambda clip: (
                clip.start_time,
                clip.layer,
                clip.id,
            )
        )

    @staticmethod
    def ensure_editable(
        timeline: VideoTimeline,
    ) -> None:

        if timeline.is_locked:
            raise ValueError(
                "Timeline is locked and cannot be modified"
            )