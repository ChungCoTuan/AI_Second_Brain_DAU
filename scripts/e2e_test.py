"""Test end-to-end: upload PDF -> theo dõi SSE progress -> kiểm tra DB. Đo thời gian."""
import json
import os
import sys
import time

import requests

BASE = "http://127.0.0.1:8000/api/v1"
PDF = sys.argv[1] if len(sys.argv) > 1 else r"D:\AI_Second_Brain_DAU\backend\data\uploads\QCVQF.1982_KhungTrinhDoQuocGiaVietNam.pdf"

s = requests.Session()

# --- Login admin ---
r = s.post(f"{BASE}/auth/login", data={"username": "admin@dau.edu.vn", "password": "Dau@Second2026"},
           timeout=30)
if r.status_code != 200:
    # Thử tìm email admin trong DB
    print("LOGIN FAILED", r.status_code, r.text[:300])
    sys.exit(1)
print("Login OK")
token = r.json().get("access_token")
if not token:
    print("NO TOKEN:", r.text[:200]); sys.exit(1)
s.headers.update({"Authorization": f"Bearer {token}"})
print("Token OK")

# --- Subscribe SSE progress ---
events = []
def listen():
    try:
        with requests.get(f"{BASE}/system/stream", stream=True, timeout=180) as resp:
            for line in resp.iter_lines(decode_unicode=True):
                if line and line.startswith("data:"):
                    events.append(line[5:].strip())
    except Exception:
        pass

import threading
th = threading.Thread(target=listen, daemon=True)
th.start()
time.sleep(1)

# --- Upload ---
fname = os.path.basename(PDF)
t0 = time.perf_counter()
with open(PDF, "rb") as fh:
    r = s.post(f"{BASE}/documents/upload",
               files={"file": (fname, fh, "application/pdf")},
               data={"domain": "Giao_duc", "allow_external_ocr": "true"}, timeout=120)
print(f"UPLOAD HTTP {r.status_code} in {time.perf_counter()-t0:.2f}s: {r.text[:200]}")

# --- Wait for completion ---
deadline = time.perf_counter() + 300
printed = set()
while time.perf_counter() < deadline:
    for ev in list(events):
        if ev.startswith("progress:") and ev not in printed:
            printed.add(ev)
            parts = ev.split(":", 2)
            pct = parts[2].split(":", 1)[0] if len(parts) > 2 else ""
            step = parts[2].split(":", 1)[1] if len(parts) > 2 and ":" in parts[2] else ""
            print(f"  [{time.perf_counter()-t0:6.1f}s] {pct:>3}% - {step}")
    if any(e.startswith("success:") for e in events) or any(e.startswith("error:") for e in events):
        break
    time.sleep(0.3)

total = time.perf_counter() - t0
print(f"\n=== TỔNG THỜI GIAN: {total:.1f}s ===")
for e in events:
    if e.startswith(("success:", "error:")):
        print("KẾT QUẢ:", e)

# --- Verify DB ---
r = s.get(f"{BASE}/documents?page=1&limit=5", timeout=30)
print("DB docs total:", r.json().get("total"))
