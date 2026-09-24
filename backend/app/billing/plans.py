from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    monthly_usd: int
    yearly_usd: int
    monthly_videos: int
    monthly_clips: int
    monthly_messages: int | None
    monthly_email: int | None
    monthly_outlook: int | None
    monthly_instagram: int
    monthly_x: int
    monthly_tiktok: int
    youtube_min_minutes: int
    youtube_target_minutes: int
    description: str


PLANS = {
    "creator": Plan(
        "creator",
        "Creator",
        19,
        190,
        27,
        12,
        999,
        999,
        999,
        60,
        60,
        60,
        15,
        25,
        "For creators building a consistent publishing system.",
    ),
    "pro": Plan(
        "pro",
        "Pro",
        49,
        490,
        72,
        39,
        1999,
        1999,
        1999,
        180,
        180,
        180,
        15,
        25,
        "For serious creators running an automated content operation.",
    ),
    "studio": Plan(
        "studio",
        "Studio",
        129,
        1290,
        111,
        100,
        4499,
        4499,
        4499,
        360,
        360,
        360,
        15,
        25,
        "For high-volume creators and creator operations.",
    ),
}


COUPONS = {
    "creator": {
        "discount_percent": 50,
        "code_env": "N1MOX_CREATOR_COUPON",
    },
    "pro": {
        "discount_percent": 25,
        "code_env": "N1MOX_PRO_COUPON",
    },
    "studio": {
        "discount_percent": 42,
        "code_env": "N1MOX_STUDIO_COUPON",
    },
}


def public_plans():
    return [
        {
            "id": plan.id,
            "name": plan.name,
            "monthly_usd": plan.monthly_usd,
            "yearly_usd": plan.yearly_usd,
            "monthly_videos": plan.monthly_videos,
            "monthly_clips": plan.monthly_clips,
            "monthly_messages": plan.monthly_messages,
            "monthly_email": plan.monthly_email,
            "monthly_outlook": plan.monthly_outlook,
            "monthly_instagram": plan.monthly_instagram,
            "monthly_x": plan.monthly_x,
            "monthly_tiktok": plan.monthly_tiktok,
            "youtube_min_minutes": plan.youtube_min_minutes,
            "youtube_target_minutes": plan.youtube_target_minutes,
            "description": plan.description,
            "coupon_discount_percent": COUPONS[plan.id]["discount_percent"],
        }
        for plan in PLANS.values()
    ]
