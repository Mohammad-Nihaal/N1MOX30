from app.main import app
from app.services.batch15.ai_pipeline import PipelineResult, run_ai_pipeline


def test_batch15_pipeline_imports():
    assert PipelineResult is not None
    assert callable(run_ai_pipeline)


def test_batch15_pipeline_route():
    assert "/platform/v5/ai/generate" in app.openapi()["paths"]

