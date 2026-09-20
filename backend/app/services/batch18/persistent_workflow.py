import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.creator_workflow_state import CreatorWorkflowState
from app.services.batch16.creator_workflow import CREATOR_STAGES


def create_persistent_workflow(
    db: Session,
    user_id: str,
    topic: str,
    stages=None,
    provider=None,
):
    selected = stages or list(CREATOR_STAGES)

    invalid = [x for x in selected if x not in CREATOR_STAGES]
    if invalid:
        raise ValueError(f"Unsupported stages: {invalid}")

    workflow = CreatorWorkflowState(
        user_id=str(user_id),
        topic=topic,
        provider=provider,
        status="created",
        stages_json=json.dumps(selected),
        completed_stages_json="[]",
        results_json="{}",
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow


def get_persistent_workflow(
    db: Session,
    workflow_id: str,
    user_id: str,
):
    return (
        db.query(CreatorWorkflowState)
        .filter(
            CreatorWorkflowState.id == workflow_id,
            CreatorWorkflowState.user_id == str(user_id),
        )
        .first()
    )


def workflow_to_dict(workflow):
    if not workflow:
        return None

    stages = json.loads(workflow.stages_json or "[]")
    completed = json.loads(workflow.completed_stages_json or "[]")
    results = json.loads(workflow.results_json or "{}")

    return {
        "workflow_id": workflow.id,
        "user_id": workflow.user_id,
        "topic": workflow.topic,
        "provider": workflow.provider,
        "status": workflow.status,
        "current_stage": workflow.current_stage,
        "failed_stage": workflow.failed_stage,
        "stages": stages,
        "completed_stages": completed,
        "results": results,
        "created_at": workflow.created_at.isoformat(),
        "updated_at": workflow.updated_at.isoformat(),
    }


def update_persistent_workflow(
    db: Session,
    workflow,
    *,
    status=None,
    current_stage=None,
    failed_stage=None,
    completed_stages=None,
    results=None,
):
    if status is not None:
        workflow.status = status

    if current_stage is not None:
        workflow.current_stage = current_stage

    if failed_stage is not None:
        workflow.failed_stage = failed_stage

    if completed_stages is not None:
        workflow.completed_stages_json = json.dumps(
            completed_stages
        )

    if results is not None:
        workflow.results_json = json.dumps(
            results,
            ensure_ascii=False,
        )

    workflow.updated_at = datetime.utcnow()

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow


def persistent_progress(workflow):
    stages = json.loads(workflow.stages_json or "[]")
    completed = json.loads(workflow.completed_stages_json or "[]")

    total = len(stages)
    done = len(completed)

    return {
        "workflow_id": workflow.id,
        "status": workflow.status,
        "current_stage": workflow.current_stage,
        "failed_stage": workflow.failed_stage,
        "completed": done,
        "total": total,
        "percent": round((done / total) * 100, 2) if total else 100,
    }
