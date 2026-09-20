import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STORAGE = PROJECT_ROOT / "storage" / "publishing_tracking"
STORAGE.mkdir(parents=True, exist_ok=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _path(publish_job_id):
    return STORAGE / f"{publish_job_id}.json"


def record_publish_result(
    publish_job_id,
    account_id,
    result,
    metadata=None,
):
    payload = {
        "publish_job_id": publish_job_id,
        "account_id": account_id,
        "status": result.get("status"),
        "video_id": result.get("video_id"),
        "video_url": (
            f"https://www.youtube.com/watch?v={result['video_id']}"
            if result.get("video_id")
            else None
        ),
        "error": result.get("error"),
        "attempts": result.get("attempts", 0),
        "metadata": metadata or {},
        "updated_at": _now(),
    }

    _path(publish_job_id).write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    return payload


def get_publish_result(publish_job_id):
    path = _path(publish_job_id)

    if not path.exists():
        return {
            "status": "not_found",
            "publish_job_id": publish_job_id,
        }

    return json.loads(path.read_text(encoding="utf-8"))


def list_publish_results(account_id=None):
    results = []

    for path in STORAGE.glob("*.json"):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))

            if account_id and item.get("account_id") != account_id:
                continue

            results.append(item)
        except Exception:
            continue

    results.sort(
        key=lambda x: x.get("updated_at", ""),
        reverse=True,
    )

    return {
        "count": len(results),
        "results": results,
    }