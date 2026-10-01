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
from ...core.security import get_current_user
from ...db.models import User

class ExtractRequest(BaseModel):
    text: str

router = APIRouter()

@router.get("/search")
async def search_documents(
    q: str = "",
    nguon: str = "all",
    loai: str = "all",
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tìm kiếm văn bản từ Database với hỗ trợ phân trang.
    """
    from sqlalchemy import or_, func

    query = db.query(Document)
    
    # Filter by nguon
    if nguon != "all":
        if nguon == "bộ":
            query = query.filter(Document.source_folder.ilike("%vanban_caotudong%"))
        elif nguon == "trường":
            query = query.filter(Document.source_folder.notilike("%vanban_caotudong%"))
        
    # Filter by loai
    if loai != "all":
        loai_lower = loai.lower()
        if loai_lower == "quyết định":
            query = query.filter(or_(Document.filename.ilike("%qd%"), Document.filename.ilike("%quyết định%")))
        elif loai_lower == "nghị định":
            query = query.filter(or_(Document.filename.ilike("%nd%"), Document.filename.ilike("%nghị định%")))
        elif loai_lower == "thông tư":
            query = query.filter(or_(Document.filename.ilike("%tt%"), Document.filename.ilike("%thông tư%")))
        elif loai_lower == "công văn":
            query = query.filter(or_(Document.filename.ilike("%cv%"), Document.filename.ilike("%công văn%")))
        elif loai_lower == "quy chế":
            query = query.filter(or_(Document.filename.ilike("%qc%"), Document.filename.ilike("%quy chế%")))
        
    # Text search
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Document.filename.ilike(search_term),
                Document.chu_de.ilike(search_term),
                Document.tags.ilike(search_term)
            )
        )
        
    total = query.count()
    
    # Pagination
    skip = (page - 1) * limit
    docs = query.order_by(Document.id.desc()).offset(skip).limit(limit).all()
    
    results = []
    for doc in docs:
        results.append({
            "id": doc.id,
            "soHieu": doc.filename,
            "loai": doc.linh_vuc or "Văn bản",
            "nguon": "bộ" if "QĐ" in doc.filename or "TT" in doc.filename else "trường",
            "coQuan": doc.co_quan_ban_hanh,
            "ngay": doc.ngay_ky,
            "tomTat": "", # Tóm tắt sẽ làm sau nếu có
            "chuDe": [doc.chu_de] if doc.chu_de else [],
            "soDieu": 0,
            "soNghiaVu": len(doc.obligations) if doc.obligations else 0,
            "ocr": doc.ocr
        })
        
    return {
        "results": results,
        "total": total,
        "page": page,
        "limit": limit
    }




