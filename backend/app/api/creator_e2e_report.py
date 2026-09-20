from fastapi import APIRouter

from app.services.analytics.e2e_report import (
    build_e2e_growth_report,
)
from app.services.publishing.publish_gate import (
    authorize_real_publish,
)

router = APIRouter(
    prefix="/platform/v22/e2e-report",
    tags=["Creator OS E2E Report"],
)


@router.get("/{user_id}")
def report(user_id: int):
    return build_e2e_growth_report(user_id)


@router.get("/publish-gate/status")
def publish_gate():
    return authorize_real_publish()