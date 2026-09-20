import json
import os
import uuid
from datetime import datetime
from threading import Lock

from app.services.batch16.creator_workflow import CREATOR_STAGES, run_creator_stage


STATE_DIR = os.path.join("storage", "orchestrator")
STATE_FILE = os.path.join(STATE_DIR, "creator_workflows.json")
_lock = Lock()


def _load():
    os.makedirs(STATE_DIR, exist_ok=True)
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, STATE_FILE)


def create_orchestration(user_id, topic, stages=None, provider=None):
    selected = stages or list(CREATOR_STAGES)

    invalid = [x for x in selected if x not in CREATOR_STAGES]
    if invalid:
        raise ValueError(f"Unsupported stages: {invalid}")

    workflow_id = str(uuid.uuid4())

    state = {
        "workflow_id": workflow_id,
        "user_id": str(user_id),
        "topic": topic,
        "provider": provider,
        "status": "created",
        "current_stage": None,
        "completed_stages": [],
        "failed_stage": None,
        "stages": selected,
        "results": {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    with _lock:
        data = _load()
        data[workflow_id] = state
        _save(data)

    return state


def get_orchestration(workflow_id, user_id=None):
    with _lock:
        state = _load().get(workflow_id)

    if not state:
        return None

    if user_id is not None and str(state["user_id"]) != str(user_id):
        return None

    return state


def _update(workflow_id, **changes):
    with _lock:
        data = _load()
        state = data.get(workflow_id)

        if not state:
            return None

        state.update(changes)
        state["updated_at"] = datetime.utcnow().isoformat()

        data[workflow_id] = state
        _save(data)

        return state


def run_orchestration(db, workflow_id, user_id):
    state = get_orchestration(workflow_id, user_id)

    if not state:
        raise ValueError("Workflow not found")

    if state["status"] == "completed":
        return state

    if state["status"] == "running":
        return state

    completed = set(state.get("completed_stages", []))
    stages = state["stages"]

    _update(
        workflow_id,
        status="running",
        failed_stage=None,
    )

    for stage in stages:
        if stage in completed:
            continue

        _update(
            workflow_id,
            current_stage=stage,
            status="running",
        )

        prompt = (
            f"N1MOX30 production creator workflow.\n"
            f"Topic: {state['topic']}\n"
            f"Current stage: {stage}\n"
            f"Generate production-ready output for this stage."
        )

        result = run_creator_stage(
            db=db,
            user_id=user_id,
            stage=stage,
            prompt=prompt,
            provider=state.get("provider"),
            estimated_units=1,
        )

        if not result.success:
            return _update(
                workflow_id,
                status="failed",
                failed_stage=stage,
                current_stage=stage,
                results={
                    **state.get("results", {}),
                    stage: {
                        "success": False,
                        "provider": result.provider,
                        "error": result.error,
                    },
                },
            )

        current = get_orchestration(workflow_id, user_id)

        completed = list(current.get("completed_stages", []))
        if stage not in completed:
            completed.append(stage)

        results = dict(current.get("results", {}))
        results[stage] = {
            "success": True,
            "provider": result.provider,
            "content": result.content,
            "generation_id": result.generation_id,
            "usage_recorded": result.usage_recorded,
            "fallback_used": result.fallback_used,
        }

        _update(
            workflow_id,
            completed_stages=completed,
            results=results,
            current_stage=stage,
            status="running",
        )

    return _update(
        workflow_id,
        status="completed",
        current_stage=None,
        failed_stage=None,
    )


def resume_orchestration(db, workflow_id, user_id):
    state = get_orchestration(workflow_id, user_id)

    if not state:
        raise ValueError("Workflow not found")

    if state["status"] == "completed":
        return state

    return run_orchestration(
        db=db,
        workflow_id=workflow_id,
        user_id=user_id,
    )


def orchestration_progress(workflow_id, user_id):
    state = get_orchestration(workflow_id, user_id)

    if not state:
        return None

    total = len(state["stages"])
    completed = len(state.get("completed_stages", []))

    return {
        "workflow_id": workflow_id,
        "status": state["status"],
        "current_stage": state.get("current_stage"),
        "failed_stage": state.get("failed_stage"),
        "completed": completed,
        "total": total,
        "percent": round((completed / total) * 100, 2) if total else 100,
    }

