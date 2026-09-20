$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "=== N1MOX30 COMPLETE SETUP ===" -ForegroundColor Cyan

if (-not (Test-Path ".\backend\.venv\Scripts\python.exe")) {
    py -m venv .\backend\.venv
}
& .\backend\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\backend\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt

if (-not (Test-Path ".\backend\.env")) {
    Copy-Item .\backend\.env.example .\backend\.env
}
& .\backend\.venv\Scripts\python.exe .\backend\run_migration.py

Set-Location .\frontend
npm install
if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed." }
npm run build
if ($LASTEXITCODE -ne 0) { throw "Frontend production build failed." }
Set-Location $PSScriptRoot

Write-Host "=== N1MOX30 SETUP COMPLETE ===" -ForegroundColor Green
Write-Host "Run .\start_n1mox30.ps1 to start the web app." -ForegroundColor Cyan
Write-Host "Mobile client: cd .\mobile ; npm install ; npx expo start" -ForegroundColor Cyan
