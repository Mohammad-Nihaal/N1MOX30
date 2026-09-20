from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.connected_account import ConnectedAccount
from app.models.user import User
from app.schemas.connected_account import (
    ConnectedAccountCreate,
    ConnectedAccountResponse,
)


router = APIRouter(
    prefix="/connected-accounts",
    tags=["Connected Accounts"],
)


@router.post(
    "/",
    response_model=ConnectedAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_connected_account(
    account_data: ConnectedAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == current_user.id,
            ConnectedAccount.platform == account_data.platform,
            ConnectedAccount.platform_account_id
            == account_data.platform_account_id,
        )
        .first()
    )

    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account is already connected.",
        )

    account = ConnectedAccount(
        user_id=current_user.id,
        platform=account_data.platform,
        platform_account_id=account_data.platform_account_id,
        account_name=account_data.account_name,
        is_active=True,
        is_authorized=False,
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@router.get(
    "/",
    response_model=list[ConnectedAccountResponse],
)
def get_my_connected_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.user_id == current_user.id,
        )
        .order_by(
            ConnectedAccount.created_at.desc(),
        )
        .all()
    )


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def disconnect_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.id == account_id,
            ConnectedAccount.user_id == current_user.id,
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connected account not found.",
        )

    db.delete(account)
    db.commit()

    return None