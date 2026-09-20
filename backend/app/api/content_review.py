from fastapi import APIRouter

from app.schemas.content_review import (
    ContentReviewRequest,
    ContentReviewResponse,
)
from app.services.content_review.review_service import (
    content_review_service,
)


router = APIRouter(
    prefix="/content-review",
    tags=["Content Review"],
)


@router.post(
    "/review",
    response_model=ContentReviewResponse,
)
def review_content(
    request: ContentReviewRequest,
) -> ContentReviewResponse:
    return content_review_service.review(request)


@router.get("/health")
def content_review_health() -> dict[str, str]:
    return {
        "service": "content-review",
        "status": "ready",
    }
