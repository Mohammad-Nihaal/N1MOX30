from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.automation.workflow_types import WorkflowStage


@dataclass(frozen=True)
class StageDefinition:
    """Definition of one executable N1MOX workflow stage."""

    stage: WorkflowStage
    name: str
    description: str
    handler: Callable[..., dict[str, Any]] | None = None


class StageRegistry:
    """
    Central registry for N1MOX workflow stages.

    The registry deliberately separates stage identity from
    stage implementation. This allows individual AI providers,
    media providers, research systems, and publishing adapters
    to be introduced later without changing the workflow engine.
    """

    def __init__(self) -> None:
        self._stages: dict[WorkflowStage, StageDefinition] = {}

    def register(
        self,
        stage: WorkflowStage,
        name: str,
        description: str,
        handler: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        """Register or replace a workflow stage."""

        self._stages[stage] = StageDefinition(
            stage=stage,
            name=name,
            description=description,
            handler=handler,
        )

    def get(
        self,
        stage: WorkflowStage,
    ) -> StageDefinition:
        """Return a registered stage definition."""

        if stage not in self._stages:
            raise KeyError(
                f"Workflow stage '{stage.value}' is not registered."
            )

        return self._stages[stage]

    def has(self, stage: WorkflowStage) -> bool:
        """Return whether a stage is registered."""

        return stage in self._stages

    def all(self) -> list[StageDefinition]:
        """Return all registered stages in workflow order."""

        return list(self._stages.values())


stage_registry = StageRegistry()


def register_default_stages() -> None:
    """Register the default N1MOX30 workflow stages."""

    stage_registry.register(
        WorkflowStage.RESEARCH,
        "Research",
        "Research the topic, audience, trends, references, and relevant signals.",
    )

    stage_registry.register(
        WorkflowStage.STRATEGY,
        "Strategy",
        "Determine the content angle, audience promise, format, and strategic direction.",
    )

    stage_registry.register(
        WorkflowStage.HOOKS,
        "Hooks",
        "Generate, score, and select high-retention opening hooks.",
    )

    stage_registry.register(
        WorkflowStage.SCRIPT,
        "Script",
        "Create and optimize the content script for the selected platform and format.",
    )

    stage_registry.register(
        WorkflowStage.VOICE,
        "Voice",
        "Generate or prepare professional narration from the approved script.",
    )

    stage_registry.register(
        WorkflowStage.VISUALS,
        "Visuals",
        "Plan and source or generate visuals, B-roll, overlays, and supporting assets.",
    )

    stage_registry.register(
        WorkflowStage.VIDEO,
        "Video",
        "Assemble the final video from narration, visuals, timing, transitions, and audio.",
    )

    stage_registry.register(
        WorkflowStage.CAPTIONS,
        "Captions",
        "Generate synchronized captions and platform-ready subtitle assets.",
    )

    stage_registry.register(
        WorkflowStage.THUMBNAIL,
        "Thumbnail",
        "Generate and evaluate thumbnail concepts optimized for click-through potential.",
    )

    stage_registry.register(
        WorkflowStage.METADATA,
        "Metadata",
        "Generate titles, descriptions, keywords, hashtags, chapters, and related metadata.",
    )

    stage_registry.register(
        WorkflowStage.QUALITY_CHECK,
        "Quality Check",
        "Validate content, media, metadata, assets, and workflow requirements before delivery.",
    )

    stage_registry.register(
        WorkflowStage.SCHEDULING,
        "Scheduling",
        "Determine or apply the publishing schedule and connected account.",
    )

    stage_registry.register(
        WorkflowStage.PUBLISHING,
        "Publishing",
        "Publish the completed content through the appropriate platform adapter.",
    )


register_default_stages()