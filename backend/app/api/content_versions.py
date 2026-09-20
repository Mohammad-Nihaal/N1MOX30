from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.content import Content
from app.models.user import User
from app.schemas.content_version import (
    ContentVersionCompareResponse,
    ContentVersionCreate,
    ContentVersionListResponse,
    ContentVersionRestoreResponse,
    ContentVersionResponse,
)
from app.versioning.content_version_service import ContentVersionService

router = APIRouter(
    prefix="/content-versions",
    tags=["Content Versioning"],
)


def _get_content(
    content_id: str,
    current_user: User,
    db: Session,
) -> Content:
    content = (
        db.query(Content)
        .filter(
            Content.id == content_id,
            Content.user_id == current_user.id,
        )
        .first()
    )

    if not content:
        raise HTTPException(
            status_code=404,
            detail="Content not found.",
        )

    return content


@router.post(
    "/{content_id}",
    response_model=ContentVersionResponse,
)
def create_version(
    content_id: str,
    payload: ContentVersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = _get_content(content_id, current_user, db)

    service = ContentVersionService(db)

    return service.create_version(
        content=content,
        changes=payload.changes,
        created_by="creator",
        reason=payload.reason,
    )


@router.get(
    "/{content_id}",
    response_model=ContentVersionListResponse,
)
def list_versions(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = _get_content(content_id, current_user, db)

    service = ContentVersionService(db)

    return {
        "content_id": str(content.id),
        "current_version": getattr(content, "current_version", 0) or 0,
        "versions": service.get_versions(content),
    }


@router.get(
    "/{content_id}/{version_number}",
    response_model=ContentVersionResponse,
)
def get_version(
    content_id: str,
    version_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = _get_content(content_id, current_user, db)

    service = ContentVersionService(db)

    version = service.get_version(content, version_number)

    if not version:
        raise HTTPException(
            status_code=404,
            detail="Content version not found.",
        )

    return version


@router.get(
    "/{content_id}/compare/{first_version}/{second_version}",
    response_model=ContentVersionCompareResponse,
)
def compare_versions(
    content_id: str,
    first_version: int,
    second_version: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = _get_content(content_id, current_user, db)

    service = ContentVersionService(db)

    try:
        return service.compare_versions(
            content=content,
            first_version=first_version,
            second_version=second_version,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post(
    "/{content_id}/restore/{version_number}",
    response_model=ContentVersionRestoreResponse,
)
def restore_version(
    content_id: str,
    version_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = _get_content(content_id, current_user, db)

    service = ContentVersionService(db)

    try:
        new_version = service.restore_version(
            content=content,
            version_number=version_number,
            created_by="creator",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "content_id": str(content.id),
        "restored_from_version": version_number,
        "new_version": new_version,
    }
