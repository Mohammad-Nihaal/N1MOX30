from app.main import app
from app.services.batch17.orchestrator import (
    create_orchestration,
    get_orchestration,
    orchestration_progress,
)


def test_batch17_imports():
    assert callable(create_orchestration)
    assert callable(get_orchestration)
    assert callable(orchestration_progress)


def test_batch17_routes():
    paths = app.openapi()["paths"]

    assert "/platform/v7/orchestrator/create" in paths
    assert "/platform/v7/orchestrator/{workflow_id}" in paths
    assert "/platform/v7/orchestrator/{workflow_id}/progress" in paths
    assert "/platform/v7/orchestrator/{workflow_id}/run" in paths
    assert "/platform/v7/orchestrator/{workflow_id}/resume" in paths


def test_batch17_state_creation():
    state = create_orchestration(
        user_id="batch17-test-user",
        topic="N1MOX30 test",
        stages=["research", "hooks"],
    )

    assert state["status"] == "created"
    assert state["completed_stages"] == []
    assert state["stages"] == ["research", "hooks"]

    loaded = get_orchestration(
        state["workflow_id"],
        "batch17-test-user",
    )

    assert loaded is not None
    assert loaded["workflow_id"] == state["workflow_id"]

    progress = orchestration_progress(
        state["workflow_id"],
        "batch17-test-user",
    )

    assert progress["completed"] == 0
    assert progress["total"] == 2
    assert progress["percent"] == 0

