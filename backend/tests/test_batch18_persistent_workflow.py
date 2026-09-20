from app.main import app
from app.core.database import SessionLocal
from app.services.batch18.persistent_workflow import (
    create_persistent_workflow,
    get_persistent_workflow,
    persistent_progress,
)


def test_batch18_imports():
    assert callable(create_persistent_workflow)
    assert callable(get_persistent_workflow)
    assert callable(persistent_progress)


def test_batch18_routes():
    paths = app.openapi()["paths"]

    assert "/platform/v8/workflows" in paths
    assert "/platform/v8/workflows/{workflow_id}" in paths
    assert "/platform/v8/workflows/{workflow_id}/progress" in paths


def test_batch18_database_persistence():
    db = SessionLocal()
    workflow = None

    try:
        workflow = create_persistent_workflow(
            db=db,
            user_id="batch18-test-user",
            topic="Persistent workflow test",
            stages=["research", "hooks"],
        )

        loaded = get_persistent_workflow(
            db,
            workflow.id,
            "batch18-test-user",
        )

        assert loaded is not None
        assert loaded.id == workflow.id
        assert loaded.topic == "Persistent workflow test"

        progress = persistent_progress(loaded)

        assert progress["completed"] == 0
        assert progress["total"] == 2
        assert progress["percent"] == 0

    finally:
        if workflow is not None:
            db.delete(workflow)
            db.commit()

        db.close()
