# Bat/Tat Tailscale Funnel cho DAU Second Brain (Phuong an 2).
#
#   .\scripts\funnel.ps1 on       # public http://127.0.0.1:5173 ra Internet
#   .\scripts\funnel.ps1 off      # tat
#   .\scripts\funnel.ps1 status   # xem trang thai + URL
#
# Luong duong dan:
#   Internet -> Tailscale Funnel (https://<machine>.<tailnet>.ts.net)
#            -> Vite :5173  (vite.config.ts da dat host: '0.0.0.0')
#            -> proxy /api -> FastAPI :8000 -> PostgreSQL local
#
# YEU CAU:
#   1. Da dang nhap Tailscale
#   2. Da bat Funnel cho tailnet (mot lan): https://login.tailscale.com/f/funnel

$ErrorActionPreference = "Continue"
$Port = if ($env:PORT) { $env:PORT } else { "5173" }
$Target = "http://127.0.0.1:$Port"
$Action = if ($args.Count -ge 1) { $args[0] } else { "status" }

$TailScaleExe = "C:\Program Files\Tailscale\tailscale.exe"
if (-not (Test-Path $TailScaleExe)) {
    $cmd = Get-Command tailscale -ErrorAction SilentlyContinue
    if ($cmd) { $TailScaleExe = $cmd.Source }
    else {
        Write-Host "[funnel] Khong tim thay tailscale. Cai dat: winget install --id Tailscale.Tailscale" -ForegroundColor Red
        exit 1
    }
}

switch ($Action) {
    "on" {
        Write-Host "[funnel] Public $Target ra Internet..." -ForegroundColor Cyan
        & $TailScaleExe funnel --bg $Target
        Write-Host ""
        & $TailScaleExe funnel status
        Write-Host ""
        Write-Host "[funnel] Mo URL tren bang may khac (4G/5G) de kiem tra." -ForegroundColor Yellow
    }
    "off" {
        Write-Host "[funnel] Dang tat funnel..." -ForegroundColor Cyan
        & $TailScaleExe funnel --https=443 off
    }
    "status" {
        & $TailScaleExe funnel status
    }
    default {
        Write-Host "Usage: .\scripts\funnel.ps1 {on|off|status}" -ForegroundColor Red
        exit 1
    }
}
