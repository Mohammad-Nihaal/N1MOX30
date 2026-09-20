from datetime import datetime, timezone

from app.services.publishing.queue import (
    execute_publish_job,
    get_job,
    update_job,
)

from app.services.publishing.tracking import record_publish_result


def _now():
    return datetime.now(timezone.utc).isoformat()


def process_publish_job(job, access_token=None):
    job["worker_started_at"] = _now()
    update_job(job)

    result = execute_publish_job(
        job,
        access_token=access_token,
    )

    result["worker_completed_at"] = _now()

    if result.get("status") in {
        "published",
        "failed",
        "retry_pending",
        "authorization_required",
    }:
        record_publish_result(
            publish_job_id=job["job_id"],
            account_id=job["account_id"],
            result=result,
            metadata=job.get("metadata", {}),
        )

    update_job(result)

    return result


def process_publish_job_by_id(
    job_id,
    access_token=None,
):
    job = get_job(job_id)

    if not job:
        return {
            "status": "not_found",
            "job_id": job_id,
        }

    return process_publish_job(
        job,
        access_token=access_token,
    )