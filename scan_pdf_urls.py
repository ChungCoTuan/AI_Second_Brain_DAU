"""Script quet datafiles.chinhphu.vn de tim TAT CA file PDF Thong tu va Quyet dinh giao duc.
Toi uu: dung concurrent requests de quet nhanh hon."""

import requests
import urllib3
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

urllib3.disable_warnings()
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

found_docs = []

def check_url(year, month, num, suffix, doc_type):
    """Kiem tra 1 URL co tra ve PDF hay khong."""
    if suffix.startswith("bgd"):
        url = f"https://datafiles.chinhphu.vn/cpp/files/vbpq/{year}/{month:02d}/{num:02d}-{suffix}"
    else:
        # QD: so khong pad zero
        url = f"https://datafiles.chinhphu.vn/cpp/files/vbpq/{year}/{month:02d}/{num}-{suffix}"
    try:
        r = requests.head(url, verify=False, timeout=3, headers=HEADERS)
        if r.status_code == 200 and "pdf" in r.headers.get("content-type", "").lower():
            return {"year": year, "month": month, "num": num, "url": url, "type": doc_type}
    except:
        pass
    return None

# === QUET THONG TU BGDDT ===
print("=" * 60)
print("QUET THONG TU BO GIAO DUC (TT-BGDDT) 2013-2024")
print("=" * 60)

tt_tasks = []
for year in range(2013, 2025):
    for month in range(1, 13):
        for num in range(1, 50):
            for suffix in ["bgddt.signed.pdf", "bgddt.pdf", "bgd.signed.pdf"]:
                tt_tasks.append((year, month, num, suffix, "thong_tu"))

print(f"Tong so URL can quet: {len(tt_tasks)} (dung 20 luong song song)...")

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(check_url, *t): t for t in tt_tasks}
    for future in as_completed(futures):
        result = future.result()
        if result:
            found_docs.append(result)
            print(f"  [OK] TT {result['num']:02d}/{result['year']} thang {result['month']:02d} -> {result['url']}")

# === QUET QUYET DINH TTg & BGDDT ===
print("\n" + "=" * 60)
print("QUET QUYET DINH THU TUONG & BO GD (QD-TTg, QD-BGDDT) 2013-2024")
print("=" * 60)

qd_tasks = []
for year in range(2013, 2025):
    for month in range(1, 13):
        # QD Thu tuong: thu cac so pho bien
        for num in [69, 89, 117, 131, 433, 468, 522, 789, 1002, 1258, 1609, 1665, 1719, 1982, 2068, 2222, 2500, 2626, 3000, 3450, 3500, 4000, 4500, 5000, 5500]:
            for suffix in ["ttg.signed.pdf", "ttg.pdf"]:
                qd_tasks.append((year, month, num, suffix, "quyet_dinh_ttg"))
        # QD Bo GD
        for num in [69, 89, 117, 131, 433, 468, 522, 789, 1002, 1258, 1609, 1665, 1719, 2068, 2222, 2500, 2626, 3000, 3450, 3500, 4000, 4500, 5000, 5500]:
            for suffix in ["bgddt.signed.pdf", "bgddt.pdf"]:
                qd_tasks.append((year, month, num, suffix, "quyet_dinh_bgddt"))

print(f"Tong so URL can quet: {len(qd_tasks)} (dung 20 luong song song)...")

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(check_url, *t): t for t in qd_tasks}
    for future in as_completed(futures):
        result = future.result()
        if result:
            found_docs.append(result)
            print(f"  [OK] QD {result['num']}/{result['year']} thang {result['month']:02d} -> {result['url']}")

# === TONG KET ===
print("\n" + "=" * 60)
print(f"TONG KET: Tim thay {len(found_docs)} file PDF hop le")
print("=" * 60)

# Sap xep theo nam + so hieu
found_docs.sort(key=lambda x: (x["type"], x["year"], x["num"]))
for d in found_docs:
    print(f"  {d['type']:20s} | {d['num']:02d}/{d['year']} thang {d['month']:02d} | {d['url']}")

# Luu ket qua
with open("scan_results.json", "w", encoding="utf-8") as f:
    json.dump(found_docs, f, ensure_ascii=False, indent=2)

print(f"\nKet qua da luu vao: scan_results.json")
