$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "Sentinela — subindo API + console React" -ForegroundColor Cyan

if (-not (Test-Path "backend\.venv")) {
  python -m venv backend\.venv
}
& backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
npm install

$env:SIMULATE = "true"
$env:CONFIRM_EXECUTE = "false"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 2
npm run dev
