# N1MOX30 Architecture

```text
React/Vite Frontend
        |
        v
FastAPI API Layer
        |
        +-- Auth / Users / Accounts
        +-- Creator Intelligence / Memory / Preferences
        +-- Personal Assistant / Voice
        +-- Projects / Central Workflow / Automation
        +-- Research / AI / Analytics / Growth
        +-- Media / Timeline / Video / Captions / Thumbnail
        +-- Quality / Permissions / Versioning / Recovery
        +-- Scheduling / Publishing / Multi-platform
        +-- Daily Intelligence / Notifications / System
        |
        v
Service + Provider Abstractions
        |
        +-- AI: Bedrock / OpenClaw / deterministic fallback
        +-- Voice: provider-neutral STT/TTS
        +-- Media: local / FFmpeg / image providers
        +-- Publishing: YouTube + demo adapters
        |
        v
SQLAlchemy / SQLite (local) or managed DB (production)
```

The central workflow is intentionally provider-neutral. A provider failure should be represented as a workflow state/error and handled through retries/fallbacks rather than an artificial N1MOX usage limit.
