"""Publish Document Manager — DAU Second Brain.

CLI tool để quản lý trạng thái xuất bản (PUBLISHED / PENDING_REVIEW) của documents
mà không cần chạy lại toàn bộ preprocessing pipeline.

Cách dùng:
  # Xem danh sách tất cả documents và trạng thái
  python scripts/publish_documents.py --list

  # Publish tất cả documents (chạy sau khi preprocess lần đầu)
  python scripts/publish_documents.py --publish-all

  # Publish một document cụ thể
  python scripts/publish_documents.py --publish <doc_id>

  # Chuyển về PENDING_REVIEW (khi cần review lại)
  python scripts/publish_documents.py --set-pending <doc_id>

  # Publish theo chủ đề
  python scripts/publish_documents.py --publish-topic DAO_TAO

  # Xem thống kê
  python scripts/publish_documents.py --stats
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

ROOT = Path(__file__).parent.parent.parent
DOCS_PATH = ROOT / "data" / "processed" / "documents.jsonl"
CHUNKS_PATH = ROOT / "data" / "processed" / "chunks.jsonl"


# ─── Core helpers ─────────────────────────────────────────────────────────────

def _load_jsonl(path: Path) -> list[dict]:
    """Load toàn bộ JSONL file vào list."""
    if not path.exists():
        print(f"❌ Không tìm thấy: {path}")
        sys.exit(1)
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def _save_jsonl(path: Path, items: list[dict]) -> None:
    """Ghi list dict trở lại JSONL, backup file cũ trước."""
    # Backup
    backup = path.with_suffix(f".jsonl.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(path, backup)
    print(f"   💾 Backup → {backup.name}")

    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def _update_status(doc_ids: set[str], new_status: str) -> tuple[int, int]:
    """
    Cập nhật trang_thai_xuat_ban cho documents và chunks.
    Returns: (docs_updated, chunks_updated)
    """
    # ── Update documents.jsonl ──
    docs = _load_jsonl(DOCS_PATH)
    docs_updated = 0
    for doc in docs:
        if doc["doc_id"] in doc_ids:
            old = doc.get("trang_thai_xuat_ban", "PENDING_REVIEW")
            doc["trang_thai_xuat_ban"] = new_status
            if old != new_status:
                docs_updated += 1

    _save_jsonl(DOCS_PATH, docs)

    # ── Update chunks.jsonl ──
    chunks = _load_jsonl(CHUNKS_PATH)
    chunks_updated = 0
    for chunk in chunks:
        if chunk.get("doc_id", "") in doc_ids:
            old = chunk.get("trang_thai_xuat_ban", "PENDING_REVIEW")
            chunk["trang_thai_xuat_ban"] = new_status
            if old != new_status:
                chunks_updated += 1

    _save_jsonl(CHUNKS_PATH, chunks)

    return docs_updated, chunks_updated


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_list():
    """Liệt kê tất cả documents với trạng thái."""
    docs = _load_jsonl(DOCS_PATH)

    published = [d for d in docs if d.get("trang_thai_xuat_ban") == "PUBLISHED"]
    pending = [d for d in docs if d.get("trang_thai_xuat_ban") != "PUBLISHED"]

    print(f"\n{'='*70}")
    print(f"  DANH SÁCH VĂN BẢN ({len(docs)} văn bản)")
    print(f"{'='*70}")

    if published:
        print(f"\n✅ PUBLISHED ({len(published)}):")
        for d in published:
            print(f"   [{d['doc_id']}] {d.get('ten_van_ban', d['doc_id'])[:60]}")

    if pending:
        print(f"\n⏳ PENDING_REVIEW ({len(pending)}):")
        for d in pending:
            print(f"   [{d['doc_id']}] {d.get('ten_van_ban', d['doc_id'])[:60]}")

    print(f"\n📊 Tổng: {len(published)} PUBLISHED | {len(pending)} PENDING_REVIEW")
    print(f"{'='*70}\n")


def cmd_stats():
    """Thống kê nhanh."""
    docs = _load_jsonl(DOCS_PATH)
    chunks = _load_jsonl(CHUNKS_PATH)

    pub_docs = sum(1 for d in docs if d.get("trang_thai_xuat_ban") == "PUBLISHED")
    pub_chunks = sum(1 for c in chunks if c.get("trang_thai_xuat_ban") == "PUBLISHED")

    print(f"\n📊 THỐNG KÊ:")
    print(f"   Documents : {pub_docs}/{len(docs)} PUBLISHED")
    print(f"   Chunks    : {pub_chunks}/{len(chunks)} PUBLISHED (có thể index vào FAISS)")
    print(f"   Trạng thái: {'✅ Sẵn sàng RAG' if pub_chunks > 0 else '❌ Chưa có chunk PUBLISHED — RAG sẽ trả 0 kết quả!'}\n")


def cmd_publish_all():
    """Publish tất cả documents."""
    docs = _load_jsonl(DOCS_PATH)
    all_ids = {d["doc_id"] for d in docs}

    print(f"\n🚀 Đang publish {len(all_ids)} documents...")
    d, c = _update_status(all_ids, "PUBLISHED")
    print(f"✅ Đã cập nhật: {d} documents, {c} chunks → PUBLISHED")
    print("   Hãy rebuild FAISS index: python run_pipeline.py --step index\n")


def cmd_publish(doc_id: str):
    """Publish một document."""
    docs = _load_jsonl(DOCS_PATH)
    found = next((d for d in docs if d["doc_id"] == doc_id), None)
    if not found:
        print(f"❌ Không tìm thấy doc_id: {doc_id}")
        print("   Dùng --list để xem danh sách")
        sys.exit(1)

    print(f"\n🔄 Publishing: [{doc_id}] {found.get('ten_van_ban', doc_id)}")
    d, c = _update_status({doc_id}, "PUBLISHED")
    print(f"✅ Đã cập nhật: {d} document, {c} chunks → PUBLISHED")
    print("   Hãy rebuild FAISS index: python run_pipeline.py --step index\n")


def cmd_set_pending(doc_id: str):
    """Chuyển document về PENDING_REVIEW."""
    docs = _load_jsonl(DOCS_PATH)
    found = next((d for d in docs if d["doc_id"] == doc_id), None)
    if not found:
        print(f"❌ Không tìm thấy doc_id: {doc_id}")
        sys.exit(1)

    print(f"\n🔄 Setting pending: [{doc_id}] {found.get('ten_van_ban', doc_id)}")
    d, c = _update_status({doc_id}, "PENDING_REVIEW")
    print(f"⏳ Đã cập nhật: {d} document, {c} chunks → PENDING_REVIEW")
    print("   Hãy rebuild FAISS index để áp dụng: python run_pipeline.py --step index\n")


def cmd_publish_topic(chu_de: str):
    """Publish tất cả documents theo chủ đề."""
    docs = _load_jsonl(DOCS_PATH)
    topic_ids = {d["doc_id"] for d in docs if d.get("chu_de") == chu_de}

    if not topic_ids:
        print(f"❌ Không tìm thấy văn bản nào với chủ đề: {chu_de}")
        valid = list({d.get("chu_de", "KHAC") for d in docs})
        print(f"   Chủ đề hợp lệ: {', '.join(valid)}")
        sys.exit(1)

    print(f"\n🚀 Đang publish {len(topic_ids)} documents với chu_de={chu_de}...")
    d, c = _update_status(topic_ids, "PUBLISHED")
    print(f"✅ Đã cập nhật: {d} documents, {c} chunks → PUBLISHED\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="DAU Second Brain — Quản lý trạng thái xuất bản văn bản"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="Liệt kê tất cả documents")
    group.add_argument("--stats", action="store_true", help="Thống kê nhanh")
    group.add_argument("--publish-all", action="store_true", help="Publish tất cả")
    group.add_argument("--publish", metavar="DOC_ID", help="Publish một document")
    group.add_argument("--set-pending", metavar="DOC_ID", help="Chuyển về PENDING_REVIEW")
    group.add_argument(
        "--publish-topic",
        metavar="CHU_DE",
        help="Publish theo chủ đề (DAO_TAO, TUYEN_SINH, TAI_CHINH, NHAN_SU, KHAC)",
    )

    args = parser.parse_args()

    if args.list:
        cmd_list()
    elif args.stats:
        cmd_stats()
    elif args.publish_all:
        cmd_publish_all()
    elif args.publish:
        cmd_publish(args.publish)
    elif args.set_pending:
        cmd_set_pending(args.set_pending)
    elif args.publish_topic:
        cmd_publish_topic(args.publish_topic)


if __name__ == "__main__":
    main()
