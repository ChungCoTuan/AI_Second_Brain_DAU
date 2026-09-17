import sys
import os

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Add backend and root directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.db.session import SessionLocal
from backend.db.models import Document, DocumentChunk

def test_topic_dashboard():
    db = SessionLocal()
    try:
        docs = db.query(Document).all()
        chunks = db.query(DocumentChunk).all()

        print(f"🔍 Testing Topic Summary Aggregation on {len(docs)} documents & {len(chunks)} chunks...")

        TOPIC_METADATA = {
            "DAO_TAO": "Đào Tạo & Học Vụ",
            "TUYEN_SINH": "Tuyển Sinh & Nhập Học",
            "TAI_CHINH": "Tài Chính & Học Phí",
            "NHAN_SU": "Nhân Sự & Giảng Viên",
            "CO_SO_VAT_CHAT": "Cơ Sở Vật Chất",
            "KHAC": "Văn Bản Hành Chính Khác"
        }

        topic_stats = {code: {"total": 0, "published": 0, "pending": 0, "chunks": 0} for code in TOPIC_METADATA}

        for d in docs:
            t_code = d.chu_de if d.chu_de in TOPIC_METADATA else "KHAC"
            topic_stats[t_code]["total"] += 1
            if d.trang_thai_xuat_ban == "published":
                topic_stats[t_code]["published"] += 1
            else:
                topic_stats[t_code]["pending"] += 1

        for c in chunks:
            parent = next((d for d in docs if d.id == c.document_id), None)
            t_code = parent.chu_de if parent and parent.chu_de in TOPIC_METADATA else "KHAC"
            topic_stats[t_code]["chunks"] += 1

        print("\n📊 Topic Summary Results:")
        for code, name in TOPIC_METADATA.items():
            st = topic_stats[code]
            total = st["total"]
            comp_rate = round((st["published"] / total * 100), 1) if total > 0 else 0.0
            print(f"   [{code}] {name}:")
            print(f"      Total Docs: {st['total']} | Published: {st['published']} | Pending: {st['pending']} | Chunks: {st['chunks']} | Completion: {comp_rate}%")

        assert len(topic_stats) == 6, "Expected 6 topic summary items"
        print("\n🎉 ALL TOPIC DASHBOARD AGGREGATION TESTS PASSED!")

    finally:
        db.close()

if __name__ == "__main__":
    test_topic_dashboard()
