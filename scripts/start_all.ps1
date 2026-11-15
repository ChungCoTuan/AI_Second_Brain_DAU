# Khởi động toàn bộ DAU Second Brain (Phương án 2 - chạy trên máy cá nhân).
# Dùng khi: .\scripts\start_all.ps1
#
# Thứ tự: PostgreSQL -> Backend (FastAPI :8000) -> Frontend (Vite :5173) -> Tailscale Funnel
# Funnel public frontend ra Internet qua https://<machine>.<tailnet>.ts.net
$ErrorActionPreference = "Continue"
$Root = "D:\AI_Second_Brain_DAU"
$funnelUrl = ""

# --- 1. PostgreSQL ---
$pgData = "C:\Program Files\PostgreSQL\18\data"
$pgBin = "C:\Program Files\PostgreSQL\18\bin"
if (-not (Get-NetTCPConnection -LocalPort 5432 -State Listen -ErrorAction SilentlyContinue)) {
    Write-Host "[1/4] Khoi dong PostgreSQL 18..." -ForegroundColor Cyan
    & "$pgBin\pg_ctl.exe" -D $pgData -l "$pgData\log\manual.log" start | Out-Null
    Start-Sleep -Seconds 8
} else {
    Write-Host "[1/4] PostgreSQL 18 da chay." -ForegroundColor Green
}

# --- 2. Backend ---
if (-not (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)) {
    Write-Host "[2/4] Khoi dong backend (uvicorn :8000)..." -ForegroundColor Cyan
    Get-Process python -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -like "$Root\backend\*" } |
        ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2

    $env:HF_HOME = "$Root\backend\data\models"
    $env:OMP_NUM_THREADS = "4"
    $env:MKL_NUM_THREADS = "4"
    $env:PATH = "$Root\backend\bin\poppler\Library\bin;$env:PATH"

    Start-Process -FilePath "$Root\backend\.venv\Scripts\python.exe" `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" `
        -WorkingDirectory "$Root\backend" `
        -RedirectStandardOutput "$Root\backend\backend.log" `
        -RedirectStandardError "$Root\backend\backend.err.log" `
        -WindowStyle Hidden
    Start-Sleep -Seconds 25
} else {
    Write-Host "[2/4] Backend da chay tren :8000." -ForegroundColor Green
}

# --- 3. Frontend ---
if (-not (Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue)) {
    Write-Host "[3/4] Khoi dong frontend (vite :5173)..." -ForegroundColor Cyan
    Get-Process node -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2

    # Dung cmd.exe de `npm` (file npm.cmd) chay duoc khi Start-Process khong co shell.
    Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/c", "npm run dev > frontend.log 2> frontend.err.log" `
        -WorkingDirectory "$Root\frontend" `
        -WindowStyle Hidden
    Start-Sleep -Seconds 12
} else {
    Write-Host "[3/4] Frontend da chay tren :5173." -ForegroundColor Green
}

# --- 4. Tailscale Funnel (public ra Internet) ---
$TailScaleExe = "C:\Program Files\Tailscale\tailscale.exe"
if (Test-Path $TailScaleExe) {
    $tsState = (& $TailScaleExe status 2>&1 | Out-String)
    if ($tsState -match "Logged out") {
        Write-Host "[4/4] Tailscale CHUA DANG NHAP - bo qua Funnel." -ForegroundColor Yellow
        Write-Host "      Dang nhap tai: https://login.tailscale.com" -ForegroundColor Yellow
    } else {
        & $TailScaleExe funnel --bg http://127.0.0.1:5173 2>&1 | Out-Null
        $funnelStatus = (& $TailScaleExe funnel status 2>&1 | Out-String)
        if ($funnelStatus -match "(https://[A-Za-z0-9\.\-]+\.ts\.net)") { $funnelUrl = $Matches[1] }
        Write-Host "[4/4] Tailscale Funnel: ON" -ForegroundColor Green
        if ($funnelUrl) { Write-Host "      URL public: $funnelUrl" -ForegroundColor Green }
    }
} else {
    Write-Host "[4/4] Chua cai Tailscale - bo qua Funnel." -ForegroundColor Yellow
}

# --- Kiem tra ---
try {
    $api = (Invoke-WebRequest http://127.0.0.1:8000/ -UseBasicParsing -TimeoutSec 10).Content
    Write-Host "  Backend: $api" -ForegroundColor Green
} catch { Write-Host "  Backend CHUA PING duoc: $($_.Exception.Message)" -ForegroundColor Red }
try {
    (Invoke-WebRequest http://127.0.0.1:5173/ -UseBasicParsing -TimeoutSec 10).StatusCode | Out-Null
    Write-Host "  Frontend: OK" -ForegroundColor Green
} catch { Write-Host "  Frontend CHUA PING duoc: $($_.Exception.Message)" -ForegroundColor Red }

Write-Host ""
if ($funnelUrl) {
    Write-Host "  PUBLIC URL: $funnelUrl" -ForegroundColor Yellow
    Write-Host "  (mo tren may khac / 4G de kiem tra)" -ForegroundColor DarkGray
}
Write-Host "  API local : http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "  Frontend : http://127.0.0.1:5173" -ForegroundColor Yellow
Write-Host "  Tai khoan: admin@dau.edu.vn / Dau@Second2026" -ForegroundColor Yellow
