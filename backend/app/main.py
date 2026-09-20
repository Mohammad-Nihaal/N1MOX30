from app.api.production import router as production_router
from app.api.production_pipeline import router as batch21_production_router
from app.services.batch11.security_hardening import security_middleware
from app.api.platform_v2 import router as platform_v2_router
from app.api.publishing import router as publishing_router
from app.api.voice_workflow_control import router as voice_workflow_control_router
from app.api.wake_word import router as wake_word_router
from app.api.voice import router as voice_router
from app.api.voice_assistant import router as voice_assistant_router
from fastapi import FastAPI
from app.api.platform_v3 import router as platform_v3_router
from app.api.provider_execution import router as provider_execution_router
from app.api.provider_runtime import router as provider_runtime_router
from app.api.ai_pipeline import router as ai_pipeline_router
from app.api.creator_workflow import router as creator_workflow_router
from app.api.creator_orchestrator import router as creator_orchestrator_router
from app.api.persistent_workflows import router as persistent_workflows_router

from app.middleware.production_security import ProductionSecurityMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai import (
    router as ai_router,
)

from app.api.ai_completion import (
    router as ai_completion_router,
)

from app.api.analytics import (
    router as analytics_router,
)

from app.api.assistant import (
    router as assistant_router,
)

from app.api.auth import (
    router as auth_router,
)

from app.api.automation import (
    router as automation_router,
)

from app.api.connected_accounts import (
    router as connected_accounts_router,
)

from app.api.content import (
    router as content_router,
)

from app.api.content_review import (
    router as content_review_router,
)

from app.api.creator_memory import (
    router as creator_memory_router,
)

from app.api.creator_profile import (
    router as creator_profile_router,
)

from app.api.growth import (
    router as growth_router,
)

from app.api.insights import (
    router as insights_router,
)

from app.api.media_assets import (
    router as media_assets_router,
)

from app.api.oauth import (
    router as oauth_router,
)

from app.api.performance import (
    router as performance_router,
)

from app.api.personal_ai_assistant import (
    router as personal_ai_assistant_router,
)

from app.api.project_activities import (
    router as project_activities_router,
)

from app.api.project_dashboard import (
    router as project_dashboard_router,
)

from app.api.project_workflows import (
    router as project_workflows_router,
)
from app.api.project_workspace import (
    router as project_workspace_router,
)

from app.api.projects import (
    router as projects_router,
)

from app.api.research import (
    router as research_router,
)

from app.api.scheduler import (
    router as scheduler_router,
)

from app.api.schedules import (
    router as schedules_router,
)

from app.api.subtitles import (
    router as subtitles_router,
)

from app.api.thumbnails import (
    router as thumbnails_router,
)

from app.api.users import (
    router as users_router,
)

from app.api.video_render import (
    router as video_render_router,
)

from app.api.video_timelines import (
    router as video_timelines_router,
)

from app.api.youtube import (
    router as youtube_router,
)

from app.core.config import (
    settings,
)

from app.core.database import (
    engine,
)
from app.core.logging_config import configure_logging

configure_logging()

from app.models.base import (
    Base,
)

from app.services.scheduler_service import (
    scheduler,
    start_scheduler,
)
from app.api.creator_intelligence import (
    router as creator_intelligence_router,
)
from app.api.creator_preferences import (
    router as creator_preferences_router,
)
from app.api.central_workflow import (
    router as central_workflow_router,
)
from app.api.completion_confirmation import (
    router as completion_confirmation_router,
)
# Import all models before creating tables.
import app.models

from app.api.action_permissions import router as action_permissions_router

from app.api.quality_control import router as quality_control_router
from app.api.content_versions import router as content_versions_router
from app.api.error_recovery import router as error_recovery_router
from app.api.stt import router as stt_router
from app.api.voice_understanding import router as voice_understanding_router
from app.api.voice_response import router as voice_response_router
from app.api.voice_actions import router as voice_actions_router
from app.api.notifications import router as notifications_router
from app.api.daily_intelligence import router as daily_intelligence_router
from app.api.multi_publishing import router as multi_publishing_router
from app.api.system import router as system_router
from app.api.repurposing import router as repurposing_router
from app.api.daily_workspace import router as daily_workspace_router
from app.api.platform import router as platform_router
if settings.auto_create_tables:
    Base.metadata.create_all(
        bind=engine,
    )

from app.api.oauth import router as oauth_router

app = FastAPI(
    title=settings.app_name,
    description=(
        "N1MOX30 is an AI-powered creator assistant, "
        "automation, analytics, research, trend intelligence, "
        "long-term creator memory, personal AI assistance, "
        "project management, content management, subtitles, "
        "professional video creation, thumbnail generation, "
        "and final content quality review platform."
    ),
    version=settings.app_version,
)
# N1MOX30 OAuth direct route attachment
# OAuth router is already fully constructed with its /oauth prefix.
for _oauth_route in oauth_router.routes:
    if _oauth_route not in app.router.routes:
        app.router.routes.append(_oauth_route)

app.include_router(production_router)

app.include_router(batch21_production_router)


app.mount("/media", StaticFiles(directory="storage/media", check_dir=False), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# N1MOX30 YouTube OAuth routes

@app.on_event("startup")
def startup_event():
    start_scheduler()


@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()


# -------------------------------------------------
# Core
# -------------------------------------------------

app.middleware("http")(security_middleware)

app.include_router(
auth_router,
)

app.include_router(
    users_router,
)
app.include_router(platform_router)
app.include_router(platform_v2_router)
app.include_router(quality_control_router)

app.include_router(content_versions_router)

app.include_router(voice_response_router)
app.include_router(voice_actions_router)
app.include_router(notifications_router)
app.include_router(daily_intelligence_router)
app.include_router(multi_publishing_router)
app.include_router(system_router)
app.include_router(repurposing_router)
app.include_router(daily_workspace_router)
# -------------------------------------------------
# Creator Intelligence
# -------------------------------------------------

app.include_router(
    creator_profile_router,
)

app.include_router(
    creator_intelligence_router,
)

app.include_router(
    creator_memory_router,
)

app.include_router(
    personal_ai_assistant_router,
)

app.include_router(
    assistant_router,
)
app.include_router(
    creator_preferences_router,
)
app.include_router(
    central_workflow_router,
)
app.include_router(completion_confirmation_router)

app.include_router(action_permissions_router)

app.include_router(error_recovery_router)
app.include_router(stt_router)
app.include_router(voice_understanding_router)
app.include_router(wake_word_router)
# -------------------------------------------------
# Content / AI
# -------------------------------------------------

app.include_router(
    content_router,
)

app.include_router(
    ai_router,
)

app.include_router(
    ai_completion_router,
)


# -------------------------------------------------
# Research / Intelligence
# -------------------------------------------------

app.include_router(
    research_router,
)

app.include_router(
    insights_router,
)

app.include_router(
    growth_router,
)

app.include_router(
    analytics_router,
)

app.include_router(
    performance_router,
)


# -------------------------------------------------
# Connected Accounts / YouTube
# -------------------------------------------------

app.include_router(
    connected_accounts_router,
)

app.include_router(
    oauth_router,
)

app.include_router(
    youtube_router,
)


# -------------------------------------------------
# Projects / Workflows
# -------------------------------------------------

app.include_router(
    projects_router,
)

app.include_router(
    project_activities_router,
)

app.include_router(
    project_dashboard_router,
)

app.include_router(
    project_workflows_router,
)

app.include_router(
    project_workspace_router,
)

app.include_router(
    automation_router,
)


# -------------------------------------------------
# Scheduling
# -------------------------------------------------

app.include_router(
    schedules_router,
)

app.include_router(
    scheduler_router,
)


# -------------------------------------------------
# Media / Video Pipeline
# -------------------------------------------------

app.include_router(
    media_assets_router,
)

app.include_router(
    video_timelines_router,
)

app.include_router(
    video_render_router,
)

app.include_router(
    subtitles_router,
)

app.include_router(
    thumbnails_router,
)


# -------------------------------------------------
# Final Content Review
# -------------------------------------------------

app.include_router(
    content_review_router,
)


# -------------------------------------------------
# Root
# -------------------------------------------------

@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running",
        "message": "Welcome to the N1MOX30 API",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "N1MOX30 Backend",
        "version": settings.app_version,
        "database": "connected",
    }
app.include_router(voice_assistant_router)

app.include_router(voice_router)

app.include_router(voice_workflow_control_router)


app.include_router(publishing_router)



app.include_router(platform_v3_router)
app.include_router(provider_execution_router)
app.include_router(provider_runtime_router)
app.include_router(ai_pipeline_router)
app.include_router(creator_workflow_router)
app.include_router(creator_orchestrator_router)
app.include_router(persistent_workflows_router)












from app.api.creator_accounts import router as creator_accounts_router

app.include_router(creator_accounts_router)
from app.api.youtube_analytics import router as youtube_analytics_router
app.include_router(youtube_analytics_router)
from app.api.creator_os import router as creator_os_router
from app.api.creator_os_live import router as creator_os_live_router
from app.api.creator_operations import router as creator_operations_router
app.include_router(creator_os_router)
app.include_router(creator_os_live_router)
app.include_router(creator_operations_router)
from app.api.creator_insights import router as creator_insights_router
app.include_router(creator_insights_router)
from app.api.live_creator import router as live_creator_router
app.include_router(live_creator_router)
from app.api.creator_dashboard import router as creator_dashboard_router
from app.api.production_readiness import router as production_readiness_router
from app.api.youtube_oauth_real import router as youtube_oauth_real_router
from app.api.youtube_activation import router as youtube_activation_router
from app.api.creator_e2e import router as creator_e2e_router
from app.api.creator_e2e_report import router as creator_e2e_report_router
app.include_router(creator_dashboard_router)
app.include_router(production_readiness_router)
app.include_router(youtube_oauth_real_router)
app.include_router(youtube_activation_router)
app.include_router(creator_e2e_router)
app.include_router(creator_e2e_report_router)







