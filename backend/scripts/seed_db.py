import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.db.session import SessionLocal, engine

from backend.db.models import Document, DocumentChunk, Citation, ReviewItem, Base


DOCUMENTS_JSONL = os.path.join("data", "processed", "documents.jsonl")
CHUNKS_JSONL = os.path.join("data", "processed", "chunks.jsonl")

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None

def seed_database():
    db: Session = SessionLocal()

    print("Checking existing records in database...")
    existing_docs = db.query(Document).count()
    if existing_docs > 0:
        print(f"Database already contains {existing_docs} documents. Seeding skipped or appending new records.")

    print(f"Loading documents from {DOCUMENTS_JSONL}...")
    doc_map = {}
    if os.path.exists(DOCUMENTS_JSONL):
        with open(DOCUMENTS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                doc_id = data.get("doc_id")
                if not doc_id:
                    continue

                existing = db.query(Document).filter(Document.id == doc_id).first()
                if not existing:
                    doc = Document(
                        id=doc_id,
                        ten_van_ban=data.get("ten_van_ban", doc_id),
                        so_hieu=data.get("so_hieu"),
                        loai_van_ban=data.get("loai_van_ban", "Quy định"),
                        chu_de=data.get("chu_de", "KHAC"),
                        pham_vi_ap_dung=data.get("muc_do_lien_quan_dau", "GENERAL"),
                        nguon_du_lieu="chinhphu.vn",
                        ngay_ban_hanh=parse_date(data.get("ngay_ban_hanh")),
                        co_quan_ban_hanh=data.get("co_quan_ban_hanh"),
                        file_goc_url=data.get("file_path"),
                        trang_thai_hieu_luc="con_hieu_luc",
                        trang_thai_xuat_ban="published" if data.get("trang_thai_xuat_ban") == "PUBLISHED" else "pending_review"
                    )
                    db.add(doc)
                    doc_map[doc_id] = doc

        db.commit()
        print(f"Inserted {len(doc_map)} documents.")

    print(f"Loading chunks from {CHUNKS_JSONL}...")
    chunk_count = 0
    seen_ids = set()
    if os.path.exists(CHUNKS_JSONL):
        with open(CHUNKS_JSONL, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if not line.strip():
                    continue
                data = json.loads(line)
                chunk_id = data.get("chunk_id")
                doc_id = data.get("doc_id")
                content = data.get("content", "").strip()

                if not chunk_id or not content:
                    continue

                # Ensure parent document exists
                doc_obj = db.query(Document).filter(Document.id == doc_id).first()
                if not doc_obj:
                    doc_obj = Document(
                        id=doc_id,
                        ten_van_ban=data.get("ten_van_ban", doc_id),
                        so_hieu=data.get("so_hieu"),
                        loai_van_ban="Quy định",
                        chu_de=data.get("chu_de", "KHAC"),
                        trang_thai_xuat_ban="published"
                    )
                    db.add(doc_obj)
                    db.commit()

                # Create unique chunk_id if duplicated in source JSON
                unique_chunk_id = chunk_id
                if unique_chunk_id in seen_ids or db.query(DocumentChunk).filter(DocumentChunk.id == unique_chunk_id).first():
                    unique_chunk_id = f"{chunk_id}_{idx}"
                seen_ids.add(unique_chunk_id)


                chunk = DocumentChunk(
                    id=unique_chunk_id,
                    document_id=doc_id,
                    dieu_khoan=data.get("title", "Khoản 1"),
                    noi_dung=content,
                    so_trang=data.get("so_trang", 1),
                    chunk_index=idx
                )
                db.add(chunk)
                chunk_count += 1

        db.commit()
        print(f"Inserted {chunk_count} chunks into PostgreSQL database.")


    print("Populating initial NLI citations & review items...")
    total_docs = db.query(Document).count()
    total_chunks = db.query(DocumentChunk).count()
    total_citations = db.query(Citation).count()
    total_reviews = db.query(ReviewItem).count()

    from backend.services.document_tree.tree_service import seed_document_relations
    total_relations = seed_document_relations(db)

    db.close()
    print(f"=== Database Seeding Complete ===")
    print(f"Total Documents in DB: {total_docs}")
    print(f"Total Chunks in DB: {total_chunks}")
    print(f"Total Citations in DB: {total_citations}")
    print(f"Total Review Items in DB: {total_reviews}")
    print(f"Total Relations in DB: {total_relations}")

if __name__ == "__main__":
    seed_database()
