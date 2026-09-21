from app.services.hooks.hook_service import HookService


def test_hook_v2_generates_desire_and_character_hooks():
    service = HookService()

    result = service.generate_hooks(
        topic="AI creator automation",
        platform="instagram_reels",
        command="help creators grow faster",
        research={
            "findings": [
                "Creators spend significant time on repetitive production tasks."
            ]
        },
        strategy={
            "strategy": {
                "audience_promise": "grow your audience without doing everything manually",
                "target_audience": "a creator trying to grow",
                "content_angle": "automation removes repetitive creator work",
            }
        },
    )

    assert result["engine_version"] == "2.0"
    assert len(result["hooks"]) >= 7

    hook_types = {
        item["type"]
        for item in result["hooks"]
    }

    assert "desire" in hook_types
    assert "character_desire" in hook_types
    assert result["recommended_hook"]["hook"]


def test_hook_v2_scores_are_bounded():
    service = HookService()

    result = service.generate_hooks(
        topic="creator growth",
        platform="youtube_shorts",
        command="grow faster",
        research={},
        strategy={},
    )

    assert result["hooks"]

    for item in result["hooks"]:
        assert 0 <= item["score"] <= 100
        assert isinstance(item["score_breakdown"], dict)


def test_hook_v2_avoids_generic_ai_openers():
    service = HookService()

    result = service.generate_hooks(
        topic="creator automation",
        platform="instagram",
        command="grow",
        research={},
        strategy={},
    )

    banned = (
        "you won't believe",
        "this changes everything",
        "did you know",
    )

    for item in result["hooks"]:
        text = item["hook"].lower()
        assert not any(
            phrase in text
            for phrase in banned
        )


def test_hook_v2_preserves_downstream_contract():
    service = HookService()

    result = service.generate_hooks(
        topic="AI video creation",
        platform="youtube",
        research={"findings": ["automation can reduce repetitive work"]},
        strategy={"strategy": {"audience_promise": "create faster"}},
    )

    assert "topic" in result
    assert "platform" in result
    assert "command" in result
    assert "hooks" in result
    assert "recommended_hook" in result
    assert "scoring" in result
    assert result["hook_status"] == "generated"
