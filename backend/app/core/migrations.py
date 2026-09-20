from sqlalchemy import inspect, text

from app.core.database import engine


# =================================================
# DATABASE HELPERS
# =================================================

def table_exists(
    table_name: str,
) -> bool:
    """
    Return True when a database table exists.
    """
    inspector = inspect(engine)

    return table_name in inspector.get_table_names()


def create_table_if_missing(
    table_name: str,
    create_sql: str,
) -> None:
    """
    Create a table only when it does not exist.
    """
    if table_exists(table_name):
        print(
            f"[SKIP] {table_name} already exists."
        )
        return

    with engine.begin() as connection:
        connection.execute(
            text(create_sql)
        )

    print(
        f"[CREATED] {table_name}"
    )


def get_existing_columns(
    table_name: str,
) -> set[str]:
    """
    Return all existing columns for a table.
    """
    inspector = inspect(engine)

    columns = inspector.get_columns(
        table_name
    )

    return {
        column["name"]
        for column in columns
    }


def add_column_if_missing(
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    """
    Add a column only when it is missing.
    """
    if not table_exists(table_name):
        print(
            f"[SKIP] {table_name} does not exist."
        )
        return

    existing_columns = get_existing_columns(
        table_name
    )

    if column_name in existing_columns:
        print(
            f"[SKIP] {table_name}.{column_name} "
            "already exists."
        )
        return

    sql = (
        f"ALTER TABLE {table_name} "
        f"ADD COLUMN {column_name} "
        f"{column_definition}"
    )

    with engine.begin() as connection:
        connection.execute(
            text(sql)
        )

    print(
        f"[ADDED] {table_name}.{column_name}"
    )


# =================================================
# CREATOR MEMORY
# =================================================

def migrate_creator_memory_table() -> None:
    """
    Add missing Creator Memory fields.
    """
    if not table_exists("creator_memories"):
        print(
            "[SKIP] creator_memories does not exist."
        )
        return

    add_column_if_missing(
        table_name="creator_memories",
        column_name="confidence_score",
        column_definition=(
            "FLOAT NOT NULL DEFAULT 1.0"
        ),
    )


# =================================================
# PROJECTS
# =================================================

def migrate_projects_table() -> None:
    """
    Add project management columns.
    """
    if not table_exists("projects"):
        print(
            "[SKIP] projects does not exist."
        )
        return

    add_column_if_missing(
        table_name="projects",
        column_name="progress",
        column_definition=(
            "INTEGER NOT NULL DEFAULT 0"
        ),
    )

    add_column_if_missing(
        table_name="projects",
        column_name="workflow_count",
        column_definition=(
            "INTEGER NOT NULL DEFAULT 0"
        ),
    )

    add_column_if_missing(
        table_name="projects",
        column_name="completed_workflow_count",
        column_definition=(
            "INTEGER NOT NULL DEFAULT 0"
        ),
    )

    add_column_if_missing(
        table_name="projects",
        column_name="completed_at",
        column_definition="DATETIME",
    )


# =================================================
# AUTOMATION WORKFLOWS
# =================================================

def migrate_automation_workflows_table() -> None:
    """
    Add project relationship to automation workflows.
    """
    if not table_exists("automation_workflows"):
        print(
            "[SKIP] automation_workflows does not exist."
        )
        return

    add_column_if_missing(
        table_name="automation_workflows",
        column_name="project_id",
        column_definition="VARCHAR(36)",
    )


# =================================================
# PROJECT ACTIVITIES
# =================================================

def migrate_project_activities_table() -> None:
    """
    Create project activity table.
    """
    create_table_if_missing(
        table_name="project_activities",
        create_sql="""
        CREATE TABLE project_activities (
            id VARCHAR(36) PRIMARY KEY NOT NULL,
            project_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            activity_type VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            workflow_id VARCHAR(36),
            created_at DATETIME NOT NULL
        )
        """,
    )


# =================================================
# AI COMPLETIONS
# =================================================

def migrate_ai_completions_table() -> None:
    """
    Create AI completions table.
    """
    create_table_if_missing(
        table_name="ai_completions",
        create_sql="""
        CREATE TABLE ai_completions (
            id VARCHAR(36) PRIMARY KEY NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            generation_id VARCHAR(36),
            workflow_id VARCHAR(36),
            project_id VARCHAR(36),
            content_type VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            status VARCHAR(50) NOT NULL
                DEFAULT 'pending',
            rejection_reason TEXT,
            approved_at DATETIME,
            rejected_at DATETIME,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(generation_id)
                REFERENCES ai_generations(id),

            FOREIGN KEY(workflow_id)
                REFERENCES automation_workflows(id),

            FOREIGN KEY(project_id)
                REFERENCES projects(id)
        )
        """,
    )


# =================================================
# MEDIA ASSETS
# =================================================

def migrate_media_assets_table() -> None:
    """
    Create Media Asset table.
    """
    create_table_if_missing(
        table_name="media_assets",
        create_sql="""
        CREATE TABLE media_assets (
            id VARCHAR(36) PRIMARY KEY NOT NULL,

            user_id VARCHAR(36) NOT NULL,
            project_id VARCHAR(36),
            content_id VARCHAR(36),

            asset_type VARCHAR(50) NOT NULL,

            media_type VARCHAR(100)
                NOT NULL DEFAULT 'unknown',

            name VARCHAR(255) NOT NULL,
            description TEXT,
            original_filename VARCHAR(500),

            storage_provider VARCHAR(100)
                NOT NULL DEFAULT 'local',

            storage_path VARCHAR(1000),
            public_url VARCHAR(2000),
            provider_asset_id VARCHAR(500),

            mime_type VARCHAR(255),
            file_extension VARCHAR(50),
            file_size_bytes INTEGER,

            width INTEGER,
            height INTEGER,

            duration_seconds FLOAT,
            frame_rate FLOAT,

            scene_number INTEGER,
            asset_role VARCHAR(100),

            status VARCHAR(50)
                NOT NULL DEFAULT 'pending',

            retry_count INTEGER
                NOT NULL DEFAULT 0,

            max_retries INTEGER
                NOT NULL DEFAULT 3,

            error_message TEXT,
            metadata_json TEXT,

            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            processed_at DATETIME,

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(project_id)
                REFERENCES projects(id),

            FOREIGN KEY(content_id)
                REFERENCES content(id)
        )
        """,
    )


# =================================================
# VIDEO TIMELINES
# =================================================

def migrate_video_timelines_table() -> None:
    """
    Create the Video Timeline table.
    """
    create_table_if_missing(
        table_name="video_timelines",
        create_sql="""
        CREATE TABLE video_timelines (
            id VARCHAR(36) PRIMARY KEY NOT NULL,

            user_id VARCHAR(36) NOT NULL,
            content_id VARCHAR(36),

            name VARCHAR(255) NOT NULL
                DEFAULT 'Untitled Timeline',

            aspect_ratio VARCHAR(20) NOT NULL
                DEFAULT '16:9',

            width INTEGER NOT NULL
                DEFAULT 1920,

            height INTEGER NOT NULL
                DEFAULT 1080,

            duration_seconds FLOAT NOT NULL
                DEFAULT 0.0,

            fps INTEGER NOT NULL
                DEFAULT 30,

            background_color VARCHAR(20) NOT NULL
                DEFAULT '#000000',

            status VARCHAR(50) NOT NULL
                DEFAULT 'draft',

            version INTEGER NOT NULL
                DEFAULT 1,

            is_locked BOOLEAN NOT NULL
                DEFAULT 0,

            timeline_json TEXT NOT NULL
                DEFAULT '{}',

            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY(content_id)
                REFERENCES content(id)
                ON DELETE SET NULL
        )
        """,
    )


# =================================================
# THUMBNAILS
# =================================================

def migrate_thumbnails_table() -> None:
    """
    Create the Thumbnail table.
    """
    create_table_if_missing(
        table_name="thumbnails",
        create_sql="""
        CREATE TABLE thumbnails (
            id VARCHAR(36) PRIMARY KEY NOT NULL,

            user_id VARCHAR(36) NOT NULL,
            content_id VARCHAR(36),

            name VARCHAR(255) NOT NULL,

            platform VARCHAR(50) NOT NULL
                DEFAULT 'youtube',

            width INTEGER NOT NULL
                DEFAULT 1280,

            height INTEGER NOT NULL
                DEFAULT 720,

            title_text VARCHAR(500),

            concept TEXT,
            visual_direction TEXT,
            background_prompt TEXT,
            foreground_prompt TEXT,

            text_style VARCHAR(100),
            composition VARCHAR(100),

            curiosity_score FLOAT NOT NULL
                DEFAULT 0.0,

            readability_score FLOAT NOT NULL
                DEFAULT 0.0,

            visual_score FLOAT NOT NULL
                DEFAULT 0.0,

            ctr_score FLOAT NOT NULL
                DEFAULT 0.0,

            overall_score FLOAT NOT NULL
                DEFAULT 0.0,

            image_path TEXT,

            provider VARCHAR(100) NOT NULL
                DEFAULT 'local',

            status VARCHAR(50) NOT NULL
                DEFAULT 'planned',

            is_selected BOOLEAN NOT NULL
                DEFAULT 0,

            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(content_id)
                REFERENCES content(id)
        )
        """,
    )


# =================================================
# CREATOR PREFERENCES
# =================================================

def migrate_creator_preferences_table() -> None:
    """
    Create the structured Creator Preferences table.

    This stores persistent preferences used by
    N1MOX30 for personalization across AI generation,
    workflows, video creation, thumbnails, scheduling,
    voice, and approval behavior.
    """
    create_table_if_missing(
        table_name="creator_preferences",
        create_sql="""
        CREATE TABLE creator_preferences (
            id VARCHAR(36) PRIMARY KEY NOT NULL,

            user_id VARCHAR(36) NOT NULL UNIQUE,

            preferred_content_types TEXT,
            preferred_formats TEXT,
            preferred_topics TEXT,
            avoided_topics TEXT,

            preferred_tone VARCHAR(255),
            preferred_language VARCHAR(100),
            brand_voice TEXT,

            target_audience TEXT,
            audience_level VARCHAR(100),
            audience_interests TEXT,

            primary_platform VARCHAR(100),
            enabled_platforms TEXT,

            default_aspect_ratio VARCHAR(20)
                NOT NULL DEFAULT '16:9',

            default_video_style VARCHAR(255),
            default_caption_style VARCHAR(255),
            default_thumbnail_style VARCHAR(255),

            creativity_level INTEGER
                NOT NULL DEFAULT 70,

            research_depth INTEGER
                NOT NULL DEFAULT 70,

            personalization_level INTEGER
                NOT NULL DEFAULT 90,

            automation_level INTEGER
                NOT NULL DEFAULT 70,

            auto_generate_titles BOOLEAN
                NOT NULL DEFAULT 1,

            auto_generate_description BOOLEAN
                NOT NULL DEFAULT 1,

            auto_generate_hashtags BOOLEAN
                NOT NULL DEFAULT 1,

            auto_generate_thumbnail BOOLEAN
                NOT NULL DEFAULT 1,

            auto_generate_subtitles BOOLEAN
                NOT NULL DEFAULT 1,

            auto_quality_review BOOLEAN
                NOT NULL DEFAULT 1,

            require_publish_approval BOOLEAN
                NOT NULL DEFAULT 1,

            require_content_approval BOOLEAN
                NOT NULL DEFAULT 0,

            preferred_timezone VARCHAR(100),
            preferred_posting_times TEXT,

            preferred_voice_provider VARCHAR(100),
            preferred_voice_id VARCHAR(255),
            voice_style VARCHAR(255),

            notes TEXT,

            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
        """,
    )


# =================================================
# CONTENT VERSIONING
# =================================================

def migrate_content_versioning_table() -> None:
    """
    Add persistent versioning fields to content.
    """
    if not table_exists("content"):
        print(
            "[SKIP] content table does not exist."
        )
        return

    add_column_if_missing(
        table_name="content",
        column_name="current_version",
        column_definition=(
            "INTEGER NOT NULL DEFAULT 0"
        ),
    )

    add_column_if_missing(
        table_name="content",
        column_name="version_history",
        column_definition=(
            "TEXT NOT NULL DEFAULT '[]'"
        ),
    )


# =================================================
# RUN ALL MIGRATIONS
# =================================================

def run_migrations() -> None:
    """
    Run all safe N1MOX30 migrations.
    """

    print(
        "\n"
        "========================================"
    )

    print(
        "N1MOX30 DATABASE MIGRATION STARTED"
    )

    print(
        "========================================"
        "\n"
    )

    migrate_creator_memory_table()

    migrate_projects_table()

    migrate_automation_workflows_table()

    migrate_project_activities_table()

    migrate_ai_completions_table()

    migrate_media_assets_table()

    migrate_video_timelines_table()

    migrate_thumbnails_table()

    migrate_creator_preferences_table()

    migrate_content_versioning_table()

    print(
        "\n"
        "========================================"
    )

    print(
        "N1MOX30 DATABASE MIGRATION COMPLETED"
    )

    print(
        "========================================"
        "\n"
    )


# =================================================
# DIRECT EXECUTION
# =================================================

if __name__ == "__main__":
    run_migrations()