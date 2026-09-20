from __future__ import annotations

from typing import Any

from app.services.script.script_service import ScriptService


class ScriptStageHandler:
    """
    Automation handler for the N1MOX30 Script stage.

    Consumes:
        - Research output
        - Strategy output
        - Hooks output

    Produces:
        - Structured production-ready script output
    """

    def __init__(self, script_service: ScriptService | None = None):
        self.script_service = script_service or ScriptService()

    def __call__(self, payload: dict[str, Any]) -> dict[str, Any]:
        workflow = payload.get("workflow", {})

        topic = str(workflow.get("topic", "")).strip()
        platform = str(workflow.get("platform", "youtube")).strip().lower()
        command = str(workflow.get("command", "")).strip()

        if not topic:
            raise ValueError("Script stage requires a workflow topic.")

        previous_outputs = payload.get("previous_outputs", {})

        research_output = previous_outputs.get("research", {})
        strategy_output = previous_outputs.get("strategy", {})
        hooks_output = previous_outputs.get("hooks", {})

        if not research_output:
            raise ValueError("Script stage requires completed research output.")

        if not strategy_output:
            raise ValueError("Script stage requires completed strategy output.")

        if not hooks_output:
            raise ValueError("Script stage requires completed hooks output.")

        result = self.script_service.generate_script(
            topic=topic,
            platform=platform,
            command=command,
            research=research_output,
            strategy=strategy_output,
            hooks=hooks_output,
        )

        return {
            "stage": "script",
            "status": "completed",
            "execution": "script_service",
            "script": result,
        }


script_stage_handler = ScriptStageHandler()