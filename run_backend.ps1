$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\backend"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "N1MOX30 backend environment is missing. Run ..\setup.ps1 first."
}

& .\.venv\Scripts\python.exe run_migration.py
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
