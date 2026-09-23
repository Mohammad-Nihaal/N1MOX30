from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    monthly_usd: int
    yearly_usd: int
    monthly_videos: int
    description: str


PLANS = {
    "creator": Plan(
        "creator",
        "Creator",
        19,
        190,
        27,
        "For creators building a consistent publishing system.",
    ),
    "pro": Plan(
        "pro",
        "Pro",
        49,
        490,
        72,
        "For serious creators running an automated content operation.",
    ),
    "studio": Plan(
        "studio",
        "Studio",
        129,
        1290,
        100,
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
            "description": plan.description,
            "coupon_discount_percent": COUPONS[plan.id]["discount_percent"],
        }
        for plan in PLANS.values()
    ]
