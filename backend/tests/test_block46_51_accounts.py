from pathlib import Path

from app.services.creator_accounts.manager import (
    create_connection,
    list_accounts,
)

from app.services.creator_accounts.youtube_oauth import (
    create_oauth_state,
    consume_oauth_state,
)

from app.services.creator_accounts.token_store import (
    save_token,
    load_token,
    delete_token,
)

from app.services.publishing.queue import (
    enqueue_publish,
    execute_publish_job,
)


def test_creator_account_connection():
    result = create_connection(
        user_id=987654,
        provider="youtube",
    )

    assert result["status"] == "created"
    assert result["account"]["provider"] == "youtube"

    accounts = list_accounts(987654)

    assert len(accounts["accounts"]) >= 1


def test_youtube_oauth_state_roundtrip():
    state = create_oauth_state(
        user_id=987655,
        account_id="acct_test_oauth",
    )

    assert state

    data = consume_oauth_state(state)

    assert data is not None
    assert data["user_id"] == 987655
    assert data["account_id"] == "acct_test_oauth"


def test_token_storage():
    account_id = "acct_token_test"

    token = {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
    }

    path = save_token(
        account_id,
        token,
    )

    assert Path(path).exists()

    loaded = load_token(account_id)

    assert loaded == token

    assert delete_token(account_id) is True


def test_publish_queue_authorization_boundary():
    job = enqueue_publish(
        user_id=987656,
        account_id="acct_publish_test",
        video_path="missing-video.mp4",
        metadata={
            "snippet": {
                "title": "N1MOX30 Test",
            }
        },
        max_attempts=2,
    )

    assert job["status"] == "queued"
    assert job["attempts"] == 0

    result = execute_publish_job(
        job,
        access_token=None,
    )

    assert result["status"] == "retry_pending"
    assert result["attempts"] == 1


def test_publish_queue_max_retry():
    job = enqueue_publish(
        user_id=987657,
        account_id="acct_retry_test",
        video_path="missing-video.mp4",
        metadata={},
        max_attempts=1,
    )

    result = execute_publish_job(
        job,
        access_token=None,
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 1