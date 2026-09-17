import sys
import os

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Add backend directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.db.session import SessionLocal
from backend.db.models import Document
from backend.services.report_suggestion.report_service import (
    generate_report_outline,
    build_report_docx_stream,
)

def test_report_suggestion():
    db = SessionLocal()
    try:
        # Fetch any document from DB
        doc = db.query(Document).first()
        if not doc:
            print("❌ No documents found in database.")
            return

        print(f"🔍 Testing report generation for doc_id: {doc.id} ({doc.so_hieu})")

        # 1. Test outline generation
        outline = generate_report_outline(db, doc.id)
        assert outline is not None, "Outline generation returned None"
        print(f"✅ Outline generated using template: '{outline['template_used']}'")
        print(f"   Document Title: {outline['ten_van_ban']}")
        print(f"   Category: {outline['loai_van_ban']} | Topic: {outline['chu_de']}")
        print(f"   Sections count: {len(outline['sections'])}")

        # Verify blank sections constraint
        blank_sections = [sec for sec in outline['sections'] if sec.get('is_blank')]
        assert len(blank_sections) > 0, "No blank sections found! Safety constraint violated."
        print(f"✅ Verified {len(blank_sections)} sections explicitly marked as BLANK (no synthetic hallucinated data)")

        for sec in outline['sections']:
            status = "⚠️ BLANK" if sec.get('is_blank') else "📝 POPULATED"
            print(f"   - [{status}] {sec['heading']}")

        # 2. Test Word (.docx) binary stream generation
        docx_bytes_content = build_report_docx_stream(db, doc.id)
        docx_bytes = len(docx_bytes_content)
        assert docx_bytes > 0, "Generated docx stream is empty!"
        print(f"✅ Word (.docx) stream successfully generated! File size: {docx_bytes} bytes")

        # Save test output for verification
        out_path = os.path.join(os.path.dirname(__file__), "test_report_output.docx")
        with open(out_path, "wb") as f:
            f.write(docx_bytes_content)
        print(f"💾 Test file saved to: {out_path}")
        print("\n🎉 ALL REPORT SUGGESTION ENGINE & DOCX EXPORTER TESTS PASSED!")

    finally:
        db.close()

if __name__ == "__main__":
    test_report_suggestion()
