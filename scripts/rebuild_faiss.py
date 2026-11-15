"""Thêm cột documents.noi_dung_day_du (nếu chưa có) + rebuild FAISS từ text đã lưu.

Dùng khi chunker được cải tiến: text OCR đã lưu trong DB sẽ được chia lại thành các
đoạn nhỏ (theo Điều/Chương) rồi embedding lại và ghi đè FAISS index.
"""
import argparse
import json
import os
import sys

BACKEND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, BACKEND)
os.chdir(BACKEND)


def ensure_column():
    from app.db.session import engine
    from sqlalchemy import text

    with engine.begin() as conn:
        exists = conn.execute(
            text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name='documents' AND column_name='noi_dung_day_du'"
            )
        ).fetchone()
        if not exists:
            conn.execute(text("ALTER TABLE documents ADD COLUMN noi_dung_day_du TEXT"))
            print("[migrate] Đã thêm cột documents.noi_dung_day_du")
        else:
            print("[migrate] Cột documents.noi_dung_day_du đã tồn tại")


def rebuild_faiss():
    from app.db.session import SessionLocal
    from app.db.models import Document
    from app.services.pdf_parser import chunk_document, clean_ocr_text
    from app.services.vector_db import vector_db
    from app.services.nlp_pipeline import create_embedding

    db = SessionLocal()
    try:
        docs = db.query(Document).all()
        vector_db.clear()
        total_chunks = 0
        total_embeds = 0

        for doc in docs:
            text = doc.noi_dung_day_du or ""
            if not text:
                print(f"[skip] {doc.filename}: chưa có noi_dung_day_du")
                continue

            # Làm sạch text OCR đã lưu (newline literal -> newline thật, bỏ watermark)
            text = clean_ocr_text(text)
            articles = chunk_document(text)
            if not articles:
                articles = [{"dieu_so": "Toàn văn", "raw": text[:2000]}]

            embeddings = []
            metadatas = []
            for art in articles:
                raw = (art.get("raw") or "").strip()
                if not raw:
                    continue
                embeddings.append(create_embedding(raw))
                metadatas.append({
                    "id": str(doc.id),
                    "vb": doc.filename,
                    "dieu": art.get("dieu_so", "Toàn văn"),
                    "tieu_de": art.get("tieu_de", ""),
                    "nguon": raw,
                })

            if embeddings:
                vector_db.add_texts(embeddings, metadatas)
                total_chunks += len(embeddings)
                total_embeds += len(embeddings)
                print(f"[ok] {doc.filename}: {len(embeddings)} chunks")

        print(f"\n[done] Tổng cộng {total_chunks} chunks từ {len(docs)} văn bản")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--migrate-only", action="store_true")
    args = parser.parse_args()

    ensure_column()
    if not args.migrate_only:
        rebuild_faiss()
