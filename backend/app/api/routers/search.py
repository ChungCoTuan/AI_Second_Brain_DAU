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
    db: Session = Depends(get_db)
):
    """
    Tìm kiếm văn bản.
    Do chưa có bảng Corpus và Elasticsearch, tạm giả lập dữ liệu trả về dựa trên input.
    """
    
    all_docs = []
    results = []
    q_lower = q.lower()
    
    for doc in all_docs:
        if nguon != "all" and doc["nguon"] != nguon:
            continue
        if loai != "all" and doc["loai"] != loai:
            continue
        
        # Simple text search
        if q_lower:
            text_to_search = f'{doc["soHieu"]} {doc["tomTat"]} {" ".join(doc["chuDe"])} {doc["coQuan"]} {doc["ngay"]}'.lower()
            if q_lower not in text_to_search:
                continue
                
        results.append(doc)
        
    return {
        "results": results,
        "total": len(all_docs)
    }




