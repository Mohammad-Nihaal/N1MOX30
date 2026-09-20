"""Local N1MOX30 verification without network calls."""
from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
sys.path.insert(0, str(ROOT))

errors: list[str] = []
python_files = list(APP.rglob("*.py"))
for path in python_files:
    try:
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    except Exception as exc:
        errors.append(f"syntax: {path}: {exc}")

if errors:
    print("N1MOX30 VERIFY: FAIL")
    print("\n".join(errors))
    raise SystemExit(1)

from app.automation.registry import stage_registry
from app.core.database import engine
from sqlalchemy import inspect

stages = [item.stage.value for item in stage_registry.all()]
tables = inspect(engine).get_table_names()
print("N1MOX30 VERIFY: PASS")
print(f"Python files checked: {len(python_files)}")
print(f"Workflow stages: {len(stages)}")
print("Stages:", ", ".join(stages))
print(f"Database tables: {len(tables)}")
print("Database:", engine.url)
