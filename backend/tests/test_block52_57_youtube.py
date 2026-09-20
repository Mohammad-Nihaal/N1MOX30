from pathlib import Path

from app.services.youtube.channel_sync import (
    save_channel_videos,
    get_channel_videos,
)

from app.services.publishing.tracking import (
    record_publish_result,
    get_publish_result,
    list_publish_results,
)

from app.services.analytics.youtube_analytics import (
    build_channel_analytics,
    build_video_analytics,
)


def test_channel_video_storage():
    result = save_channel_videos(
        "acct_test_52",
        [
            {
                "video_id": "vid_001",
                "title": "N1MOX30 Test",
                "view_count": 100,
                "like_count": 10,
                "comment_count": 2,
            }
        ],
    )

    assert result["account_id"] == "acct_test_52"

    loaded = get_channel_videos("acct_test_52")

    assert loaded["videos"][0]["video_id"] == "vid_001"


def test_publish_tracking():
    result = record_publish_result(
        publish_job_id="job_52_test",
        account_id="acct_test_52",
        result={
            "status": "published",
            "video_id": "youtube123",
            "attempts": 1,
        },
        metadata={
            "snippet": {
                "title": "N1MOX30 Test"
            }
        },
    )

    assert result["status"] == "published"
    assert result["video_url"].endswith("youtube123")

    loaded = get_publish_result("job_52_test")

    assert loaded["video_id"] == "youtube123"

    listing = list_publish_results("acct_test_52")

    assert listing["count"] >= 1


def test_channel_analytics():
    result = build_channel_analytics(
        {
            "channel_id": "channel123",
            "title": "N1MOX30",
            "subscriber_count": 1000,
            "view_count": 50000,
            "video_count": 10,
        }
    )

    assert result["subscribers"] == 1000
    assert result["views"] == 50000
    assert result["average_views_per_video"] == 5000


def test_video_analytics():
    result = build_video_analytics(
        {
            "video_id": "vid123",
            "title": "N1MOX30",
            "view_count": 1000,
            "like_count": 100,
            "comment_count": 20,
        }
    )

    assert result["views"] == 1000
    assert result["likes"] == 100
    assert result["comments"] == 20
    assert result["engagement_rate"] == 12.0