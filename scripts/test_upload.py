"""Test upload 1 PDF qua PUBLIC URL (Tailscale Funnel) de kiem tra pipeline day du.

Usage:
    python scripts/test_upload.py <ten-file.pdf> [public-url]
"""
import json
import os
import sys
import time
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
UPLOAD_DIR = r"D:\AI_Second_Brain_DAU\backend\data\uploads"
PASSWORD = "Dau@Second2026"


def login(base):
    from urllib.parse import urlencode

    data = urlencode({"username": "admin@dau.edu.vn", "password": PASSWORD}).encode()
    req = urllib.request.Request(
        base + "/auth/login", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["access_token"]


def api_get(base, token, path):
    req = urllib.request.Request(base + path, headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def upload(base, token, path, allow_ocr=True):
    boundary = uuid.uuid4().hex
    name = os.path.basename(path)
    with open(path, "rb") as f:
        data = f.read()
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"allow_external_ocr\"\r\n\r\n"
        f"{'true' if allow_ocr else 'false'}\r\n"
    ).encode()
    body += (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'
        "Content-Type: application/pdf\r\n\r\n"
    ).encode()
    body += data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        base + "/documents/upload", data=body,
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "multipart/form-data; boundary=" + boundary},
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "test_van_ban.pdf"
    url = sys.argv[2] if len(sys.argv) > 2 else "https://ai-second-brain-dau.vercel.app/api/v1"
    base = url.rstrip("/")
    path = os.path.join(UPLOAD_DIR, target)

    token = login(base)
    print("login ok", flush=True)
    res = upload(base, token, path, allow_ocr=False)
    print("upload:", json.dumps(res, ensure_ascii=False)[:250], flush=True)

    deadline = time.time() + 600
    while time.time() < deadline:
        time.sleep(10)
        try:
            data = api_get(base, token, "/search?page=1&limit=500")
        except Exception as exc:
            print("search err", exc, flush=True)
            continue
        for r in data.get("results", []):
            if r.get("soHieu") == target:
                print("FOUND:", json.dumps(r, ensure_ascii=False)[:500], flush=True)
                return
    print("TIMEOUT - khong thay van ban trong DB", flush=True)


if __name__ == "__main__":
    main()
