$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."
python run_migration.py
python .\scripts\verify_installation.py
python -m compileall -q app
Write-Host "N1MOX30 FULL LOCAL CHECK: PASS" -ForegroundColor Green
