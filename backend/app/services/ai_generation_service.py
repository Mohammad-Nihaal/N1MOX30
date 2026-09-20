import json

from sqlalchemy.orm import Session

from app.models.ai_completion import AICompletion
from app.models.ai_generation import AIGeneration


def serialize_list(
    values: list[str] | None,
) -> str | None:
    """Convert a list of strings into JSON for database storage."""

    if not values:
        return None

    return json.dumps(values)


def deserialize_list(
    value: str | None,
) -> list[str]:
    """Convert stored JSON text back into a list of strings."""

    if not value:
        return []

    try:
        parsed = json.loads(value)

        if isinstance(parsed, list):
            return [
                str(item)
                for item in parsed
            ]

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        pass

    return []


def build_generation_content(
    *,
    titles: list[str] | None = None,
    script: str | None = None,
    caption: str | None = None,
    hashtags: list[str] | None = None,
) -> str:
    """
    Build a single reviewable content value
    from an AI generation result.
    """

    content_parts: list[str] = []

    if titles:
        content_parts.append(
            "TITLES\n"
            + "\n".join(
                f"- {title}"
                for title in titles
            )
        )

    if script:
        content_parts.append(
            "SCRIPT\n"
            + script
        )

    if caption:
        content_parts.append(
            "CAPTION\n"
            + caption
        )

    if hashtags:
        content_parts.append(
            "HASHTAGS\n"
            + " ".join(hashtags)
        )

    return "\n\n".join(content_parts)


def create_completion_for_generation(
    *,
    db: Session,
    generation: AIGeneration,
    titles: list[str] | None = None,
    script: str | None = None,
    caption: str | None = None,
    hashtags: list[str] | None = None,
) -> AICompletion | None:
    """
    Create a pending AI completion record
    for a successfully generated AI result.

    Only one completion record is created
    for each AI generation.
    """

    if generation.generation_status != "completed":
        return None

    existing_completion = (
        db.query(AICompletion)
        .filter(
            AICompletion.generation_id == generation.id,
            AICompletion.user_id == generation.user_id,
        )
        .first()
    )

    if existing_completion is not None:
        return existing_completion

    content = build_generation_content(
        titles=titles,
        script=script,
        caption=caption,
        hashtags=hashtags,
    )

    if not content:
        return None

    completion = AICompletion(
        user_id=generation.user_id,
        generation_id=generation.id,
        workflow_id=None,
        project_id=None,
        content_type=generation.content_type,
        title=(
            f"AI {generation.content_type.title()} "
            f"for {generation.topic}"
        ),
        content=content,
        status="pending",
    )

    db.add(completion)
    db.commit()
    db.refresh(completion)

    return completion


def save_generation(
    *,
    db: Session,
    user_id: str,
    platform: str,
    topic: str,
    content_type: str,
    tone: str,
    titles: list[str] | None = None,
    script: str | None = None,
    caption: str | None = None,
    hashtags: list[str] | None = None,
    provider: str | None = None,
    generation_status: str = "completed",
    error_message: str | None = None,
) -> AIGeneration:
    """
    Save an AI content generation to the database.

    Successfully completed generations automatically
    receive an AI completion confirmation record.
    """

    generation = AIGeneration(
        user_id=user_id,
        platform=platform,
        topic=topic,
        content_type=content_type,
        tone=tone,
        titles=serialize_list(titles),
        script=script,
        caption=caption,
        hashtags=serialize_list(hashtags),
        provider=provider,
        generation_status=generation_status,
        error_message=error_message,
    )

    db.add(generation)
    db.commit()
    db.refresh(generation)

    create_completion_for_generation(
        db=db,
        generation=generation,
        titles=titles,
        script=script,
        caption=caption,
        hashtags=hashtags,
    )

    return generation


def get_generation(
    *,
    db: Session,
    user_id: str,
    generation_id: str,
) -> AIGeneration | None:
    """Get one AI generation belonging to the user."""

    return (
        db.query(AIGeneration)
        .filter(
            AIGeneration.id == generation_id,
            AIGeneration.user_id == user_id,
        )
        .first()
    )


def get_generation_history(
    *,
    db: Session,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[AIGeneration], int]:
    """Get AI generation history for a user."""

    query = (
        db.query(AIGeneration)
        .filter(
            AIGeneration.user_id == user_id
        )
    )

    total = query.count()

    generations = (
        query
        .order_by(
            AIGeneration.created_at.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return generations, total


def delete_generation(
    *,
    db: Session,
    user_id: str,
    generation_id: str,
) -> bool:
    """Delete one AI generation belonging to the user."""

    generation = get_generation(
        db=db,
        user_id=user_id,
        generation_id=generation_id,
    )

    if not generation:
        return False

    completions = (
        db.query(AICompletion)
        .filter(
            AICompletion.generation_id == generation.id,
            AICompletion.user_id == user_id,
        )
        .all()
    )

    for completion in completions:
        db.delete(completion)

    db.delete(generation)
    db.commit()

    return True


def generation_to_response(
    generation: AIGeneration,
) -> dict:
    """
    Convert a database generation into an API-safe
    response dictionary.
    """

    return {
        "id": generation.id,
        "user_id": generation.user_id,
        "platform": generation.platform,
        "topic": generation.topic,
        "content_type": generation.content_type,
        "tone": generation.tone,
        "titles": deserialize_list(
            generation.titles
        ),
        "script": generation.script,
        "caption": generation.caption,
        "hashtags": deserialize_list(
            generation.hashtags
        ),
        "provider": generation.provider,
        "generation_status": (
            generation.generation_status
        ),
        "error_message": generation.error_message,
        "created_at": generation.created_at,
        "updated_at": generation.updated_at,
    }