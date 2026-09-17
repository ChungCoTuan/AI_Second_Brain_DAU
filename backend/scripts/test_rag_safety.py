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
from backend.db.models import Document
from backend.services.retrieval.rag_chain import query_with_citation

def test_rag_safety():
    db = SessionLocal()
    try:
        print("🔍 Testing RAG Safety & Citations Filtering...")

        question = "Quy định về xét tuyển và tuyển sinh đại học như thế nào?"
        res = query_with_citation(question=question, run_nli_check=False)

        assert res is not None, "query_with_citation returned None"
        print(f"✅ RAG query executed with status: '{res.get('nli_status')}'")
        print(f"   Message: {res.get('message')}")
        print(f"   Citations returned: {len(res.get('citations', []))}")

        for cit in res.get("citations", []):
            doc_id = cit.get("doc_id")
            if doc_id:
                doc = db.query(Document).filter(Document.id == doc_id).first()
                if doc:
                    assert doc.trang_thai_xuat_ban in ("published", "PUBLISHED"), (
                        f"Safety Violation! Citation doc {doc_id} is in status '{doc.trang_thai_xuat_ban}'"
                    )
                    print(f"   - Verified Citation [{cit['index']}] '{cit['ten_van_ban']}': Status='{doc.trang_thai_xuat_ban}' (PUBLISHED ✅)")

        print("\n🎉 ALL RAG SAFETY & CITATIONS TESTS PASSED (100% PUBLISHED ONLY)!")

    finally:
        db.close()

if __name__ == "__main__":
    test_rag_safety()
