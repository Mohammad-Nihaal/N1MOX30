from pathlib import Path

from app.services.creator_accounts.token_store import (
    save_token,
    load_token,
    delete_token,
)

from app.services.publishing.live_publish import (
    publish_to_youtube,
)


def test_live_token_boundary():
    account="acct_live_64"

    save_token(
        account,
        {
            "access_token":"test-token",
        },
    )

    token=load_token(account)

    assert token["access_token"]=="test-token"

    assert delete_token(account) is True


def test_publish_missing_video():
    result=publish_to_youtube(
        user_id=1,
        account_id="missing-account",
        video_path="missing-video.mp4",
        title="N1MOX30 Test",
    )

    assert result["status"]=="failed"


def test_publish_requires_authorization():
    path=Path("live_test_video.mp4")
    path.write_bytes(b"test")

    try:
        result=publish_to_youtube(
            user_id=1,
            account_id="no-token-account",
            video_path=str(path),
            title="N1MOX30 Test",
        )

        assert result["status"]=="authorization_required"
    finally:
        path.unlink(missing_ok=True)


def test_live_creator_api_import():
    from app.api.live_creator import router

    paths=[
        route.path
        for route in router.routes
    ]

    assert any(p.endswith("/youtube/{account_id}/channel") for p in paths)
    assert any(p.endswith("/youtube/{account_id}/videos") for p in paths)
    assert any(p.endswith("/youtube/{account_id}/analytics") for p in paths)
    assert any(p.endswith("/youtube/publish") for p in paths)