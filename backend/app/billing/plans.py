from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    monthly_usd: int
    description: str


PLANS = {
    "creator": Plan("creator", "Creator", 19, "For creators building a consistent publishing system."),
    "pro": Plan("pro", "Pro", 49, "For serious creators running an automated content operation."),
    "studio": Plan("studio", "Studio", 129, "For teams and high-volume creator operations."),
}


def public_plans():
    return [
        {
            "id": plan.id,
            "name": plan.name,
            "monthly_usd": plan.monthly_usd,
            "description": plan.description,
        }
        for plan in PLANS.values()
    ]