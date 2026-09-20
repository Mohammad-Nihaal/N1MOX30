$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "=== N1MOX30 START ===" -ForegroundColor Cyan

if (-not (Test-Path ".\backend\.venv\Scripts\python.exe") -or -not (Test-Path ".\frontend\node_modules")) {
    & powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\setup.ps1"
}

Start-Process powershell -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File',"$PSScriptRoot\run_backend.ps1"
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File',"$PSScriptRoot\run_frontend.ps1"

Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host "Frontend: http://127.0.0.1:5173" -ForegroundColor Gray
Write-Host "Swagger:  http://127.0.0.1:8000/docs" -ForegroundColor Gray
