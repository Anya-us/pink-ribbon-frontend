param(
    [switch]$PrepareOnly
)

$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    $systemPython = Get-Command python -ErrorAction SilentlyContinue
    if (-not $systemPython) {
        throw "未找到 Python。请先安装 Python 3.10 或更高版本，并勾选 Add Python to PATH。"
    }

    Write-Host "正在创建推理服务环境（首次运行只需一次）..." -ForegroundColor Cyan
    & $systemPython.Source -m venv (Join-Path $projectRoot ".venv")
}

Write-Host "正在检查推理服务依赖..." -ForegroundColor Cyan
& $venvPython -m pip install --disable-pip-version-check -r (Join-Path $projectRoot "backend\requirements.txt")
if ($LASTEXITCODE -ne 0) {
    throw "推理服务依赖安装失败。"
}

if ($PrepareOnly) {
    return
}

Set-Location (Join-Path $projectRoot "backend")
Write-Host "推理服务已启动：http://127.0.0.1:8000" -ForegroundColor Green
& $venvPython -m uvicorn app.main:app --host 127.0.0.1 --port 8000
