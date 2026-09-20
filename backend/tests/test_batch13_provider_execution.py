from app.main import app
from app.services.batch13.provider_execution import execute_provider, execute_with_fallback

def test_batch13_imports():
    assert callable(execute_provider)
    assert callable(execute_with_fallback)

def test_batch13_route():
    assert "/platform/v4/providers/execute" in app.openapi()["paths"]
