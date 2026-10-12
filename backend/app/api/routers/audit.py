import re
from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...db.models import Document, DocumentRelation, AuditTrail, User
from ...core.security import get_current_admin

router = APIRouter()

@router.get("/auditing/warnings")
async def get_auditing_warnings(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    """
    Quét chéo: Tìm các văn bản (quy chế) căn cứ vào văn bản đã hết hiệu lực.
    """
    warnings = []
    
    # Lấy tất cả quan hệ "căn cứ" chưa được resolve
    can_cu_relations = db.query(DocumentRelation).filter(
        DocumentRelation.relation_type == "căn cứ",
        DocumentRelation.status == "published"
    ).all()
    
    # Lấy tất cả văn bản đã bị thay thế/bãi bỏ
    het_hieu_luc = db.query(DocumentRelation).filter(
        DocumentRelation.relation_type.ilike("%thay thế%") |
        DocumentRelation.relation_type.ilike("%bãi bỏ%")
    ).all()
    
    import re
    def normalize_doc_id(s: Optional[str]) -> str:
        if not s:
            return ""
        return re.sub(r'[\)\.\,\;\:\/\-\s]+$', '', s.strip()).strip().lower()
    
    # Map normalized target_doc của văn bản bị thay thế/bãi bỏ -> relation
    het_hieu_luc_map = {}
    for rel in het_hieu_luc:
        norm_key = normalize_doc_id(rel.target_doc)
        if norm_key and norm_key not in het_hieu_luc_map:
            het_hieu_luc_map[norm_key] = rel
            
    # Bổ sung các văn bản trong CSDL có trạng thái Hết hiệu lực
    docs_expired = db.query(Document).filter(
        Document.trang_thai_hieu_luc.in_(["Hết hiệu lực", "Hết hiệu lực một phần", "Bị thay thế", "Bị bãi bỏ"])
    ).all()
    for d in docs_expired:
        norm_key = normalize_doc_id(d.filename)
        if norm_key and norm_key not in het_hieu_luc_map:
            het_hieu_luc_map[norm_key] = d
    
    warnings_map = {}
    
    for rel in can_cu_relations:
        norm_target = normalize_doc_id(rel.target_doc)
        if norm_target in het_hieu_luc_map:
            thay_the_item = het_hieu_luc_map[norm_target]
            rel_type_display = getattr(thay_the_item, 'relation_type', 'hết hiệu lực')
            
            so_hieu = rel.source_doc
            if so_hieu not in warnings_map:
                warnings_map[so_hieu] = {
                    "docId": str(rel.id),
                    "soHieu": so_hieu,
                    "loai": "Văn bản",
                    "n": 1,
                    "baiBo": True if "bãi bỏ" in rel_type_display else False,
                    "chiTietLoi": f"Căn cứ {rel.target_doc} đã {rel_type_display}"
                }
            else:
                warnings_map[so_hieu]["n"] += 1
                warnings_map[so_hieu]["chiTietLoi"] += f", {rel.target_doc} đã {rel_type_display}"
                
            if "bãi bỏ" in rel_type_display:
                warnings_map[so_hieu]["baiBo"] = True
                
    warnings = list(warnings_map.values())
            
    return {"warnings": warnings}


@router.post("/auditing/warnings/{so_hieu:path}/resolve")
async def resolve_warning(so_hieu: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    """Đánh dấu các cảnh báo của văn bản này là đã xem/giải quyết."""
    relations = db.query(DocumentRelation).filter(
        DocumentRelation.source_doc == so_hieu,
        DocumentRelation.relation_type == "căn cứ",
        DocumentRelation.status == "published"
    ).all()
    
    for rel in relations:
        rel.status = "resolved"
        
    db.commit()
    from ...services.notifier import notifier
    notifier.push_sync("update")
    return {"status": "success"}


@router.get("/audit/logs")
async def get_audit_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    """Returns all audit logs, ordered by timestamp descending."""
    logs = db.query(AuditTrail).order_by(AuditTrail.timestamp.desc()).all()
    log_list = []
    for log in logs:
        log_list.append({
            "id": log.id,
            "item_type": log.item_type,
            "item_id": log.item_id,
            "vb": log.vb,
            "dieu": log.dieu,
            "original_text": log.original_text,
            "original_summary": log.original_summary,
            "edited_summary": log.edited_summary,
            "action": log.action,
            "author": log.author,
            "timestamp": log.timestamp
        })
    return {"logs": log_list}


