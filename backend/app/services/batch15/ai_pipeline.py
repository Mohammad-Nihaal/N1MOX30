from dataclasses import dataclass

from app.services.batch12.ai_gateway import authorize_ai_call, audit_ai_generation, record_provider_usage
from app.services.batch14.provider_runtime import execute_runtime_with_fallback


@dataclass
class PipelineResult:
    success: bool
    provider: str
    content: str = ""
    units: int = 0
    fallback_used: bool = False
    generation_id: str | None = None
    usage_recorded: bool = False
    error: str | None = None


def run_ai_pipeline(
    db,
    user_id,
    prompt,
    requested_provider=None,
    estimated_units=1,
    content_type="text",
):
    # 1. Gateway authorization + quota
    authorization = authorize_ai_call(
        db,
        user_id,
        requested_provider=requested_provider,
        estimated_units=estimated_units,
    )

    if not authorization.allowed:
        return PipelineResult(
            success=False,
            provider=authorization.provider or "none",
            units=estimated_units,
            error=authorization.reason,
        )

    # 2. Real provider runtime + fallback
    runtime = execute_runtime_with_fallback(
        db=db,
        user_id=user_id,
        prompt=prompt,
        requested=authorization.provider,
    )

    if not runtime.success:
        return PipelineResult(
            success=False,
            provider=runtime.provider,
            units=estimated_units,
            fallback_used=runtime.fallback_used,
            error=runtime.error,
        )

    # 3. Generation audit
    audit = audit_ai_generation(
        db=db,
        user_id=user_id,
        provider=runtime.provider,
        units=estimated_units,
        content_type=content_type,
        status="completed",
    )

    # 4. Provider usage ledger
    usage = record_provider_usage(
        db=db,
        user_id=user_id,
        provider=runtime.provider,
        units=estimated_units,
        operation="generation",
    )

    return PipelineResult(
        success=True,
        provider=runtime.provider,
        content=runtime.content,
        units=estimated_units,
        fallback_used=runtime.fallback_used,
        generation_id=audit.get("generation_id"),
        usage_recorded=bool(usage.get("recorded")),
    )

