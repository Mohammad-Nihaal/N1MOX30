from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User

from app.schemas.research import (
    GenerateContentFromResearchRequest,
    ResearchHistoryResponse,
    ResearchListResponse,
    ResearchRequest,
    ResearchResponse,
)

from app.services.ai_generation_service import (
    save_generation,
)

from app.services.ai_service import (
    generate_content,
)

from app.services.creator_context_service import (
    get_creator_context,
)

from app.services.research_service import (
    calculate_opportunity_score,
    calculate_trend_score,
    delete_research,
    generate_fallback_research,
    get_research,
    get_research_history,
    normalize_research_result,
    research_to_response,
    save_research,
)


router = APIRouter(
    prefix="/research",
    tags=["AI Research"],
)


# =================================================
# RESEARCH GENERATION
# =================================================


@router.post(
    "/",
    response_model=ResearchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_research(
    research_data: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate AI-powered research for a topic.
    """

    try:
        raw_result = generate_fallback_research(
            topic=research_data.topic,
            platform=research_data.platform,
        )

        normalized_result = normalize_research_result(
            result=raw_result,
            topic=research_data.topic,
            platform=research_data.platform,
        )

        opportunity_score = normalized_result.get(
            "opportunity_score"
        )

        if opportunity_score is None:
            opportunity_score = (
                calculate_opportunity_score(
                    keywords=normalized_result[
                        "keywords"
                    ],
                    audience_angles=normalized_result[
                        "audience_angles"
                    ],
                    content_opportunities=normalized_result[
                        "content_opportunities"
                    ],
                )
            )

        trend_score = normalized_result.get(
            "trend_score"
        )

        if trend_score is None:
            trend_score = calculate_trend_score(
                topic=research_data.topic,
                keywords=normalized_result[
                    "keywords"
                ],
                content_opportunities=normalized_result[
                    "content_opportunities"
                ],
            )

        research = save_research(
            db=db,
            user_id=current_user.id,
            platform=research_data.platform,
            topic=research_data.topic,
            keywords=normalized_result[
                "keywords"
            ],
            audience_angles=normalized_result[
                "audience_angles"
            ],
            content_opportunities=normalized_result[
                "content_opportunities"
            ],
            competitor_insights=normalized_result[
                "competitor_insights"
            ],
            research_summary=normalized_result[
                "research_summary"
            ],
            opportunity_score=opportunity_score,
            trend_score=trend_score,
            provider=raw_result.get(
                "provider"
            ),
            research_status="completed",
        )

        return {
            "research_id": research.id,
            "platform": research.platform,
            "topic": research.topic,
            "keywords": normalized_result[
                "keywords"
            ],
            "audience_angles": normalized_result[
                "audience_angles"
            ],
            "content_opportunities": normalized_result[
                "content_opportunities"
            ],
            "competitor_insights": normalized_result[
                "competitor_insights"
            ],
            "research_summary": normalized_result[
                "research_summary"
            ],
            "opportunity_score": opportunity_score,
            "trend_score": trend_score,
            "provider": research.provider,
            "research_status": research.research_status,
            "created_at": research.created_at,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Research generation failed: {exc}"
            ),
        ) from exc


# =================================================
# GENERATE CONTENT FROM RESEARCH
# =================================================


@router.post(
    "/{research_id}/generate-content",
    status_code=status.HTTP_201_CREATED,
)
def generate_content_from_research(
    research_id: str,
    generation_data: GenerateContentFromResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate AI content using a research record.

    The original research topic remains the content
    topic. Research insights are passed separately
    as creator context so they guide generation
    without polluting titles or scripts.
    """

    research = get_research(
        db=db,
        user_id=current_user.id,
        research_id=research_id,
    )

    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research not found.",
        )

    research_data = research_to_response(
        research
    )

    opportunities = (
        research_data.get(
            "content_opportunities"
        )
        or []
    )

    if not opportunities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This research record has no "
                "content opportunities."
            ),
        )

    opportunity_index = (
        generation_data.opportunity_index
    )

    if opportunity_index >= len(opportunities):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"opportunity_index must be between "
                f"0 and {len(opportunities) - 1}."
            ),
        )

    selected_opportunity = opportunities[
        opportunity_index
    ]

    keywords = research_data.get(
        "keywords"
    ) or []

    audience_angles = research_data.get(
        "audience_angles"
    ) or []

    competitor_insights = research_data.get(
        "competitor_insights"
    ) or []

    primary_keyword = (
        keywords[0]
        if keywords
        else research.topic
    )

    audience_angle = (
        audience_angles[
            opportunity_index
            % len(audience_angles)
        ]
        if audience_angles
        else None
    )

    competitor_insight = (
        competitor_insights[
            opportunity_index
            % len(competitor_insights)
        ]
        if competitor_insights
        else None
    )

    # ---------------------------------------------
    # GET EXISTING CREATOR CONTEXT
    # ---------------------------------------------

    creator_context = get_creator_context(
        db=db,
        user_id=current_user.id,
        platform=research.platform,
    )

    if not isinstance(
        creator_context,
        dict,
    ):
        creator_context = {}

    # ---------------------------------------------
    # ADD RESEARCH CONTEXT SEPARATELY
    # ---------------------------------------------

    creator_context["research_context"] = {
        "primary_keyword": primary_keyword,
        "audience_angle": audience_angle,
        "content_opportunity": selected_opportunity,
        "competitor_insight": competitor_insight,
        "research_summary": research_data.get(
            "research_summary"
        ),
        "opportunity_score": research_data.get(
            "opportunity_score"
        ),
        "trend_score": research_data.get(
            "trend_score"
        ),
    }

    # ---------------------------------------------
    # GENERATE AI CONTENT
    # ---------------------------------------------

    generated_content = generate_content(
        platform=research.platform,
        topic=research.topic,
        content_type=(
            generation_data.content_type
        ),
        tone=generation_data.tone,
        creator_context=creator_context,
    )

    # ---------------------------------------------
    # SAVE AI GENERATION
    # ---------------------------------------------

    generation = save_generation(
        db=db,
        user_id=current_user.id,
        platform=research.platform,
        topic=research.topic,
        content_type=(
            generation_data.content_type
        ),
        tone=generation_data.tone,
        titles=generated_content.get(
            "titles",
            [],
        ),
        script=generated_content.get(
            "script",
        ),
        caption=generated_content.get(
            "caption",
        ),
        hashtags=generated_content.get(
            "hashtags",
            [],
        ),
        provider=generated_content.get(
            "provider"
        ),
        generation_status=generated_content.get(
            "generation_status",
            "completed",
        ),
    )

    # ---------------------------------------------
    # RESPONSE
    # ---------------------------------------------

    return {
        "research_id": research.id,
        "generation_id": generation.id,
        "platform": generation.platform,
        "topic": generation.topic,
        "selected_opportunity": (
            selected_opportunity
        ),
        "content_type": generation.content_type,
        "tone": generation.tone,
        "titles": generated_content.get(
            "titles",
            [],
        ),
        "script": generated_content.get(
            "script",
            "",
        ),
        "caption": generated_content.get(
            "caption",
            "",
        ),
        "hashtags": generated_content.get(
            "hashtags",
            [],
        ),
        "provider": generation.provider,
        "generation_status": (
            generation.generation_status
        ),
        "created_at": generation.created_at,
        "creator_context": creator_context,
    }


# =================================================
# RESEARCH HISTORY
# =================================================


@router.get(
    "/",
    response_model=ResearchListResponse,
)
def get_my_research_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the authenticated user's research history.
    """

    limit = min(
        max(limit, 1),
        100,
    )

    offset = max(
        offset,
        0,
    )

    research_items, total = (
        get_research_history(
            db=db,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
        )
    )

    return {
        "total": total,
        "research": [
            research_to_response(
                item
            )
            for item in research_items
        ],
    }


# =================================================
# GET SINGLE RESEARCH
# =================================================


@router.get(
    "/{research_id}",
    response_model=ResearchHistoryResponse,
)
def get_single_research(
    research_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get one research record."""

    research = get_research(
        db=db,
        user_id=current_user.id,
        research_id=research_id,
    )

    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research not found.",
        )

    return research_to_response(
        research
    )


# =================================================
# DELETE RESEARCH
# =================================================


@router.delete(
    "/{research_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_research(
    research_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete one research record."""

    deleted = delete_research(
        db=db,
        user_id=current_user.id,
        research_id=research_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research not found.",
        )

    return None