from datetime import datetime
import uuid

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UsageLedger(Base):
    """Monthly per-user entitlement usage.

    One row exists for each user/metric/billing-period combination.
    """

    __tablename__ = "usage_ledger"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "metric",
            "period_start",
            name="uq_usage_user_metric_period",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    metric: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
