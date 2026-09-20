from pathlib import Path


def test_required_project_components_exist():
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "app" / "main.py",
        root / "app" / "publishing" / "providers" / "youtube.py",
        root / "app" / "publishing" / "providers" / "instagram.py",
        root / "app" / "publishing" / "providers" / "tiktok.py",
        root / "app" / "publishing" / "providers" / "x.py",
        root / "app" / "services" / "voice" / "voice_service.py",
        root / "app" / "automation" / "openclaw_adapter.py",
    ]
    assert all(path.exists() for path in required)


def test_frontend_routes_exist():
    root = Path(__file__).resolve().parents[2]
    app = root / "frontend" / "src" / "App.jsx"
    text = app.read_text(encoding="utf-8")
    assert 'path="publishing"' in text
    assert 'path="daily"' in text
