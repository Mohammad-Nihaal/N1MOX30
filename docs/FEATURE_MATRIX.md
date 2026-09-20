# N1MOX30 Master Feature Matrix

This matrix maps the locked master flow to the shipped implementation. **Demo mode means the feature works locally without paid/external credentials; real provider actions remain credential-gated.**

| Area | Shipped implementation |
|---|---|
| Backend/Auth/DB | FastAPI + SQLAlchemy + JWT + SQLite |
| Accounts/YouTube | Connected accounts + Google/YouTube OAuth foundation |
| Analytics/Scheduler | YouTube analytics, snapshots, APScheduler |
| Research/AI Studio | Research services, AI generation/history/reuse/delete, provider router and deterministic fallbacks |
| Creator Intelligence | Creator intelligence service/API |
| Preferences | Persistent creator preferences with context API |
| Long-term Memory | Learn/search/context/deactivate/reactivate |
| Personal AI Assistant | Context + message APIs and assistant conversation/memory services |
| Central Workflow | 13-stage orchestration engine |
| Projects | Project CRUD, dashboards, workflow attachment and activity timeline |
| Automation | Research → strategy → hooks → script → voice → visuals → video → captions → thumbnail → metadata → QC → scheduling → publishing |
| Completion/Permissions | Completion confirmation + action permission/approval APIs |
| Versioning/Recovery | Content versions, compare/restore, error recovery and activity logs |
| Voice | Wake word, STT abstraction, intent understanding, natural responses, real actions and workflow control |
| Media | Asset service, timeline engine, FFmpeg renderer, subtitle generation, Pillow thumbnails |
| Publishing | Provider-neutral service + YouTube uploader + safe demo mode |
| Scheduling | Content schedule persistence + intelligent scheduling service |
| Multi-platform | Provider-neutral coordinator for YouTube, Instagram, TikTok, Facebook and X; demo adapters included |
| Performance/Growth | Performance insights, analytics decisions, growth score/recommendations and strategy |
| Daily Intelligence | Active/failed/completed work, upcoming publishing, unread notifications and next actions |
| Notifications | Persistent notification API and read/unread management |
| Settings | Creator preferences cover AI, voice, workflow, scheduling and approval controls |
| Unified readiness | `/system/readiness` reports database, workflow stages and external-provider configuration |
| UX | React/Vite app, dashboard shell, auth, analytics, research, AI Studio, assistant, schedules and accounts |
| Reliability | Migrations, retries, workflow recovery, health endpoints and verification scripts |
| Security | JWT authentication, authenticated resource access, environment-based secrets |
| Deployment | Local startup scripts + production-oriented configuration foundation |
| E2E readiness | Seed data, full local verification and deterministic demo fallbacks |

## External credential boundary

The archive cannot contain your private Google/YouTube, OpenAI, AWS, or other provider credentials. Add them to `backend/.env` when you want real external actions. N1MOX30 should never pretend a demo/simulated operation was actually published.


## Final Test3 launch pack additions
- Multi-platform OAuth: YouTube, Instagram, TikTok, X
- Real provider dispatch for YouTube, Instagram, TikTok and X
- Cross-platform analytics snapshot endpoints
- Unified Publishing Center
- PWA manifest
- Expo Android/iOS/web client
- Production Docker baseline
