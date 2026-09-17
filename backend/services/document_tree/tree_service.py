import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.db.models import Document, DocumentRelation

logger = logging.getLogger(__name__)

def seed_document_relations(db: Session) -> int:
    """Seed sample explicit legal relations if table is empty."""
    count = db.query(DocumentRelation).count()
    if count > 0:
        return count

    docs = db.query(Document).all()
    if len(docs) < 2:
        return 0

    # Add sample legal relations between documents
    r1 = DocumentRelation(
        document_id_a=docs[0].id,
        document_id_b=docs[1].id,
        loai_quan_he="can_cu",
        diem_tuong_dong=1.0
    )
    db.add(r1)

    if len(docs) >= 3:
        r2 = DocumentRelation(
            document_id_a=docs[2].id,
            document_id_b=docs[0].id,
            loai_quan_he="sua_doi",
            diem_tuong_dong=1.0
        )
        db.add(r2)

    db.commit()
    logger.info("Seeded initial document relations into database.")
    return db.query(DocumentRelation).count()


def build_document_tree(db: Session, doc_id: str) -> Dict[str, Any]:
    """Retrieve legal relations and semantic similarity tree for a document."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise ValueError(f"Văn bản ID={doc_id} không tồn tại")

    relations = db.query(DocumentRelation).filter(
        (DocumentRelation.document_id_a == doc_id) | (DocumentRelation.document_id_b == doc_id)
    ).all()

    legal_parents = []
    legal_children = []

    for rel in relations:
        is_source = rel.document_id_a == doc_id
        target_id = rel.document_id_b if is_source else rel.document_id_a
        target_doc = db.query(Document).filter(Document.id == target_id).first()
        if not target_doc:
            continue

        rel_info = {
            "doc_id": target_doc.id,
            "ten_van_ban": target_doc.ten_van_ban,
            "so_hieu": target_doc.so_hieu or "",
            "loai_quan_he": rel.loai_quan_he,
            "pham_vi_ap_dung": target_doc.pham_vi_ap_dung or "GENERAL"
        }

        if is_source:
            legal_children.append(rel_info)
        else:
            legal_parents.append(rel_info)

    # Top-K semantic related docs from same topic or database
    semantic_docs = (
        db.query(Document)
        .filter(Document.id != doc_id, Document.chu_de == doc.chu_de)
        .limit(3)
        .all()
    )

    if not semantic_docs:
        semantic_docs = (
            db.query(Document)
            .filter(Document.id != doc_id)
            .limit(3)
            .all()
        )

    semantic_related = [
        {
            "doc_id": s.id,
            "ten_van_ban": s.ten_van_ban,
            "so_hieu": s.so_hieu or "",
            "loai_quan_he": "cung_chu_de",
            "diem_tuong_dong": 0.85,
            "pham_vi_ap_dung": s.pham_vi_ap_dung or "GENERAL"
        }
        for s in semantic_docs
    ]

    return {
        "doc_id": doc.id,
        "so_hieu": doc.so_hieu or "",
        "ten_van_ban": doc.ten_van_ban,
        "pham_vi_ap_dung": doc.pham_vi_ap_dung or "GENERAL",
        "legal_parents": legal_parents,
        "legal_children": legal_children,
        "semantic_related": semantic_related
    }


def update_document_scope(db: Session, doc_id: str, scope: str) -> Dict[str, Any]:
    """Update DAU application scope for document."""
    valid_scopes = {"DIRECT_DAU", "GENERAL", "REFERENCE"}
    if scope not in valid_scopes:
        raise ValueError(f"Scope '{scope}' không hợp lệ. Phải là một trong {valid_scopes}")

    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise ValueError(f"Văn bản ID={doc_id} không tồn tại")

    doc.pham_vi_ap_dung = scope
    db.commit()
    db.refresh(doc)
    return {
        "doc_id": doc.id,
        "pham_vi_ap_dung": doc.pham_vi_ap_dung,
        "message": "Cập nhật phạm vi áp dụng thành công"
    }
