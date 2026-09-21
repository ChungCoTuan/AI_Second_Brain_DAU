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

@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """
    Trả về dữ liệu tổng hợp cho Analytics Dashboard.
    """
    # Tính tổng số văn bản bị thay thế / bãi bỏ
    thay_the_count = db.query(DocumentRelation).filter(DocumentRelation.relation_type == "bị thay thế").count()
    bai_bo_count = db.query(DocumentRelation).filter(DocumentRelation.relation_type == "bị bãi bỏ").count()
    
    # Tính số lượt viện dẫn căn cứ đã hết hiệu lực
    can_cu_relations = db.query(DocumentRelation).filter(DocumentRelation.relation_type == "căn cứ").all()
    het_hieu_luc_names = [r.source_doc for r in db.query(DocumentRelation).filter(
        DocumentRelation.relation_type.in_(["bị thay thế", "bị bãi bỏ"])
    ).all()]
    
    luot_vien = 0
    top_can_cu_dict = {}
    
    for rel in can_cu_relations:
        if rel.target_doc in het_hieu_luc_names:
            luot_vien += 1
            if rel.target_doc in top_can_cu_dict:
                top_can_cu_dict[rel.target_doc] += 1
            else:
                top_can_cu_dict[rel.target_doc] = 1
                
    # Sort top_can_cu_dict
    top_can_cu_sorted = sorted(top_can_cu_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    top_can_cu = [{"canCu": k, "n": v} for k, v in top_can_cu_sorted]
    
    # Mock some data for UI stability (these would normally require deeper NLP analysis)
    tin_cay = {
        "tb": 0,
        "tong": 0,
        "ocr": 0,
        "duoi80": 0
    }
    theo_nam = []

    return {
        "insights": {
            "luotVien": luot_vien,
            "thayThe": thay_the_count,
            "baiBo": bai_bo_count,
            "vbNhieuCanCu": 0,
            "luotLuatMoi": 0,
            "topCanCu": top_can_cu,
            "theoNam": [],
            "tapTrung": {"theoLoai": [], "theoChuDe": []},
            "tinCay": {"tb": 0, "tong": 0, "ocr": 0, "duoi80": 0}
        }
    }


