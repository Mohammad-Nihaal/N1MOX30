from fastapi import APIRouter

from app.services.creator_dashboard.service import (
    build_creator_dashboard,
)

router=APIRouter(
    prefix="/platform/v15/dashboard",
    tags=["creator-dashboard"],
)


@router.get("/{user_id}")
def dashboard(user_id:int):
    return build_creator_dashboard(user_id)


@router.get("/{user_id}/summary")
def dashboard_summary(user_id:int):

    data=build_creator_dashboard(user_id)

    return {
        "status":data.get("status"),
        "channel":data.get("channel"),
        "summary":data.get("summary",{}),
        "growth":data.get("growth",{}),
        "publishing":data.get(
            "publishing",
            {},
        ),
    }