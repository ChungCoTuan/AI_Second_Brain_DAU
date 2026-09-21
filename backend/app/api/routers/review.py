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

class RevalidateRequest(BaseModel):
    original_text: str
    edited_summary: str

@router.post("/review/revalidate")
async def revalidate_nli(request: RevalidateRequest):
    """
    Xác minh lại nhãn NLI sau khi người dùng sửa đổi tóm tắt.
    """
    label = extractor.verify_nli(request.original_text, request.edited_summary)
    return {"nli_label": label}

@router.get("/review/pending")
async def get_pending_review_data(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns all items that are pending review.
    """
    obligations = db.query(Obligation).filter(Obligation.status == "pending_review").all()
    thresholds = db.query(Threshold).filter(Threshold.status == "pending_review").all()
    
    nghia_vu_list = []
    for nv in obligations:
        nghia_vu_list.append({
            "id": nv.id,
            "document_id": nv.document_id,
            "vb": nv.vb,
            "dieu": nv.dieu,
            "loai": nv.loai,
            "chuThe": nv.chu_the,
            "noiDung": nv.noi_dung,
            "hanChot": nv.han_chot,
            "nguon": nv.nguon,
            "status": nv.status,
            "tom_tat": nv.tom_tat,
            "nli_label": nv.nli_label
        })
        
    con_so_chot_list = []
    for cs in thresholds:
        con_so_chot_list.append({
            "id": cs.id,
            "document_id": cs.document_id,
            "vb": cs.vb,
            "dieu": cs.dieu,
            "giaTri": cs.gia_tri,
            "yNghia": cs.y_nghia,
            "nguon": cs.nguon,
            "status": cs.status,
            "tom_tat": cs.tom_tat,
            "nli_label": cs.nli_label
        })
        
    return {
        "nghiaVu": nghia_vu_list,
        "conSoChot": con_so_chot_list
    }


@router.put("/review/{item_type}/{item_id}/publish")
async def publish_item(item_type: str, item_id: int, db: Session = Depends(get_db)):
    """
    Changes the status of a specific item to 'published'
    """
    if item_type == "nghiaVu":
        item = db.query(Obligation).filter(Obligation.id == item_id).first()
    elif item_type == "conSoChot":
        item = db.query(Threshold).filter(Threshold.id == item_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid item_type. Must be 'nghiaVu' or 'conSoChot'.")
        
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if item.status == "published":
        return {"status": "success", "message": "Item is already published."}
        
    
    action_taken = "Duyệt giữ nguyên"
    
    # Check if there is edited_summary in request (if request exists)
    # The original function signature might not have request, let's keep it simple
    # if we can't extract edited_summary, we just log it as "Duyệt giữ nguyên"
    # Actually, let's just create the AuditTrail
    
    from datetime import datetime
    audit = AuditTrail(
        item_type=item_type,
        item_id=item_id,
        vb=item.vb,
        dieu=item.dieu,
        original_text=item.nguon,
        original_summary=item.tom_tat or "",
        edited_summary=None,
        action="Duyệt giữ nguyên",
        author="Admin",
        timestamp=datetime.now().isoformat()
    )
    db.add(audit)
    
    item.status = "published"
    db.commit()
    
    return {"status": "success", "message": f"{item_type} ID {item_id} has been published successfully."}


@router.put("/review/{item_type}/{item_id}/reject")
async def reject_item(item_type: str, item_id: int, db: Session = Depends(get_db)):
    """
    Changes the status of a specific item to 'rejected'
    """
    if item_type == "nghiaVu":
        item = db.query(Obligation).filter(Obligation.id == item_id).first()
    elif item_type == "conSoChot":
        item = db.query(Threshold).filter(Threshold.id == item_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid item_type. Must be 'nghiaVu' or 'conSoChot'.")
        
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if item.status == "rejected":
        return {"status": "success", "message": "Item is already rejected."}
        
    
    from datetime import datetime
    audit = AuditTrail(
        item_type=item_type,
        item_id=item_id,
        vb=item.vb,
        dieu=item.dieu,
        original_text=item.nguon,
        original_summary=item.tom_tat or "",
        edited_summary=None,
        action="Từ chối duyệt",
        author="Admin",
        timestamp=datetime.now().isoformat()
    )
    db.add(audit)
    item.status = "rejected"
    db.commit()
    
    return {"status": "success", "message": f"{item_type} ID {item_id} has been rejected successfully."}

class ChatRequest(BaseModel):
    query: str


