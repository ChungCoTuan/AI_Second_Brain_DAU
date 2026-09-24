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

@router.get("/search")
async def search_documents(
    q: str = "",
    nguon: str = "all",
    loai: str = "all",
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Tìm kiếm văn bản từ Database với hỗ trợ phân trang.
    """
    from sqlalchemy import or_, func

    query = db.query(Document)
    
    # Filter by nguon
    if nguon != "all":
        # Tạm map "bộ" -> nguồn là 'bộ' (không có cột này trong DB nên giả lập qua filename hoặc linh_vuc)
        pass # Not fully supported without a source column, keeping it simple
        
    # Filter by loai
    if loai != "all":
        # Mapping loai in frontend to DB
        pass # In a real scenario we might filter by Document.loai if available
        
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




