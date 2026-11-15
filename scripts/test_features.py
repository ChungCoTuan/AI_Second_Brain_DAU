"""Kiem tra cac tinh nang khac: gioi han trang, search, chat, analytics."""
import sys
import time

import requests

BASE = "http://127.0.0.1:8000/api/v1"
s = requests.Session()

r = s.post(f"{BASE}/auth/login", data={"username": "admin@dau.edu.vn", "password": "Dau@Second2026"}, timeout=30)
token = r.json()["access_token"]
s.headers.update({"Authorization": f"Bearer {token}"})
print("1. LOGIN: OK")

# 2. Upload file vuot gioi han 105 trang -> phai bi tu choi 400
pdf = r"D:\AI_Second_Brain_DAU\backend\data\uploads\TEST_OVERLIMIT_105.pdf"
with open(pdf, "rb") as fh:
    r = s.post(f"{BASE}/documents/upload",
               files={"file": ("TEST_OVERLIMIT_105.pdf", fh, "application/pdf")},
               data={"domain": "Giao_duc"}, timeout=120)
print(f"2. UPLOAD 105 trang: HTTP {r.status_code}")
print(f"   -> {r.json().get('detail')}")

# 3. Upload trung ten -> phai bi tu choi
with open(pdf, "rb") as fh:
    r = s.post(f"{BASE}/documents/upload",
               files={"file": ("TEST_OVERLIMIT_105.pdf", fh, "application/pdf")},
               data={"domain": "Giao_duc"}, timeout=120)
print(f"3. UPLOAD trung ten: HTTP {r.status_code} -> {str(r.json().get('detail'))[:80]}")

# 4. Danh sach van ban
r = s.get(f"{BASE}/documents?page=1&limit=5", timeout=30)
d = r.json()
total = d.get("total") if isinstance(d, dict) else len(d)
print(f"4. DANH SACH van ban: total={total}")

# 5. Search semantic
t0 = time.perf_counter()
r = s.get(f"{BASE}/search", params={"q": "tuyen sinh", "page": 1, "limit": 5}, timeout=60)
print(f"5. SEARCH: HTTP {r.status_code} trong {time.perf_counter()-t0:.2f}s")
if r.status_code == 200:
    res = r.json()
    items = res.get("results") or res.get("items") or res.get("data") or []
    print(f"   -> total={res.get('total')} items={len(items)}")
    for it in items[:3]:
        print(f"      - {str(it.get('soHieu') or it.get('vb'))[:60]}")

# 6. Analytics / dashboard
for ep in ["/analytics/stats", "/analytics/overview", "/topics", "/legal-data"]:
    try:
        r = s.get(f"{BASE}{ep}", timeout=20)
        print(f"6. {ep}: HTTP {r.status_code}")
    except Exception as e:
        print(f"6. {ep}: {type(e).__name__}")

# 7. Chat (RAG)
try:
    t0 = time.perf_counter()
    r = s.post(f"{BASE}/chat", json={"query": "Quy che tuyen sinh 2026 quy dinh gi gi?"}, timeout=180)
    print(f"7. CHAT: HTTP {r.status_code} trong {time.perf_counter()-t0:.2f}s")
    if r.status_code == 200:
        print(f"   -> {str(r.json())[:250]}")
    else:
        print(f"   -> {r.text[:250]}")
except Exception as e:
    print(f"7. CHAT: {type(e).__name__}: {str(e)[:150]}")

# 8. SSE stream
try:
    r = s.get(f"{BASE}/system/stream", stream=True, timeout=8)
    print(f"8. SSE stream: HTTP {r.status_code} (OK)")
except Exception as e:
    print(f"8. SSE stream: {type(e).__name__}")
