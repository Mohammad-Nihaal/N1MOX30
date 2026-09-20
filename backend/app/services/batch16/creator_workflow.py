from dataclasses import dataclass
from typing import Any

from app.services.batch15.ai_pipeline import run_ai_pipeline


@dataclass
class CreatorWorkflowResult:
    success: bool
    stage: str
    provider: str
    content: str = ""
    generation_id: str | None = None
    usage_recorded: bool = False
    fallback_used: bool = False
    error: str | None = None


CREATOR_STAGES = (
    "research",
    "hooks",
    "script",
    "voice",
    "visuals",
    "video",
    "captions",
    "thumbnail",
    "metadata",
    "qc",
    "scheduling",
)


def run_creator_stage(
    db,
    user_id,
    stage: str,
    prompt: str,
    provider: str | None = None,
    estimated_units: int = 1,
):
    stage = stage.lower().strip()

    if stage not in CREATOR_STAGES:
        return CreatorWorkflowResult(
            False,
            stage,
            "none",
            error=f"Unsupported creator stage: {stage}",
        )

    result = run_ai_pipeline(
        db=db,
        user_id=user_id,
        prompt=prompt,
        requested_provider=provider,
        estimated_units=estimated_units,
        content_type=stage,
    )

    return CreatorWorkflowResult(
        success=result.success,
        stage=stage,
        provider=result.provider,
        content=result.content,
        generation_id=result.generation_id,
        usage_recorded=result.usage_recorded,
        fallback_used=result.fallback_used,
        error=result.error,
    )


def run_creator_workflow(
    db,
    user_id,
    topic: str,
    stages: list[str] | None = None,
    provider: str | None = None,
):
    selected = stages or ["research", "hooks", "script"]

    results: list[dict[str, Any]] = []

    for stage in selected:
        prompt = (
            f"N1MOX30 creator workflow stage: {stage}\n"
            f"Topic: {topic}\n"
            f"Create production-ready output for this stage."
        )

        result = run_creator_stage(
            db=db,
            user_id=user_id,
            stage=stage,
            prompt=prompt,
            provider=provider,
            estimated_units=1,
        )

        results.append({
            "stage": result.stage,
            "success": result.success,
            "provider": result.provider,
            "content": result.content,
            "generation_id": result.generation_id,
            "usage_recorded": result.usage_recorded,
            "fallback_used": result.fallback_used,
            "error": result.error,
        })

        if not result.success:
            return {
                "success": False,
                "topic": topic,
                "completed_stages": results,
                "failed_stage": stage,
                "error": result.error,
            }

    return {
        "success": True,
        "topic": topic,
        "completed_stages": results,
        "failed_stage": None,
        "error": None,
    }

