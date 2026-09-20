from app.main import app


def test_batch11_production_routes():
    paths = set(
        app.openapi().get(
            "paths",
            {},
        )
    )

    required = {
        "/platform/v2/security/status",
        "/platform/v2/providers/route",
        "/platform/v2/billing/checkout",
        "/platform/v2/billing/activate",
        "/platform/v2/billing/cancel",
        "/platform/v2/notifications",
        "/platform/v2/notifications/{notification_id}/read",
    }

    missing = required - paths

    assert not missing, (
        "Missing Batch 11 routes: "
        + ", ".join(sorted(missing))
    )


def test_batch11_application():
    assert app is not None
