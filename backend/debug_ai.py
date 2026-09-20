from app.services.ai_service import generate_ai_text

result = generate_ai_text(
    prompt="""You are N1MOX30's content generation engine.

Generate creator content directly.

Your entire response MUST contain ONLY these four sections:

TITLES:
1. Why AI Is Changing Content Creation in 2026
2. How AI Is Transforming YouTube
3. The AI Creator Revolution
4. AI's New Role in Content Creation
5. What Creators Need to Know About AI

SCRIPT:
AI is changing content creation faster than ever. In 2026, creators can use AI to research ideas, develop scripts, create visuals, and streamline publishing. But the biggest change is not that AI replaces creativity. It gives creators more time to focus on their unique voice, storytelling, and ideas.

CAPTION:
AI is transforming the creator workflow in 2026. The tools are getting faster, but your creativity and unique voice still matter most.

HASHTAGS:
#AIContentCreation #CreatorEconomy #AIForCreators #YouTube #N1MOX30""",
    temperature=0.7,
)

print("TYPE:", type(result))
print("RESULT:")
print(repr(result))
