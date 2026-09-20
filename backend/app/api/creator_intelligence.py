from fastapi import APIRouter

from app.schemas.creator_intelligence import (
    CreatorIntelligenceRequest,
    CreatorIntelligenceResponse,
)
from app.services.creator_intelligence.intelligence_service import (
    creator_intelligence_service,
)


router = APIRouter(
    prefix="/creator-intelligence",
    tags=["Creator Intelligence"],
)


@router.post(
    "/analyze",
    response_model=CreatorIntelligenceResponse,
)
def analyze_creator(
    request: CreatorIntelligenceRequest,
) -> CreatorIntelligenceResponse:
    return creator_intelligence_service.analyze(
        request,
    )


@router.get("/health")
def creator_intelligence_health() -> dict[str, str]:
    return {
        "service": "creator-intelligence",
        "status": "ready",
    }