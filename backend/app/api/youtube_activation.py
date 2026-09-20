from fastapi import APIRouter

from app.services.publishing.durable_queue import (
    list_queue,
)
from app.services.publishing.queue_executor import (
    execute_queue_item,
)
from app.services.analytics.history import (
    calculate_trends,
)


router = APIRouter(
    prefix="/platform/v20/activation",
    tags=["YouTube Activation"],
)


@router.get("/queue")
def queue():
    return {
        "status": "ready",
        "items": list_queue(),
    }


@router.post("/queue/{job_id}/execute")
def execute(job_id: str):
    return execute_queue_item(job_id)


@router.get("/analytics/{user_id}/trends")
def trends(user_id: int):
    return calculate_trends(user_id)