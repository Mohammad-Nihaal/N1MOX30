from app.main import app
from app.services.batch16.creator_workflow import (
    CREATOR_STAGES,
    CreatorWorkflowResult,
    run_creator_stage,
    run_creator_workflow,
)


def test_batch16_workflow_imports():
    assert CreatorWorkflowResult is not None
    assert callable(run_creator_stage)
    assert callable(run_creator_workflow)


def test_batch16_stage_count():
    assert len(CREATOR_STAGES) == 11


def test_batch16_routes():
    paths = app.openapi()["paths"]
    assert "/platform/v6/creator/stages" in paths
    assert "/platform/v6/creator/stage" in paths
    assert "/platform/v6/creator/workflow" in paths

