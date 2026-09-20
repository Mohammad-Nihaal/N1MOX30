import uuid
from unittest.mock import patch


def test_queue_module_exposes_durable_operations():
    from app.services.publishing import durable_queue

    assert callable(getattr(durable_queue, "enqueue", None))
    assert callable(getattr(durable_queue, "load", None))
    assert callable(getattr(durable_queue, "mark_attempt", None))


def test_queue_persists_publish_payload():
    from app.services.publishing.durable_queue import enqueue, load

    job_id = "batch8-" + uuid.uuid4().hex

    payload = {
        "video_path": "batch8.mp4",
        "title": "N1MOX30 Batch 8",
        "description": "Durable queue test",
        "tags": ["N1MOX30"],
        "privacy_status": "private",
    }

    enqueue(
        job_id,
        900008,
        "batch8-account",
        payload,
    )

    job = load(job_id)

    assert job is not None
    assert job_id in str(job)
    assert "batch8.mp4" in str(job)


def test_queue_executor_handles_missing_asset():
    from app.services.publishing.durable_queue import enqueue
    from app.services.publishing.queue_executor import execute_queue_item

    job_id = "batch8-missing-" + uuid.uuid4().hex

    enqueue(
        job_id,
        900009,
        "batch8-account",
        {
            "video_path": "definitely-missing-batch8.mp4",
            "title": "N1MOX30 Batch 8",
        },
    )

    result = execute_queue_item(job_id)

    assert result is not None
    assert result.get("status") in {
        "asset_missing",
        "failed",
        "authorization_required",
        "blocked",
    }


def test_queue_executor_respects_publisher_safety_gate(tmp_path):
    from app.services.publishing.durable_queue import enqueue
    from app.services.publishing.queue_executor import execute_queue_item

    video = tmp_path / "batch8.mp4"
    video.write_bytes(b"batch8-video")

    job_id = "batch8-safe-" + uuid.uuid4().hex

    enqueue(
        job_id,
        900010,
        "batch8-account",
        {
            "video_path": str(video),
            "title": "N1MOX30 Batch 8 Safety",
        },
    )

    with patch(
        "app.services.publishing.real_youtube_publish._token_for_account",
        return_value="batch8-token",
    ):
        result = execute_queue_item(job_id)

    assert result is not None
    assert result.get("status") in {
        "blocked",
        "ready_for_real_upload",
        "published",
    }

    # Real publishing must remain disabled in this batch.
    assert result.get("status") != "published"


def test_queue_failure_boundary_does_not_fake_success():
    from app.services.publishing.durable_queue import enqueue
    from app.services.publishing.queue_executor import execute_queue_item

    job_id = "batch8-failure-" + uuid.uuid4().hex

    enqueue(
        job_id,
        900011,
        "batch8-account",
        {
            "video_path": "missing-batch8-failure.mp4",
            "title": "N1MOX30 Batch 8 Failure",
        },
    )

    result = execute_queue_item(job_id)

    assert result.get("status") != "published"

