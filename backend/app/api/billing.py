from fastapi import APIRouter

from app.billing.plans import public_plans

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans")
def get_public_plans():
    return {"currency": "USD", "plans": public_plans()}


@router.get("/status")
def billing_status():
    return {
        "provider_configured": False,
        "checkout_ready": False,
        "message": "Configure a verified payment provider before accepting live payments.",
    }