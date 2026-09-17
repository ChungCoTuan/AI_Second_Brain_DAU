import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


from sqlalchemy.orm import Session
from backend.db.session import SessionLocal, engine
from backend.db.models import (
    Document, DocumentChunk, Summary, Citation, ReviewItem,
    ReviewLog, ReportTemplate, QueryLog, DocumentRelation
)

def test_crud_all_tables():
    print("🧪 Running End-to-End PostgreSQL CRUD Verification Test...")
    print("=" * 60)
    db: Session = SessionLocal()

    try:
        # 1. Test Documents & Chunks querying
        doc_count = db.query(Document).count()
        chunk_count = db.query(DocumentChunk).count()
        print(f"✅ Table 'documents': {doc_count} records found.")
        print(f"✅ Table 'document_chunks': {chunk_count} records found.")

        # 2. Test Summary insert & delete
        test_summary = Summary(
            document_id="CP_QD_1982_KhungTrinhDoQuocGiaVietNam",
            noi_dung_tom_tat="Bản tóm tắt kiểm thử hệ thống DB PostgreSQL",
            phien_ban_model="unit-test-v1"
        )
        db.add(test_summary)
        db.commit()
        db.refresh(test_summary)
        print(f"✅ Table 'summaries': Inserted test record ID={test_summary.id}.")

        # 3. Test Citation insert
        test_citation = Citation(
            summary_id=test_summary.id,
            chunk_id="CP_QD_1982_KhungTrinhDoQuocGiaVietNam_D1",
            cau_tom_tat="Câu tóm tắt kiểm thử citation",
            diem_faithfulness=0.95,
            nhan_nli="entailment"
        )
        db.add(test_citation)
        db.commit()
        db.refresh(test_citation)
        print(f"✅ Table 'citations': Inserted test record ID={test_citation.id}.")

        # 4. Test ReviewItem insert
        test_review = ReviewItem(
            citation_id=test_citation.id,
            document_id="CP_QD_1982_KhungTrinhDoQuocGiaVietNam",
            nhan_nli="contradiction",
            do_uu_tien="high",
            trang_thai="pending"
        )
        db.add(test_review)
        db.commit()
        db.refresh(test_review)
        print(f"✅ Table 'review_items': Inserted test record ID={test_review.id}.")

        # 5. Test ReviewLog insert
        test_log = ReviewLog(
            review_item_id=test_review.id,
            cau_ai_sinh="Câu AI sinh bị lỗi",
            cau_sau_sua="Câu đã được cán bộ sửa",
            reviewer_id="can_bo_test",
            hanh_dong="edit",
            diem_nli_sau_sua=0.99
        )
        db.add(test_log)
        db.commit()
        db.refresh(test_log)
        print(f"✅ Table 'review_logs': Inserted test record ID={test_log.id}.")

        # 6. Test ReportTemplate insert
        test_template = ReportTemplate(
            loai_bao_cao="Báo cáo định kỳ",
            chu_de_ap_dung="Đào tạo",
            danh_sach_de_muc={"sections": ["Căn cứ pháp lý", "Nội dung báo cáo", "Kết luận"]}
        )
        db.add(test_template)
        db.commit()
        db.refresh(test_template)
        print(f"✅ Table 'report_templates': Inserted test record ID={test_template.id}.")

        # 7. Test QueryLog insert
        test_query = QueryLog(
            cau_hoi="Test quy định đào tạo?",
            cau_tra_loi="Câu trả lời test",
            danh_sach_citation={"citations": ["CP_QD_1982_KhungTrinhDoQuocGiaVietNam_D1"]},
            diem_faithfulness=1.0
        )
        db.add(test_query)
        db.commit()
        db.refresh(test_query)
        print(f"✅ Table 'query_logs': Inserted test record ID={test_query.id}.")

        # 8. Test DocumentRelation insert
        test_relation = DocumentRelation(
            document_id_a="CP_QD_1982_KhungTrinhDoQuocGiaVietNam",
            document_id_b="NT-2026-AI-native-Second-Brain-World-Models",
            loai_quan_he="can_cu",
            diem_tuong_dong=0.88
        )
        db.add(test_relation)
        db.commit()
        db.refresh(test_relation)
        print(f"✅ Table 'document_relations': Inserted test record ID={test_relation.id}.")

        # Cleanup test records
        db.delete(test_relation)
        db.delete(test_query)
        db.delete(test_template)
        db.delete(test_log)
        db.delete(test_review)
        db.delete(test_citation)
        db.delete(test_summary)
        db.commit()
        print("🧹 Cleaned up test verification entries.")

        print("=" * 60)
        print("🎉 ALL 9 POSTGRESQL TABLES VERIFIED SUCCESSFULLY!")

    except Exception as e:
        db.rollback()
        print(f"❌ Database test failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    test_crud_all_tables()
