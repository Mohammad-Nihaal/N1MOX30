
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.batch12.ai_gateway import authorize_ai_call, gateway_status, audit_ai_generation, record_provider_usage
from app.services.batch13.provider_execution import execute_provider

router = APIRouter(prefix="/platform/v3", tags=["Platform AI Gateway"])


class GatewayRequest(BaseModel):
    provider: str | None = None
    estimated_units: int = 1


@router.get("/ai/status")
def ai_status():
    return gateway_status()


@router.post("/ai/authorize")
def ai_authorize(
    payload: GatewayRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.estimated_units < 1:
        raise HTTPException(status_code=400, detail="estimated_units must be >= 1")

    result = authorize_ai_call(
        db,
        user.id,
        payload.provider,
        payload.estimated_units,
    )

    if not result.allowed:
        raise HTTPException(status_code=402, detail=result.reason)

    return {
        "allowed": result.allowed,
        "provider": result.provider,
        "reason": result.reason,
        "estimated_units": result.estimated_units,
    }


# N1MOX30_BATCH12_GENERATION_GATE
class GenerationGateRequest(BaseModel):
    provider: str | None = None
    estimated_units: int = 1


@router.post("/ai/generation-gate")
def generation_gate(
    payload: GenerationGateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = authorize_ai_call(
        db=db,
        user_id=user.id,
        requested_provider=payload.provider,
        estimated_units=payload.estimated_units,
    )

    if not result.allowed:
        raise HTTPException(status_code=402, detail=result.reason)

    audit = audit_ai_generation(
        db=db,
        user_id=user.id,
        provider=result.provider,
        units=result.estimated_units,
    )

    return {
        "authorized": True,
        "provider": result.provider,
        "units": result.estimated_units,
        "audit": audit,
        "message": "AI generation authorized through N1MOX30 Gateway",
    }


class ProviderUsageRequest(BaseModel):
    provider: str
    units: int = 1
    operation: str = "generation"


@router.post("/ai/usage")
def record_usage(
    payload: ProviderUsageRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.units < 1:
        raise HTTPException(status_code=400, detail="units must be >= 1")

    return record_provider_usage(
        db=db,
        user_id=user.id,
        provider=payload.provider,
        units=payload.units,
        operation=payload.operation,
    )


class AIExecuteRequest(BaseModel):
    prompt: str
    provider: str | None = None
    api_key: str | None = None
    estimated_units: int = 1


@router.post("/ai/execute")
async def ai_execute(
    payload: AIExecuteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt is required")

    decision = authorize_ai_call(
        db=db,
        user_id=user.id,
        requested_provider=payload.provider,
        estimated_units=payload.estimated_units,
    )

    if not decision.allowed:
        raise HTTPException(status_code=402, detail=decision.reason)

    result = await execute_provider(
        provider=decision.provider,
        prompt=payload.prompt,
        api_key=payload.api_key,
    )

    if not result.success:
        raise HTTPException(
            status_code=502,
            detail=result.error or "AI provider execution failed",
        )

    audit = audit_ai_generation(
        db=db,
        user_id=user.id,
        provider=result.provider,
        units=decision.estimated_units,
        content_type="ai_execution",
        status="completed",
    )

    return {
        "success": True,
        "provider": result.provider,
        "used_byok": result.used_byok,
        "content": result.content,
        "units": decision.estimated_units,
        "audit": audit,
    }
