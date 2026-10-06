param(
    [switch]$PrepareOnly
)

$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    $systemPython = Get-Command python -ErrorAction SilentlyContinue
    if (-not $systemPython) {
        throw "Python was not found. Install Python 3.10 or newer and add it to PATH."
    }

    Write-Host "Creating the inference environment (first run only)..." -ForegroundColor Cyan
    & $systemPython.Source -m venv (Join-Path $projectRoot ".venv")
}

Write-Host "Checking inference dependencies..." -ForegroundColor Cyan
& $venvPython -m pip install --disable-pip-version-check -r (Join-Path $projectRoot "backend\requirements.txt")
if ($LASTEXITCODE -ne 0) {
    throw "Inference dependency installation failed."
}

if ($PrepareOnly) {
    return
}

Set-Location (Join-Path $projectRoot "backend")
Write-Host "Inference service started: http://127.0.0.1:8000" -ForegroundColor Green
& $venvPython -m uvicorn app.main:app --host 127.0.0.1 --port 8000
