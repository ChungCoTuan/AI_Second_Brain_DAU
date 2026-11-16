"""Nap PDF vao he thong mot cach tuan tu: upload 1 tai lieu, cho xong roi moi upload tiep theo."""
import json
import os
import time
import urllib.error
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000/api/v1"
UPLOAD_DIR = r"D:\AI_Second_Brain_DAU\backend\data\uploads"
TIMEOUT_PER_DOC = 600  # 10 phut / tai lieu


def login():
    from urllib.parse import urlencode

    data = urlencode({"username": "admin@dau.edu.vn", "password": "Dau@Second2026"}).encode()
    req = urllib.request.Request(
        BASE + "/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def api_get(token, path):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def upload(token, path, allow_ocr):
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
        BASE + "/documents/upload",
        data=body,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "multipart/form-data; boundary=" + boundary,
        },
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def existing_filenames(token):
    try:
        res = api_get(token, "/search?page=1&limit=500")
        return {r["soHieu"] for r in res.get("results", [])}
    except Exception:
        return set()


def wait_for_doc(token, filename, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(10)
        try:
            res = api_get(token, "/search?page=1&limit=500")
            for r in res.get("results", []):
                if r.get("soHieu") == filename:
                    return True
        except Exception:
            pass
    return False


def main():
    token = login()
    print("login ok", flush=True)
    done = existing_filenames(token)
    print("da co trong DB:", len(done), flush=True)

    files = sorted(f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(".pdf"))
    for name in files:
        if name in done:
            print("SKIP", name, flush=True)
            continue
        path = os.path.join(UPLOAD_DIR, name)
        try:
            upload(token, path, allow_ocr=True)
            print("UPLOADED", name, flush=True)
        except urllib.error.HTTPError as e:
            print("ERR-UP", name, e.code, e.read().decode("utf-8", "replace")[:150], flush=True)
            continue
        except Exception as e:
            print("ERR-UP", name, type(e).__name__, str(e)[:150], flush=True)
            time.sleep(15)
            try:
                token = login()
            except Exception:
                pass
            continue

        ok = wait_for_doc(token, name, TIMEOUT_PER_DOC)
        print(("DONE  " if ok else "TIMEOUT "), name, flush=True)
        time.sleep(3)


if __name__ == "__main__":
    main()
