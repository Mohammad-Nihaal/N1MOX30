from datetime import datetime, timezone
from typing import Any

from app.services.creator_os.pipeline import CREATOR_OS_STAGES
from app.services.production.engine import (
    create_job,
    execute_real_stage,
    generate_voice,
    generate_visuals,
    create_video,
    generate_captions,
    generate_thumbnail,
    generate_metadata,
    quality_check_production,
    schedule_production,
    publish_production,
)


def _now():
    return datetime.now(timezone.utc).isoformat()


def execute_creator_os(job: dict[str, Any]) -> dict[str, Any]:
    """
    Unified execution boundary for the real 13-stage Creator OS.

    Stages:
      research
      strategy
      hooks
      script
      voice
      visuals
      video
      captions
      thumbnail
      metadata
      quality_check
      scheduling
      publishing
    """

    job.setdefault("results", {})
    job.setdefault("completed_stages", [])
    job["started_at"] = job.get("started_at") or _now()
    job["status"] = "running"

    topic = job.get("topic", "")

    try:
        # 1-4: intellectual/content stages
        for stage in (
            "research",
            "strategy",
            "hooks",
            "script",
        ):
            result = execute_real_stage(
                job,
                stage,
                topic,
            )

            job["results"][stage] = result

            if stage not in job["completed_stages"]:
                job["completed_stages"].append(stage)

        # 5-8: media stages
        job["results"]["voice"] = generate_voice(job)
        job["completed_stages"].append("voice")

        job["results"]["visuals"] = generate_visuals(job)
        job["completed_stages"].append("visuals")

        job["results"]["video"] = create_video(job)
        job["completed_stages"].append("video")

        job["results"]["captions"] = generate_captions(job)
        job["completed_stages"].append("captions")

        # 9-13: publishing preparation
        job["results"]["thumbnail"] = generate_thumbnail(job)
        job["completed_stages"].append("thumbnail")

        job["results"]["metadata"] = generate_metadata(job)
        job["completed_stages"].append("metadata")

        job["results"]["quality_check"] = quality_check_production(job)
        job["completed_stages"].append("quality_check")

        job["results"]["scheduling"] = schedule_production(job)
        job["completed_stages"].append("scheduling")

        job["results"]["publishing"] = publish_production(job)
        job["completed_stages"].append("publishing")

        job["status"] = "completed"

    except Exception as exc:
        job["status"] = "failed"
        job["error"] = str(exc)

    job["completed_at"] = _now()

    total = len(CREATOR_OS_STAGES)
    done = len(set(job["completed_stages"]))

    job["progress_percent"] = round(
        (done / total) * 100,
        2,
    )

    return job