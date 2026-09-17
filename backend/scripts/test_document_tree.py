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
from backend.db.models import Document, DocumentRelation
from backend.services.document_tree.tree_service import (
    seed_document_relations,
    build_document_tree,
    update_document_scope,
)

def test_document_tree():
    db = SessionLocal()
    try:
        # Fetch target doc
        doc = db.query(Document).first()
        if not doc:
            print("❌ No documents found in database.")
            return

        print(f"🔍 Testing Document Tree for doc_id: {doc.id} ({doc.so_hieu})")

        # 1. Seed relations
        rel_count = seed_document_relations(db)
        print(f"✅ Seeding relations complete: {rel_count} total relations in DB.")

        # 2. Test build_document_tree
        tree = build_document_tree(db, doc.id)
        assert tree is not None, "build_document_tree returned None"
        print(f"✅ Document Tree payload generated successfully:")
        print(f"   Doc ID: {tree['doc_id']}")
        print(f"   DAU Scope: {tree['pham_vi_ap_dung']}")
        print(f"   Legal Parents: {len(tree['legal_parents'])}")
        print(f"   Legal Children: {len(tree['legal_children'])}")
        print(f"   Semantic Related: {len(tree['semantic_related'])}")

        # 3. Test update_document_scope
        updated = update_document_scope(db, doc.id, "DIRECT_DAU")
        assert updated["pham_vi_ap_dung"] == "DIRECT_DAU", "Scope update failed"
        print(f"✅ DAU Application Scope updated to: '{updated['pham_vi_ap_dung']}'")

        # Re-verify DB state
        doc_reloaded = db.query(Document).filter(Document.id == doc.id).first()
        assert doc_reloaded.pham_vi_ap_dung == "DIRECT_DAU", "DB persistence check failed"
        print("✅ DB persistence verified!")

        print("\n🎉 ALL DOCUMENT TREE & APPLICATION SCOPE TESTS PASSED!")

    finally:
        db.close()

if __name__ == "__main__":
    test_document_tree()
