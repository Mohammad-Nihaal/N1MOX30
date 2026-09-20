import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HISTORY_ROOT = ROOT / "storage" / "analytics_history"
HISTORY_ROOT.mkdir(parents=True, exist_ok=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def save_snapshot(
    user_id: int,
    metrics: dict,
):
    path = HISTORY_ROOT / f"{user_id}.json"

    history = []

    if path.exists():
        try:
            history = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )
        except Exception:
            history = []

    snapshot = {
        "timestamp": _now(),
        "metrics": metrics,
    }

    history.append(snapshot)

    # Keep a bounded local history.
    history = history[-100:]

    path.write_text(
        json.dumps(
            history,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return snapshot


def get_history(user_id: int):
    path = HISTORY_ROOT / f"{user_id}.json"

    if not path.exists():
        return []

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return []


def calculate_trends(user_id: int):
    history = get_history(user_id)

    if len(history) < 2:
        return {
            "status": "insufficient_history",
            "snapshots": len(history),
            "trends": {},
        }

    previous = history[-2]["metrics"]
    current = history[-1]["metrics"]

    trends = {}

    keys = set(previous) | set(current)

    for key in keys:
        try:
            old = float(previous.get(key, 0))
            new = float(current.get(key, 0))

            trends[key] = {
                "previous": old,
                "current": new,
                "delta": new - old,
                "percent_change": (
                    ((new - old) / old) * 100
                    if old
                    else None
                ),
            }
        except Exception:
            continue

    return {
        "status": "ready",
        "snapshots": len(history),
        "trends": trends,
    }