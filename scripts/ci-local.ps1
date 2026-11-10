$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "== Sentinela CI local ==" -ForegroundColor Cyan
Write-Host "Stage: Backend tests"
Set-Location backend
python -m pip install -r requirements.txt
python -m pytest -q
Set-Location ..

Write-Host "Stage: Frontend build"
npm install
npm run build

Write-Host "Stage: Safety gate SIMULATE=true"
if ($env:SIMULATE -eq "false") { throw "Pipeline bloqueada" }
Write-Host "OK — pronto para demonstração." -ForegroundColor Green
