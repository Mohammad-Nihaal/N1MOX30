from app.services.creator_dashboard.service import (
    build_creator_dashboard,
)


def test_dashboard_requires_authorization():
    result=build_creator_dashboard(
        987654321
    )

    assert result["status"]=="authorization_required"
    assert result["channel"] is None
    assert "growth" in result
    assert "publishing" in result


def test_dashboard_service_shape():
    result=build_creator_dashboard(
        987654322
    )

    assert "user_id" in result
    assert "videos" in result
    assert "analytics" in result
    assert "growth" in result
    assert "publishing" in result


def test_dashboard_api_import():
    from app.api.creator_dashboard import router

    paths=[
        route.path
        for route in router.routes
    ]

    assert any(
        p.endswith("/{user_id}")
        for p in paths
    )

    assert any(
        p.endswith("/{user_id}/summary")
        for p in paths
    )


def test_frontend_dashboard_api_exists():
    from pathlib import Path

    root=Path(__file__).resolve().parents[1]
    path=(
        root.parent /
        "frontend" /
        "src" /
        "api" /
        "creatorDashboard.js"
    )

    assert path.exists()


def test_creator_intelligence_component_exists():
    from pathlib import Path

    root=Path(__file__).resolve().parents[1]
    path=(
        root.parent /
        "frontend" /
        "src" /
        "components" /
        "CreatorIntelligencePanel.jsx"
    )

    assert path.exists()