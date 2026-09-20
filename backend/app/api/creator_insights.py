from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.analytics.creator_analytics import (
    analyze_content,
)
from app.services.growth.intelligence import (
    build_growth_report,
)

router = APIRouter(
    prefix="/platform/v13/insights",
    tags=["creator-insights"],
)


class ContentAnalysisRequest(BaseModel):
    title: str
    metrics: dict = {}


class GrowthRequest(BaseModel):
    metrics: dict = {}


@router.post("/content")
def content_analysis(payload: ContentAnalysisRequest):
    return analyze_content(
        title=payload.title,
        metrics=payload.metrics,
    )


@router.post("/growth")
def growth_analysis(payload: GrowthRequest):
    return build_growth_report(
        metrics=payload.metrics,
    )