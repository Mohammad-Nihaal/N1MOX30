from app.services.publishing.real_youtube_publish import publish_video
from app.services.publishing.durable_queue import (
    load,
    mark_attempt,
    update,
)
from app.services.publishing.real_youtube_publish import (
    prepare_real_publish,
)


def execute_queue_item(job_id: str):
    item = load(job_id)

    if not item:
        return {
            "status": "not_found",
            "job_id": job_id,
        }

    if item.get("status") == "published":
        return item

    attempt = mark_attempt(job_id)

    if not attempt:
        return {
            "status": "not_found",
            "job_id": job_id,
        }

    payload = item.get("payload") or {}

    result = prepare_real_publish(
        user_id=item["user_id"],
        account_id=item["account_id"],
        video_path=payload.get("video_path", ""),
        title=payload.get(
            "title",
            "N1MOX30 Creator Video",
        ),
        description=payload.get(
            "description",
            "",
        ),
        tags=payload.get(
            "tags",
            [],
        ),
        privacy_status=payload.get(
            "privacy_status",
            "private",
        ),
    )

    if result["status"] == "ready_for_real_upload":
        return update(
            job_id,
            status="ready_for_real_upload",
            publish_result=result,
            last_error=None,
        )

    return update(
        job_id,
        status=result["status"],
        last_error=result.get(
            "message",
            result["status"],
        ),
        publish_result=result,
    )