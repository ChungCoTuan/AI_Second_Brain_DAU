import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, case

from backend.db.models import ReviewItem, ReviewLog, Citation, Document, DocumentChunk
from backend.services.nli.nli_checker import get_nli_checker

logger = logging.getLogger(__name__)

def get_review_queue(
    db: Session,
    page: int = 1,
    limit: int = 20,
    status_filter: str = "pending",
    priority_filter: Optional[str] = None
) -> Dict[str, Any]:
    """Lấy danh sách các câu tóm tắt bị NLI gắn cờ cần Cán bộ rà soát (UC-04).
    Ưu tiên: 'high' (contradiction) trước, 'medium' (neutral) sau.
    """
    query = (
        db.query(ReviewItem, Citation, Document, DocumentChunk)
        .join(Document, ReviewItem.document_id == Document.id)
        .outerjoin(Citation, ReviewItem.citation_id == Citation.id)
        .outerjoin(DocumentChunk, Citation.chunk_id == DocumentChunk.id)
    )

    if status_filter:
        query = query.filter(ReviewItem.trang_thai == status_filter)
    if priority_filter:
        query = query.filter(ReviewItem.do_uu_tien == priority_filter)

    # Priority sorting: high -> medium -> low
    priority_order = case(
        (ReviewItem.do_uu_tien == "high", 1),
        (ReviewItem.do_uu_tien == "medium", 2),
        (ReviewItem.do_uu_tien == "low", 3),
        else_=4
    )
    query = query.order_by(priority_order, desc(ReviewItem.created_at))

    total = query.count()
    offset = (page - 1) * limit
    results = query.offset(offset).limit(limit).all()

    items = []
    for item, citation, doc, chunk in results:
        items.append({
            "review_item_id": item.id,
            "document_id": doc.id,
            "ten_van_ban": doc.ten_van_ban,
            "so_hieu": doc.so_hieu or "",
            "citation_id": citation.id if citation else None,
            "cau_ai_sinh": citation.cau_tom_tat if citation else "",
            "nhan_nli": item.nhan_nli,
            "do_uu_tien": item.do_uu_tien,
            "trang_thai": item.trang_thai,
            "source_chunk": {
                "chunk_id": chunk.id if chunk else "",
                "dieu_khoan": chunk.dieu_khoan if chunk else "Khoản 1",
                "noi_dung_goc": chunk.noi_dung if chunk else "",
                "so_trang": chunk.so_trang if chunk else 1,
            } if chunk else None,
            "created_at": item.created_at.isoformat() if item.created_at else None
        })

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": max(1, (total + limit - 1) // limit),
        "items": items
    }


def process_review_action(
    db: Session,
    item_id: int,
    action: str,
    edited_sentence: Optional[str] = None,
    reviewer_id: str = "can_bo_dao_tao"
) -> Dict[str, Any]:
    """Xử lý hành động rà soát của Cán bộ (UC-04):
      - action = 'approve' | 'edit' | 'reject'
      - Nếu action = 'edit': Re-evaluate NLI check câu mới vừa sửa.
      - Ghi log Audit Trail vào review_logs.
      - Publish Gate Check: Nếu văn bản hết câu pending -> chuyển sang 'published'.
    """
    review_item = db.query(ReviewItem).filter(ReviewItem.id == item_id).first()
    if not review_item:
        raise ValueError(f"Không tìm thấy ReviewItem với ID={item_id}")

    citation = db.query(Citation).filter(Citation.id == review_item.citation_id).first()
    original_sentence = citation.cau_tom_tat if citation else ""
    new_nli_score = None
    new_nli_label = review_item.nhan_nli

    if action == "edit":
        if not edited_sentence or not edited_sentence.strip():
            raise ValueError("Câu chỉnh sửa không được để trống")
        
        # Re-run NLI check if chunk exists
        if citation and citation.chunk_id:
            chunk = db.query(DocumentChunk).filter(DocumentChunk.id == citation.chunk_id).first()
            if chunk:
                checker = get_nli_checker(use_rule_based=True)
                nli_res = checker.check(
                    premise=chunk.noi_dung,
                    hypothesis=edited_sentence,
                    chunk_id=chunk.id
                )
                new_nli_label = nli_res.get("nhan_nli", "entailment")
                new_nli_score = float(nli_res.get("diem_nli", 0.95))

        # Update citation text & NLI label
        if citation:
            citation.cau_tom_tat = edited_sentence.strip()
            citation.nhan_nli = new_nli_label
            citation.diem_faithfulness = new_nli_score or 0.95

        review_item.trang_thai = "edited"
        review_item.nhan_nli = new_nli_label

    elif action == "approve":
        review_item.trang_thai = "approved"

    elif action == "reject":
        review_item.trang_thai = "rejected"
    else:
        raise ValueError(f"Hành động không hợp lệ: {action}")

    # Ghi log Audit Trail
    audit_log = ReviewLog(
        review_item_id=review_item.id,
        cau_ai_sinh=original_sentence,
        cau_sau_sua=edited_sentence if action == "edit" else None,
        reviewer_id=reviewer_id,
        hanh_dong=action,
        diem_nli_sau_sua=new_nli_score
    )
    db.add(audit_log)
    db.commit()

    # ── Publish Gate Check ──
    doc_id = review_item.document_id
    remaining_pending = db.query(ReviewItem).filter(
        ReviewItem.document_id == doc_id,
        ReviewItem.trang_thai == "pending"
    ).count()

    doc_status = "pending_review"
    if remaining_pending == 0:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.trang_thai_xuat_ban = "published"
            db.commit()
            doc_status = "published"
            logger.info(f"🎉 Document [{doc_id}] Publish Gate passed -> upgraded to PUBLISHED")

    return {
        "review_item_id": item_id,
        "document_id": doc_id,
        "action": action,
        "new_status": review_item.trang_thai,
        "document_publish_status": doc_status,
        "remaining_pending_in_doc": remaining_pending,
        "new_nli_label": new_nli_label,
        "message": f"Đã xử lý {action} cho item #{item_id} thành công"
    }


def get_audit_logs(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
    """Lấy danh sách nhật ký duyệt Audit Trail."""
    results = (
        db.query(ReviewLog, ReviewItem, Document)
        .join(ReviewItem, ReviewLog.review_item_id == ReviewItem.id)
        .join(Document, ReviewItem.document_id == Document.id)
        .order_by(desc(ReviewLog.created_at))
        .limit(limit)
        .all()
    )

    logs = []
    for log, item, doc in results:
        logs.append({
            "log_id": log.id,
            "review_item_id": item.id,
            "document_id": doc.id,
            "ten_van_ban": doc.ten_van_ban,
            "cau_ai_sinh": log.cau_ai_sinh,
            "cau_sau_sua": log.cau_sau_sua,
            "reviewer_id": log.reviewer_id,
            "hanh_dong": log.hanh_dong,
            "diem_nli_sau_sua": log.diem_nli_sau_sua,
            "created_at": log.created_at.isoformat() if log.created_at else None
        })

    return logs
