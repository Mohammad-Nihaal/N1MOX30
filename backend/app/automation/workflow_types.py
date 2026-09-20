from enum import Enum


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class WorkflowStage(str, Enum):
    RESEARCH = "research"
    STRATEGY = "strategy"
    HOOKS = "hooks"
    SCRIPT = "script"
    VOICE = "voice"
    VISUALS = "visuals"
    VIDEO = "video"
    CAPTIONS = "captions"
    THUMBNAIL = "thumbnail"
    METADATA = "metadata"
    QUALITY_CHECK = "quality_check"
    SCHEDULING = "scheduling"
    PUBLISHING = "publishing"


WORKFLOW_STAGES: tuple[WorkflowStage, ...] = (
    WorkflowStage.RESEARCH,
    WorkflowStage.STRATEGY,
    WorkflowStage.HOOKS,
    WorkflowStage.SCRIPT,
    WorkflowStage.VOICE,
    WorkflowStage.VISUALS,
    WorkflowStage.VIDEO,
    WorkflowStage.CAPTIONS,
    WorkflowStage.THUMBNAIL,
    WorkflowStage.METADATA,
    WorkflowStage.QUALITY_CHECK,
    WorkflowStage.SCHEDULING,
    WorkflowStage.PUBLISHING,
)


STAGE_LABELS: dict[WorkflowStage, str] = {
    WorkflowStage.RESEARCH: "Research",
    WorkflowStage.STRATEGY: "Strategy",
    WorkflowStage.HOOKS: "Hooks",
    WorkflowStage.SCRIPT: "Script",
    WorkflowStage.VOICE: "Voice",
    WorkflowStage.VISUALS: "Visuals",
    WorkflowStage.VIDEO: "Video",
    WorkflowStage.CAPTIONS: "Captions",
    WorkflowStage.THUMBNAIL: "Thumbnail",
    WorkflowStage.METADATA: "Metadata",
    WorkflowStage.QUALITY_CHECK: "Quality Check",
    WorkflowStage.SCHEDULING: "Scheduling",
    WorkflowStage.PUBLISHING: "Publishing",
}


def get_stage_order(stage: WorkflowStage) -> int:
    """Return the zero-based position of a workflow stage."""

    return WORKFLOW_STAGES.index(stage) + 1


def get_stage_count() -> int:
    """Return the total number of workflow stages."""

    return len(WORKFLOW_STAGES)