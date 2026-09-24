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
from ...services.ingestion.crawl_documents import crawl_chinhphu, get_sync_status, BASE_OUTPUT_DIR, check_new_chinhphu

class ExtractRequest(BaseModel):
    text: str

router = APIRouter()

@router.get("/system/status")
def get_system_status(db: Session = Depends(get_db)):
    """Returns global system status including new documents flag and crawled docs count."""
    has_new = get_sync_status()
    
    # Đếm số lượng file cào chưa xử lý
    from ...services.ingestion.crawl_documents import BASE_OUTPUT_DIR
    import os
    
    crawled_pdfs = []
    if os.path.exists(BASE_OUTPUT_DIR):
        for root, dirs, files in os.walk(BASE_OUTPUT_DIR):
            for file in files:
                if file.lower().endswith(".pdf"):
                    crawled_pdfs.append(file)
                    
    processed_docs = db.query(Document.filename).all()
    processed_filenames = {doc[0] for doc in processed_docs}
    
    unprocessed_count = sum(1 for f in crawled_pdfs if f not in processed_filenames)
    
    return {
        "has_new_docs": has_new,
        "unprocessed_crawled_count": unprocessed_count
    }

@router.post("/system/ping")
def trigger_ping():
    """Manually triggers the bot ping to check for new documents."""
    result = check_new_chinhphu()
    if not result:
        result = {"has_new": False, "skipped": 0, "scanned": 0}
        
    has_new = get_sync_status()
    return {
        "status": "success", 
        "has_new_docs": has_new,
        "scanned": result.get("scanned", 0),
        "skipped": result.get("skipped", 0)
    }


@router.post("/system/crawl")
def trigger_manual_crawl():
    """Manually triggers the document crawler synchronously."""
    crawl_chinhphu(5) # max 5 files per crawl for demo
    return {"status": "success", "message": "Crawler has finished."}


@router.get("/system/crawled_files")
def get_crawled_files(db: Session = Depends(get_db)):
    """Returns a list of crawled files that have not been processed yet."""
    from ...services.ingestion.crawl_documents import BASE_OUTPUT_DIR
    import os
    
    crawled_pdfs = []
    for root, dirs, files in os.walk(BASE_OUTPUT_DIR):
        for file in files:
            if file.lower().endswith(".pdf"):
                domain = os.path.basename(os.path.dirname(root))
                if domain == "vanban_caotudong":
                    domain = "Giao_duc"
                crawled_pdfs.append({"filename": file, "domain": domain})
                
    processed_docs = db.query(Document.filename).all()
    processed_filenames = [doc[0] for doc in processed_docs]
    
    unprocessed = [f for f in crawled_pdfs if f["filename"] not in processed_filenames]
    
    return {"unprocessed_files": unprocessed}

class ProcessCrawledRequest(BaseModel):
    filename: str


