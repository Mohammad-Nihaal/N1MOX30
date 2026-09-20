import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
)

from app.core.database import get_db

from app.models.user import User

from app.schemas.media_asset import (
    MediaAssetCreate,
    MediaAssetListResponse,
    MediaAssetResponse,
    MediaAssetStatusUpdate,
    MediaAssetUpdate,
)

from app.services.media_asset_service import (
    MediaAssetService,
)


router = APIRouter(
    prefix="/media-assets",
    tags=["Media Assets"],
)


# =================================================
# CREATE
# =================================================

@router.post(
    "",
    response_model=MediaAssetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_media_asset(
    asset_data: MediaAssetCreate,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
):
    """
    Register a media asset.
    """

    service = MediaAssetService(
        db,
    )

    try:

        asset = service.create_asset(
            user_id=current_user.id,
            project_id=asset_data.project_id,
            content_id=asset_data.content_id,
            asset_type=asset_data.asset_type,
            media_type=asset_data.media_type,
            name=asset_data.name,
            description=asset_data.description,
            original_filename=(
                asset_data.original_filename
            ),
            storage_provider=(
                asset_data.storage_provider
            ),
            storage_path=(
                asset_data.storage_path
            ),
            public_url=asset_data.public_url,
            provider_asset_id=(
                asset_data.provider_asset_id
            ),
            mime_type=asset_data.mime_type,
            file_extension=(
                asset_data.file_extension
            ),
            file_size_bytes=(
                asset_data.file_size_bytes
            ),
            width=asset_data.width,
            height=asset_data.height,
            duration_seconds=(
                asset_data.duration_seconds
            ),
            frame_rate=asset_data.frame_rate,
            scene_number=asset_data.scene_number,
            asset_role=asset_data.asset_role,
            metadata=asset_data.metadata,
            max_retries=asset_data.max_retries,
        )

        return service.asset_to_response(
            asset,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(error),
        ) from error


# =================================================
# UPLOAD
# =================================================

@router.post(
    "/upload",
    response_model=MediaAssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_media_asset(
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    name: str | None = Form(
        default=None,
    ),
    project_id: str | None = Form(
        default=None,
    ),
    content_id: str | None = Form(
        default=None,
    ),
    scene_number: int | None = Form(
        default=None,
    ),
    asset_role: str | None = Form(
        default=None,
    ),
    description: str | None = Form(
        default=None,
    ),
    metadata_json: str | None = Form(
        default=None,
    ),
    duration_seconds: float | None = Form(
        default=None,
    ),
    storage_provider: str = Form(
        default="local",
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
):
    """
    Upload a media asset.

    Supported examples:

    - image
    - video
    - audio
    - thumbnail
    """

    metadata: dict | None = None

    if metadata_json:

        try:
            parsed_metadata = json.loads(
                metadata_json,
            )

            if isinstance(
                parsed_metadata,
                dict,
            ):
                metadata = parsed_metadata

        except json.JSONDecodeError as error:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "metadata_json must be "
                    "valid JSON."
                ),
            ) from error

    service = MediaAssetService(
        db,
    )

    try:

        asset = await (
            service.upload_asset(
                user_id=current_user.id,
                file=file,
                asset_type=asset_type,
                name=name,
                project_id=project_id,
                content_id=content_id,
                scene_number=scene_number,
                asset_role=asset_role,
                description=description,
                metadata=metadata,
                duration_seconds=(
                    duration_seconds
                ),
                storage_provider=(
                    storage_provider
                ),
            )
        )

        return service.asset_to_response(
            asset,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(error),
        ) from error

    except Exception as error:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Media asset upload failed: "
                f"{str(error)}"
            ),
        ) from error


# =================================================
# LIST
# =================================================

@router.get(
    "",
    response_model=MediaAssetListResponse,
)
def get_media_assets(
    project_id: str | None = None,
    content_id: str | None = None,
    asset_type: str | None = None,
    asset_status: str | None = None,
    scene_number: int | None = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
):
    """
    Get media assets.
    """

    service = MediaAssetService(
        db,
    )

    try:

        assets, total = (
            service.get_assets(
                user_id=current_user.id,
                project_id=project_id,
                content_id=content_id,
                asset_type=asset_type,
                status=asset_status,
                scene_number=scene_number,
                limit=limit,
                offset=offset,
            )
        )

        return {
            "total": total,
            "assets": [
                service.asset_to_response(
                    asset,
                )
                for asset in assets
            ],
        }

    except ValueError as error:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(error),
        ) from error


# =================================================
# GET ONE
# =================================================

@router.get(
    "/{asset_id}",
    response_model=MediaAssetResponse,
)
def get_media_asset(
    asset_id: str,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
):
    """
    Get one media asset.
    """

    service = MediaAssetService(
        db,
    )

    asset = service.get_asset(
        asset_id=asset_id,
        user_id=current_user.id,
    )

    if asset is None:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Media asset not found.",
        )

    return service.asset_to_response(
        asset,
    )


# =================================================
# UPDATE
# =================================================

@router.put(
    "/{asset_id}",
    response_model=MediaAssetResponse,
)
def update_media_asset(
    asset_id: str,
    update_data: MediaAssetUpdate,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
):
    """
    Update media asset information.
    """

    service = MediaAssetService(
        db,
    )

    asset = service.get_asset(
        asset_id=asset_id,
        user_id=current_user.id,
    )

    if asset is None:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Media asset not found.",
        )

    updated_asset = service.update_asset(
        asset=asset,
        data=(
            update_data
            .model_dump(
                exclude_unset=True,
            )
        ),
    )

    return service.asset_to_response(
        updated_asset,
    )


# =================================================
# STATUS
# =================================================

@router.patch(
    "/{asset_id}/status",
    response_model=MediaAssetResponse,
)
def update_media_asset_status(
    asset_id: str,
    status_data: MediaAssetStatusUpdate,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
):
    """
    Update media asset status.
    """

    service = MediaAssetService(
        db,
    )

    asset = service.get_asset(
        asset_id=asset_id,
        user_id=current_user.id,
    )

    if asset is None:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Media asset not found.",
        )

    try:

        updated_asset = (
            service.update_asset_status(
                asset=asset,
                status=status_data.status,
                error_message=(
                    status_data.error_message
                ),
            )
        )

        return service.asset_to_response(
            updated_asset,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(error),
        ) from error


# =================================================
# RETRY
# =================================================

@router.post(
    "/{asset_id}/retry",
    response_model=MediaAssetResponse,
)
def retry_media_asset(
    asset_id: str,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
):
    """
    Retry a failed media asset.
    """

    service = MediaAssetService(
        db,
    )

    asset = service.get_asset(
        asset_id=asset_id,
        user_id=current_user.id,
    )

    if asset is None:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Media asset not found.",
        )

    try:

        retried_asset = (
            service.retry_asset(
                asset=asset,
            )
        )

        return service.asset_to_response(
            retried_asset,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(error),
        ) from error


# =================================================
# VERIFY FILE
# =================================================

@router.get(
    "/{asset_id}/verify",
)
def verify_media_asset(
    asset_id: str,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
):
    """
    Verify underlying asset storage.
    """

    service = MediaAssetService(
        db,
    )

    asset = service.get_asset(
        asset_id=asset_id,
        user_id=current_user.id,
    )

    if asset is None:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Media asset not found.",
        )

    file_exists = (
        service.verify_asset_file(
            asset=asset,
        )
    )

    return {
        "asset_id": asset.id,
        "status": asset.status,
        "file_exists": file_exists,
    }


# =================================================
# DELETE
# =================================================

@router.delete(
    "/{asset_id}",
)
def delete_media_asset(
    asset_id: str,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
):
    """
    Delete a media asset and its stored file.
    """

    service = MediaAssetService(
        db,
    )

    asset = service.get_asset(
        asset_id=asset_id,
        user_id=current_user.id,
    )

    if asset is None:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Media asset not found.",
        )

    service.delete_asset(
        asset=asset,
    )

    return {
        "message": (
            "Media asset deleted successfully."
        ),
        "asset_id": asset_id,
    }