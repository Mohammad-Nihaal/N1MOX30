from pathlib import Path

from app.services.voice.assistant import (
    execute_voice_command,
    understand_command,
)


def test_voice_create_command():
    result = execute_voice_command(
        user_id=1,
        text="Hey N1MOX create a video about AI automation",
    )

    assert result["status"] == "completed"
    assert result["action"] in ("create_content", "start_pipeline")
    assert result["command"]["topic"]


def test_voice_status_command():
    result = execute_voice_command(
        user_id=1,
        text="Hey N1MOX what is the workflow status",
        workflow_state={
            "completed_stages": ["research", "strategy", "hooks"],
            "total_stages": 13,
        },
    )

    assert result["status"] == "completed"
    assert result["action"] == "check_status"
    assert "3 of 13" in result["message"]


def test_voice_schedule_publish_stop():
    schedule = understand_command("schedule this video for tomorrow")
    publish = understand_command("publish this video now")
    stop = understand_command("stop the workflow")

    assert schedule["intent"] == "schedule"
    assert publish["intent"] == "publish"
    assert stop["intent"] == "stop"


def test_voice_artifact():
    result = execute_voice_command(
        user_id=1,
        text="create content about creator automation",
    )

    from app.services.voice.assistant import save_voice_command

    artifact = save_voice_command(result)

    assert Path(artifact).exists()