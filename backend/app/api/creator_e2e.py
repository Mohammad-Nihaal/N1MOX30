from fastapi import APIRouter

from app.services.creator_os.e2e import (
    run_creator_os_e2e,
    build_publish_queue,
    e2e_summary,
)

router = APIRouter(
    prefix="/platform/v21/e2e",
    tags=["Creator OS E2E"],
)


@router.post("/run")
def run(
    user_id: int,
    topic: str,
):
    result = run_creator_os_e2e(
        user_id,
        topic,
    )

    return e2e_summary(result)


@router.post("/run/full")
def run_full(
    user_id: int,
    topic: str,
    account_id: str = "default",
):
    result = run_creator_os_e2e(
        user_id,
        topic,
    )

    queue_result = build_publish_queue(
        result,
        account_id,
    )

    summary = e2e_summary(result)
    summary["queue"] = queue_result

    return summary