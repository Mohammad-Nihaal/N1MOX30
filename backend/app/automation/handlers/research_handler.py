from __future__ import annotations

from typing import Any

from app.services.research.research_service import ResearchService


class ResearchStageHandler:
    """
    Concrete N1MOX30 workflow handler for the research stage.

    The workflow engine provides a standard payload. This handler extracts
    the workflow information and delegates the actual research operation
    to ResearchService.
    """

    def __init__(
        self,
        research_service: ResearchService | None = None,
    ) -> None:
        self.research_service = research_service or ResearchService()

    def __call__(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        workflow = payload.get("workflow", {})

        topic = str(workflow.get("topic", "")).strip()
        platform = str(
            workflow.get("platform", "youtube")
        ).strip().lower()
        command = str(
            workflow.get("command", "")
        ).strip()

        if not topic:
            raise ValueError(
                "Research stage requires a workflow topic."
            )

        result = self.research_service.research(
            topic=topic,
            platform=platform,
            command=command,
        )

        return {
            "stage": "research",
            "status": "completed",
            "execution": "research_service",
            "research": result,
        }


research_stage_handler = ResearchStageHandler()