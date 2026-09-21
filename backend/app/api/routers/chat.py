from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import os
import random
from ...db.session import get_db
from ...db.models import Document, Obligation, Threshold, DocumentRelation, AuditTrail
from ...services.nlp_pipeline import generate_rag_answer, extractor, classify_text, create_embedding
from ...services.pdf_parser import extract_text_from_pdf, chunk_document
from ...services.ingestion.crawl_documents import crawl_chinhphu, get_sync_status, BASE_OUTPUT_DIR
from ...services.vector_db import vector_db

class ExtractRequest(BaseModel):
    text: str

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_rag(request: ChatRequest, db: Session = Depends(get_db)):
    """
    RAG Chatbot endpoint.
    """
    # 1. Truy xuất dữ liệu (Retrieval): Sử dụng FAISS Vector DB
    query_emb = create_embedding(request.query)
    
    # Tìm kiếm vector gần nhất, lấy top 5 kết quả với ngưỡng độ tương đồng > 0.2
    results = vector_db.search(query_emb, top_k=5, threshold=0.2)
    
    if not results:
        context_chunks = ["Không tìm thấy dữ liệu pháp lý liên quan trong hệ thống."]
        citations = []
    else:
        context_chunks = []
        citations = []
        for metadata, score in results:
            context_chunks.append(f"- Tài liệu: {metadata['vb']}, {metadata['dieu']}\n  Nội dung: {metadata['nguon']}")
            citations.append({
                "id": metadata["id"],
                "vb": metadata["vb"],
                "dieu": metadata["dieu"],
                "nguon": metadata["nguon"]
            })
    
    # 2. Sinh câu trả lời qua interface NLP
    answer = generate_rag_answer(request.query, context_chunks)
    
    # 3. Hậu xử lý (Post-processing)
    if "không tìm thấy" in answer.lower() or "tôi là" in answer.lower():
        citations = []
        
    return {
        "query": request.query,
        "answer": answer,
        "citations": citations
    }


