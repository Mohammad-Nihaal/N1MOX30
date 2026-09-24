from app.billing.plans import PLANS


def test_launch_plan_allowances_match_product_spec():
    assert PLANS["creator"].monthly_videos == 27
    assert PLANS["pro"].monthly_videos == 72
    assert PLANS["studio"].monthly_videos == 111
    assert PLANS["creator"].monthly_clips == 12
    assert PLANS["pro"].monthly_clips == 39
    assert PLANS["studio"].monthly_clips == 100
    assert PLANS["creator"].monthly_messages == 999
    assert PLANS["pro"].monthly_messages == 1999
    assert PLANS["studio"].monthly_messages == 4499
    assert PLANS["creator"].monthly_email == 999
    assert PLANS["pro"].monthly_email == 1999
    assert PLANS["studio"].monthly_email == 4499
    assert PLANS["creator"].monthly_outlook == 999
    assert PLANS["pro"].monthly_outlook == 1999
    assert PLANS["studio"].monthly_outlook == 4499
    assert (PLANS["creator"].youtube_min_minutes, PLANS["creator"].youtube_target_minutes) == (15, 25)
