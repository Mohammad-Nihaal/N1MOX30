import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
QUEUE_ROOT = ROOT / "storage" / "publishing_queue"
QUEUE_ROOT.mkdir(parents=True, exist_ok=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _path(job_id: str) -> Path:
    return QUEUE_ROOT / f"{job_id}.json"


def enqueue(
    job_id: str,
    user_id: int,
    account_id: str,
    payload: dict,
):
    item = {
        "job_id": job_id,
        "user_id": user_id,
        "account_id": account_id,
        "payload": payload,
        "status": "queued",
        "attempts": 0,
        "max_attempts": 3,
        "created_at": _now(),
        "updated_at": _now(),
        "last_error": None,
    }

    _path(job_id).write_text(
        json.dumps(
            item,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return item


def load(job_id: str):
    path = _path(job_id)

    if not path.exists():
        return None

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def update(job_id: str, **changes):
    item = load(job_id)

    if not item:
        return None

    item.update(changes)
    item["updated_at"] = _now()

    _path(job_id).write_text(
        json.dumps(
            item,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return item


def mark_attempt(job_id: str):
    item = load(job_id)

    if not item:
        return None

    attempts = int(item.get("attempts", 0)) + 1

    return update(
        job_id,
        attempts=attempts,
        status=(
            "retrying"
            if attempts < item.get("max_attempts", 3)
            else "failed"
        ),
    )


def list_queue():
    result = []

    for path in sorted(QUEUE_ROOT.glob("*.json")):
        try:
            result.append(
                json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )
            )
        except Exception:
            continue

    return result