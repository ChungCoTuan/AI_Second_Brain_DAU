from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import os
import random
from ...db.session import get_db
from ...db.models import Document, Obligation, Threshold, DocumentRelation, AuditTrail
from ...services.nlp_pipeline import generate_rag_answer, extractor, classify_text
from ...services.pdf_parser import extract_text_from_pdf, chunk_document
from ...services.ingestion.crawl_documents import crawl_chinhphu, get_sync_status, BASE_OUTPUT_DIR

class ExtractRequest(BaseModel):
    text: str

router = APIRouter()

@router.get("/auditing/warnings")
async def get_auditing_warnings(db: Session = Depends(get_db)):
    """
    Quét chéo: Tìm các văn bản (quy chế) căn cứ vào văn bản đã hết hiệu lực.
    """
    warnings = []
    
    # Lấy tất cả quan hệ "căn cứ"
    can_cu_relations = db.query(DocumentRelation).filter(DocumentRelation.relation_type == "căn cứ").all()
    
    # Lấy tất cả văn bản đã bị thay thế/bãi bỏ
    het_hieu_luc = db.query(DocumentRelation).filter(
        DocumentRelation.relation_type.in_(["bị thay thế", "bị bãi bỏ"])
    ).all()
    
    # Tạo dictionary map văn bản bị thay thế -> văn bản mới
    het_hieu_luc_map = {rel.source_doc: rel for rel in het_hieu_luc}
    
    for rel in can_cu_relations:
        if rel.target_doc in het_hieu_luc_map:
            thay_the_rel = het_hieu_luc_map[rel.target_doc]
            
            warnings.append({
                "docId": str(rel.id), # Dùng ID tạm
                "soHieu": rel.source_doc, # Tên văn bản quy chế, vd QĐ 324
                "loai": "Quy chế/Quyết định",
                "n": 1, # Số căn cứ hỏng
                "baiBo": True if thay_the_rel.relation_type == "bị bãi bỏ" else False,
                "chiTietLoi": f"Căn cứ {rel.target_doc} đã {thay_the_rel.relation_type} bởi {thay_the_rel.target_doc}"
            })
            
    return {"warnings": warnings}


@router.get("/audit/logs")
async def get_audit_logs(db: Session = Depends(get_db)):
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


