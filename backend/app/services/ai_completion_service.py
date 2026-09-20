from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.ai_completion import AICompletion


class AICompletionService:
    """
    Central service layer for AI completion confirmation.

    Responsibilities:
    - create AI completion records
    - prevent duplicate generation completions
    - retrieve user completions
    - approve AI completions
    - reject AI completions
    - manage completion status transitions
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create_completion(
        self,
        user_id: str,
        generation_id: str | None,
        workflow_id: str | None,
        project_id: str | None,
        content_type: str,
        title: str,
        content: str,
    ) -> AICompletion:
        """
        Create a new AI completion awaiting confirmation.

        If the completion belongs to an AI generation,
        return the existing completion instead of creating
        a duplicate record.
        """

        if generation_id is not None:

            existing_completion = (
                self.db.query(AICompletion)
                .filter(
                    AICompletion.generation_id
                    == generation_id,
                    AICompletion.user_id
                    == user_id,
                )
                .first()
            )

            if existing_completion is not None:
                return existing_completion

        completion = AICompletion(
            user_id=user_id,
            generation_id=generation_id,
            workflow_id=workflow_id,
            project_id=project_id,
            content_type=content_type,
            title=title,
            content=content,
            status="pending",
        )

        self.db.add(completion)
        self.db.commit()
        self.db.refresh(completion)

        return completion

    def get_completion(
        self,
        completion_id: str,
        user_id: str,
    ) -> AICompletion | None:
        """
        Return one AI completion belonging to the user.
        """

        return (
            self.db.query(AICompletion)
            .filter(
                AICompletion.id == completion_id,
                AICompletion.user_id == user_id,
            )
            .first()
        )

    def get_completion_by_generation(
        self,
        generation_id: str,
        user_id: str,
    ) -> AICompletion | None:
        """
        Return the AI completion connected
        to one AI generation.
        """

        return (
            self.db.query(AICompletion)
            .filter(
                AICompletion.generation_id
                == generation_id,
                AICompletion.user_id
                == user_id,
            )
            .first()
        )

    def get_completions(
        self,
        user_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[AICompletion]:
        """
        Return AI completions belonging to the user.
        """

        limit = max(
            1,
            min(limit, 500),
        )

        query = (
            self.db.query(AICompletion)
            .filter(
                AICompletion.user_id == user_id,
            )
        )

        if status is not None:
            query = query.filter(
                AICompletion.status == status,
            )

        return (
            query
            .order_by(
                AICompletion.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

    def approve_completion(
        self,
        completion_id: str,
        user_id: str,
    ) -> AICompletion:
        """
        Approve a pending AI completion.
        """

        completion = self.get_completion(
            completion_id=completion_id,
            user_id=user_id,
        )

        if completion is None:
            raise ValueError(
                "AI completion not found."
            )

        if completion.status == "approved":
            return completion

        if completion.status == "rejected":
            raise ValueError(
                "Rejected AI completion cannot be approved."
            )

        if completion.status != "pending":
            raise ValueError(
                "AI completion cannot be approved "
                "from its current status."
            )

        completion.status = "approved"

        completion.approved_at = (
            datetime.utcnow()
        )

        completion.rejected_at = None

        completion.rejection_reason = None

        self.db.commit()

        self.db.refresh(completion)

        return completion

    def reject_completion(
        self,
        completion_id: str,
        user_id: str,
        rejection_reason: str | None = None,
    ) -> AICompletion:
        """
        Reject a pending AI completion.
        """

        completion = self.get_completion(
            completion_id=completion_id,
            user_id=user_id,
        )

        if completion is None:
            raise ValueError(
                "AI completion not found."
            )

        if completion.status == "rejected":
            return completion

        if completion.status == "approved":
            raise ValueError(
                "Approved AI completion cannot "
                "be rejected."
            )

        if completion.status != "pending":
            raise ValueError(
                "AI completion cannot be rejected "
                "from its current status."
            )

        completion.status = "rejected"

        completion.rejected_at = (
            datetime.utcnow()
        )

        completion.approved_at = None

        completion.rejection_reason = (
            rejection_reason
        )

        self.db.commit()

        self.db.refresh(completion)

        return completion