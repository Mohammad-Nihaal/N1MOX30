"""
N1MOX30 Database Migration Runner.

Convenience entry point for running the centralized
database migration system.
"""

from app.core.migrations import run_migrations


def main() -> None:
    run_migrations()


if __name__ == "__main__":
    main()
