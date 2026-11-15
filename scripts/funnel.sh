#!/usr/bin/env bash
# Bat/Tat Tailscale Funnel cho DAU Second Brain (Phuong an 2).
#
#   ./scripts/funnel.sh on       # public http://127.0.0.1:5173 ra Internet
#   ./scripts/funnel.sh off      # tat
#   ./scripts/funnel.sh status   # xem trang thai + URL
#
# Luong duong dan:
#   Internet -> Tailscale Funnel (https://<machine>.<tailnet>.ts.net)
#            -> Vite :5173  (vite.config.ts da dat host: '0.0.0.0')
#            -> proxy /api -> FastAPI :8000 -> PostgreSQL local
#
# YEU CAU:
#   1. Da dang nhap Tailscale:  tailscale status
#   2. Da bat Funnel cho tailnet (mot lan): https://login.tailscale.com/f/funnel
#
# GHI CHU: nen dung chay bang Git Bash / WSL. Tren Windows PowerShell dung
#   .\scripts\funnel.ps1

set -euo pipefail

PORT="${PORT:-5173}"
TARGET="http://127.0.0.1:${PORT}"
ACTION="${1:-status}"

if ! command -v tailscale >/dev/null 2>&1; then
  if [ -x "/c/Program Files/Tailscale/tailscale.exe" ]; then
    TAILSCALE="/c/Program Files/Tailscale/tailscale.exe"
  else
    echo "[funnel] Khong tim thay tailscale. Cai dat: winget install --id Tailscale.Tailscale" >&2
    exit 1
  fi
else
  TAILSCALE="tailscale"
fi

case "$ACTION" in
  on)
    echo "[funnel] Public ${TARGET} ra Internet..."
    "$TAILSCALE" funnel --bg "$TARGET"
    echo ""
    "$TAILSCALE" funnel status || true
    echo ""
    echo "[funnel] Mo URL tren bang may khac (4G/5G) de kiem tra - KHONG mo tren cung may nay."
    ;;
  off)
    echo "[funnel] Dang tat funnel..."
    "$TAILSCALE" funnel --https=443 off
    ;;
  status)
    "$TAILSCALE" funnel status || true
    ;;
  *)
    echo "Usage: $0 {on|off|status}" >&2
    exit 1
    ;;
esac
