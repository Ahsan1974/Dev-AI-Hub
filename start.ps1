# DevAI Hub - one-command local start (Windows PowerShell)
# Usage:  .\start.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"
$VenvPip = Join-Path $Backend ".venv\Scripts\pip.exe"

Write-Host ""
Write-Host "DevAI Hub - starting..." -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $VenvPython)) {
  Write-Host "Creating Python virtualenv..." -ForegroundColor Yellow
  Push-Location $Backend
  python -m venv .venv
  Pop-Location
}

Write-Host "Ensuring backend dependencies..." -ForegroundColor Yellow
& $VenvPip install -q -r (Join-Path $Backend "requirements.txt")

$EnvFile = Join-Path $Backend ".env"
$EnvExample = Join-Path $Backend ".env.example"
if (-not (Test-Path $EnvFile) -and (Test-Path $EnvExample)) {
  Copy-Item $EnvExample $EnvFile
  Write-Host "Created backend\.env from .env.example" -ForegroundColor Yellow
}

Write-Host "Seeding database (safe to re-run)..." -ForegroundColor Yellow
Push-Location $Backend
& $VenvPython -m app.seed
if ($LASTEXITCODE -ne 0) {
  Pop-Location
  throw "Database seed failed. Fix the error above and run .\start.ps1 again."
}
Pop-Location

if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
  Write-Host "Installing frontend packages (npm install)..." -ForegroundColor Yellow
  Push-Location $Frontend
  npm install
  Pop-Location
}

function Stop-Port([int]$Port) {
  $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  foreach ($c in $conns) {
    try {
      Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
      Write-Host "Freed port $Port (pid $($c.OwningProcess))" -ForegroundColor DarkYellow
    } catch {}
  }
}
Stop-Port 8000
Stop-Port 5173

# On Windows, `npm` is usually npm.cmd (or a PowerShell shim). Start-Process
# cannot launch the .ps1 shim, so resolve npm.cmd explicitly.
$npmCmd = $null
foreach ($name in @("npm.cmd", "npm.exe", "npm")) {
  $found = Get-Command $name -ErrorAction SilentlyContinue
  if ($found -and $found.Source -and ($found.Source -notlike "*.ps1")) {
    $npmCmd = $found.Source
    break
  }
}
if (-not $npmCmd) {
  throw "npm was not found on PATH. Install Node.js, then run .\start.ps1 again."
}

Write-Host ""
Write-Host "API:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "App:  http://localhost:5173" -ForegroundColor Green
Write-Host "Press Ctrl+C in this window to stop both." -ForegroundColor DarkGray
Write-Host ""

$apiArgs = @("-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000")
$uiArgs = @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173")

$api = Start-Process -FilePath $VenvPython -ArgumentList $apiArgs -WorkingDirectory $Backend -PassThru -NoNewWindow
$ui = Start-Process -FilePath $npmCmd -ArgumentList $uiArgs -WorkingDirectory $Frontend -PassThru -NoNewWindow

try {
  Wait-Process -Id $api.Id, $ui.Id
} finally {
  foreach ($proc in @($api, $ui)) {
    if ($proc -and -not $proc.HasExited) {
      Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
