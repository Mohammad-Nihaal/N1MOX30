def generate_content_strategy(
    ranked_videos: list[dict],
    growth_score_result: dict,
) -> dict:
    """Generate a data-driven YouTube content strategy."""

    if not ranked_videos:
        return {
            "strategy_level": "insufficient_data",
            "summary": (
                "Not enough video data is available yet. "
                "Publish more videos to generate a personalized strategy."
            ),
            "recommended_actions": [
                "Publish consistently.",
                "Test different content topics.",
                "Track views and engagement.",
            ],
            "top_content_patterns": [],
        }

    top_videos = ranked_videos[:3]

    top_content_patterns = []

    for index, video in enumerate(top_videos, start=1):
        top_content_patterns.append(
            {
                "rank": index,
                "title": video.get("title"),
                "views": video.get("views", 0),
                "likes": video.get("likes", 0),
                "comments": video.get("comments", 0),
                "engagement_rate": video.get(
                    "engagement_rate",
                    0,
                ),
            }
        )

    growth_score = growth_score_result.get(
        "growth_score",
        0,
    )

    recommended_actions = []

    if growth_score < 40:
        strategy_level = "foundation"

        summary = (
            "Your channel is in the foundation stage. "
            "Focus on consistency, discoverability, and improving "
            "the performance of each video."
        )

        recommended_actions.extend(
            [
                "Publish consistently on a realistic schedule.",
                "Study your best-performing videos and repeat successful ideas.",
                "Improve titles and thumbnails to increase discoverability.",
                "Focus on one or two clear content niches.",
            ]
        )

    elif growth_score < 70:
        strategy_level = "growth"

        summary = (
            "Your channel has positive growth potential. "
            "Focus on scaling successful topics and testing "
            "new content variations."
        )

        recommended_actions.extend(
            [
                "Create follow-up videos related to your best-performing topics.",
                "Test new formats while keeping successful themes.",
                "Improve audience interaction using questions and calls to action.",
                "Compare new videos against your recent top performers.",
            ]
        )

    else:
        strategy_level = "scale"

        summary = (
            "Your channel shows strong growth indicators. "
            "Focus on scaling successful content while experimenting "
            "carefully with new opportunities."
        )

        recommended_actions.extend(
            [
                "Produce more content around your strongest-performing topics.",
                "Create content series to encourage returning viewers.",
                "Experiment with new formats without abandoning successful content.",
                "Focus on increasing audience loyalty and engagement.",
            ]
        )

    best_video = ranked_videos[0]

    next_content_idea = {
        "based_on_video": best_video.get("title"),
        "recommendation": (
            "Create a follow-up, deeper explanation, updated version, "
            "or related video inspired by your best-performing content."
        ),
    }

    return {
        "strategy_level": strategy_level,
        "growth_score": growth_score,
        "summary": summary,
        "best_content_reference": {
            "title": best_video.get("title"),
            "views": best_video.get("views", 0),
            "engagement_rate": best_video.get(
                "engagement_rate",
                0,
            ),
        },
        "top_content_patterns": top_content_patterns,
        "recommended_actions": recommended_actions,
        "next_content_idea": next_content_idea,
    }