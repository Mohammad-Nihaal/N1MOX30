
from app.main import app
from app.services.batch12.ai_gateway import gateway_status


def test_batch12_gateway_status():
    result = gateway_status()
    assert result["status"] == "ready"
    assert result["provider_routing"] is True
    assert result["quota_layer"] is True


def test_batch12_routes():
    paths = app.openapi()["paths"]
    assert "/platform/v3/ai/status" in paths
    assert "/platform/v3/ai/authorize" in paths


def test_batch12_audit_function_exists():
    from app.services.batch12.ai_gateway import audit_ai_generation
    assert callable(audit_ai_generation)


def test_batch12_usage_function_exists():
    from app.services.batch12.ai_gateway import record_provider_usage
    assert callable(record_provider_usage)
