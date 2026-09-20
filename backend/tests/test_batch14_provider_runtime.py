from app.main import app
from app.services.batch14.provider_runtime import (
    RuntimeResult,
    execute_runtime,
    execute_runtime_with_fallback,
)

def test_batch14_runtime_imports():
    assert RuntimeResult is not None
    assert callable(execute_runtime)
    assert callable(execute_runtime_with_fallback)

def test_batch14_runtime_route():
    assert "/platform/v4/runtime/execute" in app.openapi()["paths"]

def test_batch14_demo_runtime():
    result = execute_runtime("demo", "hello")
    assert result.success is True
    assert result.provider == "demo"
    assert "N1MOX30" in result.content

