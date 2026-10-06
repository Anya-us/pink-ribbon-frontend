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
    throw "未找到内置推理服务，请确认 inference-backend 文件夹完整。"
}

# The first run creates a virtual environment and installs the Python packages.
& $inferenceScript -PrepareOnly

if (-not (Test-InferenceService)) {
    Write-Host "正在打开研究推理服务窗口..." -ForegroundColor Cyan
    Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$inferenceScript`""
    )
} else {
    Write-Host "检测到本机推理服务已在运行。" -ForegroundColor Green
}

Set-Location $projectRoot
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot "node_modules"))) {
    Write-Host "正在安装前端依赖（首次运行只需一次）..." -ForegroundColor Cyan
    & npm ci
    if ($LASTEXITCODE -ne 0) {
        throw "前端依赖安装失败。"
    }
}

Write-Host "正在启动糖网诊疗演示平台..." -ForegroundColor Green
& npm run dev
