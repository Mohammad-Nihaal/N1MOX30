"""Create a local N1MOX30 demo creator and starter context."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.creator_preferences import CreatorPreferences
from app.models.creator_profile import CreatorProfile
from app.services.creator_memory_service import CreatorMemoryService

EMAIL = "demo@n1mox30.local"
PASSWORD = "N1MOX30-Demo-2026!"


def main() -> None:
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == EMAIL).first()
        if user is None:
            user = User(email=EMAIL, password_hash=hash_password(PASSWORD), full_name="N1MOX Demo Creator", is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)

        profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == user.id).first()
        if profile is None:
            fields = {c.name for c in CreatorProfile.__table__.columns}
            data = {"user_id": user.id}
            for key, value in {
                "creator_name": "N1MOX Demo Creator",
                "niche": "AI and technology",
                "target_audience": "curious technology and creator audiences",
                "preferred_platforms": "youtube,instagram",
                "content_style": "modern documentary",
                "preferred_tone": "clear, energetic, intelligent",
            }.items():
                if key in fields:
                    data[key] = value
            db.add(CreatorProfile(**data))

        prefs = db.query(CreatorPreferences).filter(CreatorPreferences.user_id == user.id).first()
        if prefs is None:
            prefs = CreatorPreferences(
                user_id=user.id,
                preferred_content_types="educational,storytelling,explainer",
                preferred_formats="long-form,shorts",
                preferred_topics="AI,technology,automation,creator economy",
                preferred_tone="clear, energetic, intelligent",
                preferred_language="English",
                brand_voice="practical, confident, evidence-led",
                target_audience="curious technology and creator audiences",
                primary_platform="youtube",
                enabled_platforms="youtube,instagram",
                default_aspect_ratio="16:9",
                default_video_style="modern documentary",
                default_caption_style="clean high-contrast",
                default_thumbnail_style="bold curiosity",
                creativity_level=80,
                research_depth=85,
                personalization_level=95,
                automation_level=85,
                preferred_timezone="Asia/Kolkata",
                require_publish_approval=True,
            )
            db.add(prefs)
            db.commit()

        memory = CreatorMemoryService()
        existing = memory.search_memories(db=db, user_id=user.id, query="demo creator")
        if not existing:
            memory.learn_memory(
                db=db,
                user_id=user.id,
                memory_type="creator_preference",
                memory_key="demo_creator_focus",
                memory_value="Focus on AI, technology and creator automation content.",
                source="demo_seed",
                importance_score=0.8,
                confidence_score=1.0,
            )

        print("N1MOX30 DEMO USER READY")
        print(f"Email: {EMAIL}")
        print(f"Password: {PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
