from __future__ import annotations

from sqlalchemy import inspect, text

from app.core.database import engine


def table_exists(
    table_name: str,
) -> bool:
    """
    Return True when a database table already exists.
    """

    inspector = inspect(engine)

    return table_name in inspector.get_table_names()


def create_table_if_missing(
    table_name: str,
    create_sql: str,
) -> None:
    """
    Create a table only when it does not already exist.
    """

    if table_exists(table_name):
        print(
            f"[SKIP] {table_name} already exists."
        )
        return

    with engine.begin() as connection:
        connection.execute(
            text(create_sql),
        )

    print(
        f"[CREATED] {table_name}"
    )


def get_existing_columns(
    table_name: str,
) -> set[str]:
    """
    Return all existing column names
    for a database table.
    """

    inspector = inspect(engine)

    columns = inspector.get_columns(
        table_name,
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
    Add a column only when it does not
    already exist.
    """

    existing_columns = get_existing_columns(
        table_name,
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
            text(sql),
        )

    print(
        f"[ADDED] {table_name}.{column_name}"
    )


def migrate_projects_table() -> None:
    """
    Add Project Management columns.
    """

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


def migrate_automation_workflows_table() -> None:
    """
    Add Project relationship column
    to automation workflows.
    """

    add_column_if_missing(
        table_name="automation_workflows",
        column_name="project_id",
        column_definition="VARCHAR(36)",
    )


def migrate_project_activities_table() -> None:
    """
    Create the Project Activity timeline table
    when it does not already exist.
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


def migrate_ai_completions_table() -> None:
    """
    Create the AI completions table
    when it does not already exist.
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
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            rejection_reason TEXT,
            approved_at DATETIME,
            rejected_at DATETIME,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(generation_id)
                REFERENCES ai_generations(id),
            FOREIGN KEY(workflow_id)
                REFERENCES automation_workflows(id),
            FOREIGN KEY(project_id)
                REFERENCES projects(id)
        )
        """,
    )


def run_migrations() -> None:
    """
    Run all safe N1MOX30 database migrations.
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

    migrate_projects_table()

    migrate_automation_workflows_table()

    migrate_project_activities_table()

    migrate_ai_completions_table()

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


if __name__ == "__main__":

    run_migrations()