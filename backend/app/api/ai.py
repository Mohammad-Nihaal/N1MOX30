from __future__ import annotations
from app.services.batch12.ai_gateway import authorize_ai_call

from typing import Any

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

from app.schemas.ai import (
    AIGenerationListResponse,
    AIGenerationResponse,
    GenerateContentRequest,
    GenerateContentResponse,
    ReuseGenerationRequest,
)

from app.services.ai_generation_service import (
    delete_generation,
    generation_to_response,
    get_generation,
    get_generation_history,
    save_generation,
)

from app.services.ai_service import (
    generate_content,
)

from app.services.research_service import (
    deserialize_list,
    get_research,
)


# =================================================
# ROUTER
# =================================================


router = APIRouter(
    prefix="/ai",
    tags=["AI Content"],
)


# =================================================
# CREATOR CONTEXT
# =================================================


def get_creator_context(
    *,
    db: Session,
    user_id: str,
    platform: str,
) -> dict[str, Any]:
    """
    Build creator and connected platform context
    for AI content generation.

    Relationship:

        User
          |
          v
    ConnectedAccount
          |
          v
    AnalyticsSnapshot
    """

    from app.models.analytics import AnalyticsSnapshot
    from app.models.connected_account import ConnectedAccount

    normalized_platform = platform.lower().strip()

    # ---------------------------------------------
    # FIND CONNECTED ACCOUNT
    # ---------------------------------------------

    account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == user_id,
            ConnectedAccount.platform == normalized_platform,
            ConnectedAccount.is_active.is_(True),
        )
        .order_by(
            ConnectedAccount.created_at.desc()
        )
        .first()
    )

    # ---------------------------------------------
    # NO CONNECTED ACCOUNT
    # ---------------------------------------------

    if not account:

        return {
            "has_connected_account": False,
            "platform": normalized_platform,
            "channel_name": None,
            "channel_id": None,
            "analytics": None,
        }

    # ---------------------------------------------
    # FIND LATEST ANALYTICS SNAPSHOT
    # ---------------------------------------------

    analytics_snapshot = (
        db.query(AnalyticsSnapshot)
        .filter(
            AnalyticsSnapshot.connected_account_id
            == account.id,
            AnalyticsSnapshot.platform
            == normalized_platform,
        )
        .order_by(
            AnalyticsSnapshot.recorded_at.desc()
        )
        .first()
    )

    analytics = None

    # ---------------------------------------------
    # BUILD ANALYTICS CONTEXT
    # ---------------------------------------------

    if analytics_snapshot:

        analytics = {
            "latest_views": (
                analytics_snapshot.views
            ),
            "latest_followers": (
                analytics_snapshot.followers
            ),
            "latest_likes": (
                analytics_snapshot.likes
            ),
            "latest_comments": (
                analytics_snapshot.comments
            ),
            "recorded_at": (
                analytics_snapshot.recorded_at
            ),
        }

    # ---------------------------------------------
    # RETURN CREATOR CONTEXT
    # ---------------------------------------------

    return {
        "has_connected_account": True,
        "platform": normalized_platform,
        "channel_name": (
            account.account_name
        ),
        "channel_id": (
            account.platform_account_id
        ),
        "analytics": analytics,
    }


# =================================================
# RESEARCH CONTEXT
# =================================================


def build_research_context(
    *,
    db: Session,
    user_id: str,
    research_id: str | None,
    opportunity_index: int,
) -> dict[str, Any] | None:
    """
    Load saved research and convert it into compact
    guidance for AI content generation.
    """

    if not research_id:
        return None

    research = get_research(
        db=db,
        user_id=user_id,
        research_id=research_id,
    )

    if not research:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research not found.",
        )

    if research.research_status != "completed":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This research is not ready for "
                "content generation."
            ),
        )

    keywords = deserialize_list(
        research.keywords
    )

    audience_angles = deserialize_list(
        research.audience_angles
    )

    content_opportunities = deserialize_list(
        research.content_opportunities
    )

    competitor_insights = deserialize_list(
        research.competitor_insights
    )

    selected_opportunity = None

    if content_opportunities:

        safe_index = min(
            max(opportunity_index, 0),
            len(content_opportunities) - 1,
        )

        selected_opportunity = (
            content_opportunities[
                safe_index
            ]
        )

    primary_keyword = None

    if keywords:
        primary_keyword = keywords[0]

    audience_angle = None

    if audience_angles:
        audience_angle = audience_angles[0]

    competitor_insight = None

    if competitor_insights:
        competitor_insight = competitor_insights[0]

    return {
        "research_id": research.id,
        "topic": research.topic,
        "primary_keyword": primary_keyword,
        "audience_angle": audience_angle,
        "content_opportunity": (
            selected_opportunity
        ),
        "competitor_insight": (
            competitor_insight
        ),
        "research_summary": (
            research.research_summary
        ),
        "opportunity_score": (
            research.opportunity_score
        ),
        "trend_score": (
            research.trend_score
        ),
    }


# =================================================
# ATTACH RESEARCH CONTEXT
# =================================================


def attach_research_context(
    *,
    creator_context: dict[str, Any],
    research_context: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Attach research guidance to creator context.

    ai_service.generate_content() expects research
    information inside creator_context.
    """

    updated_context = dict(
        creator_context
    )

    if research_context:

        updated_context[
            "research_context"
        ] = research_context

    return updated_context


# =================================================
# BUILD GENERATION RESPONSE
# =================================================


def build_generation_response(
    *,
    generation: Any,
    result: dict[str, Any],
    creator_context: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a consistent API response.
    """

    return {
        "generation_id": generation.id,
        "platform": generation.platform,
        "topic": generation.topic,
        "content_type": generation.content_type,
        "tone": generation.tone,
        "titles": result.get(
            "titles",
            [],
        ),
        "script": result.get(
            "script",
            "",
        ),
        "caption": result.get(
            "caption",
            "",
        ),
        "hashtags": result.get(
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
# GENERATE CONTENT
# =================================================


@router.post(
    "/generate",
    response_model=GenerateContentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ai_content(
    content_data: GenerateContentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate AI-powered creator content.
    """

    # ---------------------------------------------
    # BUILD CREATOR CONTEXT
    # ---------------------------------------------

    creator_context = get_creator_context(
        db=db,
        user_id=current_user.id,
        platform=content_data.platform,
    )

    # ---------------------------------------------
    # BUILD OPTIONAL RESEARCH CONTEXT
    # ---------------------------------------------

    research_context = build_research_context(
        db=db,
        user_id=current_user.id,
        research_id=content_data.research_id,
        opportunity_index=(
            content_data.opportunity_index
        ),
    )

    creator_context = attach_research_context(
        creator_context=creator_context,
        research_context=research_context,
    )

    # ---------------------------------------------
    # GENERATE CONTENT
    # ---------------------------------------------

    try:

        result = generate_content(
            platform=content_data.platform,
            topic=content_data.topic,
            content_type=(
                content_data.content_type
            ),
            tone=content_data.tone,
            creator_context=creator_context,
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"AI content generation failed: {exc}"
            ),
        ) from exc

    # ---------------------------------------------
    # EXTRACT RESULT
    # ---------------------------------------------

    titles = result.get(
        "titles",
        [],
    )

    script = result.get(
        "script",
        "",
    )

    caption = result.get(
        "caption",
        "",
    )

    hashtags = result.get(
        "hashtags",
        [],
    )

    provider = result.get(
        "provider"
    )

    if not provider:

        provider = (
            "deterministic_fallback"
        )

    # ---------------------------------------------
    # SAVE GENERATION
    # ---------------------------------------------

    generation = save_generation(
        db=db,
        user_id=current_user.id,
        platform=content_data.platform,
        topic=content_data.topic,
        content_type=(
            content_data.content_type
        ),
        tone=content_data.tone,
        titles=titles,
        script=script,
        caption=caption,
        hashtags=hashtags,
        provider=provider,
        generation_status="completed",
    )

    # ---------------------------------------------
    # RETURN RESPONSE
    # ---------------------------------------------

    return build_generation_response(
        generation=generation,
        result=result,
        creator_context=creator_context,
    )


# =================================================
# GENERATION HISTORY
# =================================================


@router.get(
    "/history",
    response_model=AIGenerationListResponse,
)
def get_my_generation_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get authenticated user's AI generation history.
    """

    limit = min(
        max(limit, 1),
        100,
    )

    offset = max(
        offset,
        0,
    )

    generations, total = (
        get_generation_history(
            db=db,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
        )
    )

    return {
        "total": total,
        "generations": [
            generation_to_response(
                generation
            )
            for generation in generations
        ],
    }


# =================================================
# GET SINGLE GENERATION
# =================================================


@router.get(
    "/history/{generation_id}",
    response_model=AIGenerationResponse,
)
def get_single_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get one AI generation belonging to the
    authenticated user.
    """

    generation = get_generation(
        db=db,
        user_id=current_user.id,
        generation_id=generation_id,
    )

    if not generation:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI generation not found.",
        )

    return generation_to_response(
        generation
    )


# =================================================
# REUSE / REGENERATE
# =================================================


@router.post(
    "/history/{generation_id}/reuse",
    response_model=GenerateContentResponse,
    status_code=status.HTTP_201_CREATED,
)
def reuse_generation(
    generation_id: str,
    reuse_data: ReuseGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reuse a previous generation with optional changes.
    """

    previous_generation = get_generation(
        db=db,
        user_id=current_user.id,
        generation_id=generation_id,
    )

    if not previous_generation:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI generation not found.",
        )

    topic = (
        reuse_data.topic
        or previous_generation.topic
    )

    content_type = (
        reuse_data.content_type
        or previous_generation.content_type
    )

    tone = (
        reuse_data.tone
        or previous_generation.tone
    )

    # ---------------------------------------------
    # BUILD CREATOR CONTEXT
    # ---------------------------------------------

    creator_context = get_creator_context(
        db=db,
        user_id=current_user.id,
        platform=previous_generation.platform,
    )

    # ---------------------------------------------
    # BUILD OPTIONAL RESEARCH CONTEXT
    # ---------------------------------------------

    research_context = build_research_context(
        db=db,
        user_id=current_user.id,
        research_id=reuse_data.research_id,
        opportunity_index=(
            reuse_data.opportunity_index
        ),
    )

    creator_context = attach_research_context(
        creator_context=creator_context,
        research_context=research_context,
    )

    # ---------------------------------------------
    # GENERATE CONTENT
    # ---------------------------------------------

    try:

        result = generate_content(
            platform=previous_generation.platform,
            topic=topic,
            content_type=content_type,
            tone=tone,
            creator_context=creator_context,
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"AI content generation failed: {exc}"
            ),
        ) from exc

    # ---------------------------------------------
    # EXTRACT RESULT
    # ---------------------------------------------

    titles = result.get(
        "titles",
        [],
    )

    script = result.get(
        "script",
        "",
    )

    caption = result.get(
        "caption",
        "",
    )

    hashtags = result.get(
        "hashtags",
        [],
    )

    provider = result.get(
        "provider"
    )

    if not provider:

        provider = (
            "deterministic_fallback"
        )

    # ---------------------------------------------
    # SAVE GENERATION
    # ---------------------------------------------

    generation = save_generation(
        db=db,
        user_id=current_user.id,
        platform=previous_generation.platform,
        topic=topic,
        content_type=content_type,
        tone=tone,
        titles=titles,
        script=script,
        caption=caption,
        hashtags=hashtags,
        provider=provider,
        generation_status="completed",
    )

    # ---------------------------------------------
    # RETURN RESPONSE
    # ---------------------------------------------

    return build_generation_response(
        generation=generation,
        result=result,
        creator_context=creator_context,
    )


# =================================================
# DELETE GENERATION
# =================================================


@router.delete(
    "/history/{generation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete one AI generation belonging to the
    authenticated user.
    """

    deleted = delete_generation(
        db=db,
        user_id=current_user.id,
        generation_id=generation_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI generation not found.",
        )

    return None


# N1MOX30_BATCH12_GATEWAY
def _batch12_authorize_generation(db, user_id, provider=None, estimated_units=1):
    """Authorize AI generation through the Batch 12 gateway."""
    return authorize_ai_call(
        db=db,
        user_id=user_id,
        requested_provider=provider,
        estimated_units=estimated_units,
    )
