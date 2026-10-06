$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$inferenceScript = Join-Path $projectRoot "inference-backend\start-inference.ps1"

function Test-InferenceService {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

if (-not (Test-Path -LiteralPath $inferenceScript)) {
    throw "Inference service files are missing. Check the inference-backend folder."
}

# The first run creates a virtual environment and installs the Python packages.
& $inferenceScript -PrepareOnly

if (-not (Test-InferenceService)) {
    Write-Host "Opening the research inference service..." -ForegroundColor Cyan
    Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$inferenceScript`""
    )
} else {
    Write-Host "A local inference service is already running." -ForegroundColor Green
}

Set-Location $projectRoot
$frontendDependencyMarker = Join-Path $projectRoot ".frontend-deps-ready"
$frontendCache = Join-Path $projectRoot ".npm-cache"
if (-not (Test-Path -LiteralPath $frontendDependencyMarker)) {
    Write-Host "Installing frontend dependencies (first run only)..." -ForegroundColor Cyan
    & npm ci --no-audit --no-fund --cache $frontendCache
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend dependency installation failed."
    }
    New-Item -ItemType File -Path $frontendDependencyMarker -Force | Out-Null
}

Write-Host "Starting the DR screening demo..." -ForegroundColor Green
& npm run dev
