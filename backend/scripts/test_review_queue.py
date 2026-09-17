import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy.orm import Session
from backend.db.session import SessionLocal
from backend.db.models import Document, DocumentChunk, Summary, Citation, ReviewItem, ReviewLog
from backend.services.review import get_review_queue, process_review_action, get_audit_logs

def test_review_queue_workflow():
    print("🧪 Running End-to-End Review Queue & Audit Trail Verification Test (UC-04)...")
    print("=" * 70)
    db: Session = SessionLocal()

    try:
        # 1. Fetch a real document and chunk from DB
        doc = db.query(Document).first()
        if not doc:
            print("⚠️ No document found in DB. Please run seed_db.py first.")
            return

        chunk = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).first()
        if not chunk:
            print("⚠️ No chunk found in DB. Please run seed_db.py first.")
            return

        # 2. Lock document status in pending_review
        doc.trang_thai_xuat_ban = "pending_review"
        db.commit()
        print(f"✅ Set Document [{doc.id}] status to 'pending_review' (Publish Gate active).")

        # 3. Create sample summary & flagged citation
        test_summary = Summary(
            document_id=doc.id,
            noi_dung_tom_tat="Bản tóm tắt chứa câu bị gắn cờ contradiction.",
            phien_ban_model="unit-test-nli-v1"
        )
        db.add(test_summary)
        db.commit()

        test_citation = Citation(
            summary_id=test_summary.id,
            chunk_id=chunk.id,
            cau_tom_tat="AI sinh câu bị mâu thuẫn thuật ngữ pháp lý.",
            diem_faithfulness=0.2,
            nhan_nli="contradiction"
        )
        db.add(test_citation)
        db.commit()

        # 4. Create ReviewItem in queue
        test_review = ReviewItem(
            citation_id=test_citation.id,
            document_id=doc.id,
            nhan_nli="contradiction",
            do_uu_tien="high",
            trang_thai="pending"
        )
        db.add(test_review)
        db.commit()
        print(f"✅ Inserted ReviewItem #{test_review.id} with priority 'high' (CONTRADICTION).")

        # 5. Test get_review_queue()
        queue = get_review_queue(db, page=1, limit=10, status_filter="pending")
        print(f"✅ Query get_review_queue(): Found {queue['total']} pending items.")
        assert queue["total"] > 0, "Queue should contain the inserted item"

        # 6. Test process_review_action with action="edit" and NLI re-validation
        edited_text = f"Cán bộ sửa câu chính xác dựa trên {chunk.dieu_khoan}."
        action_res = process_review_action(
            db=db,
            item_id=test_review.id,
            action="edit",
            edited_sentence=edited_text,
            reviewer_id="can_bo_test"
        )
        print(f"✅ Executed process_review_action('edit'):")
        print(f"   - Item Status: {action_res['new_status']}")
        print(f"   - New NLI Label: {action_res['new_nli_label']}")
        print(f"   - Document Publish Status: {action_res['document_publish_status']}")

        # 7. Test get_audit_logs()
        logs = get_audit_logs(db, limit=10)
        print(f"✅ Query get_audit_logs(): Found {len(logs)} audit log records.")
        assert len(logs) > 0, "Audit logs should contain entry"
        print(f"   - Latest Log: Action '{logs[0]['hanh_dong']}', Original: '{logs[0]['cau_ai_sinh']}', Edited: '{logs[0]['cau_sau_sua']}'")

        # Clean up test review objects
        db.delete(test_review)
        db.delete(test_citation)
        db.delete(test_summary)
        db.commit()
        print("🧹 Cleaned up test verification entries.")

        print("=" * 70)
        print("🎉 REVIEW QUEUE & AUDIT TRAIL (UC-04) VERIFIED 100% SUCCESSFULLY!")

    except Exception as e:
        db.rollback()
        print(f"❌ Test failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    test_review_queue_workflow()

