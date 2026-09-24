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
    
    # Dữ liệu từ bảng Document
    all_docs = db.query(Document).filter(Document.status == "published").all()
    
    # 1. Tính độ tin cậy
    tong_doc = len(all_docs)
    tb_conf = 0
    ocr_count = 0
    duoi80_count = 0
    
    # 2. Rủi ro tập trung
    loai_dict = {}
    chu_de_dict = {}
    
    # 3. Theo năm
    nam_dict = {}
    
    for doc in all_docs:
        if doc.conf is not None:
            tb_conf += doc.conf
            if doc.conf < 0.80:
                duoi80_count += 1
        if doc.ocr:
            ocr_count += 1
            
        # Theo loại (Lấy từ tên file, ví dụ QĐ, TT, NĐ)
        loai = "Khác"
        lower_name = doc.filename.lower()
        if "qđ" in lower_name or "qd" in lower_name: loai = "Quyết định"
        elif "tt" in lower_name: loai = "Thông tư"
        elif "nđ" in lower_name or "nd" in lower_name: loai = "Nghị định"
        elif "luật" in lower_name: loai = "Luật"
        elif "công văn" in lower_name or "cv" in lower_name: loai = "Công văn"
        
        loai_dict[loai] = loai_dict.get(loai, 0) + 1
        
        # Chủ đề
        if doc.chu_de:
            chu_de_dict[doc.chu_de] = chu_de_dict.get(doc.chu_de, 0) + 1
            
        # Theo năm (Từ ngay_ky hoặc regex từ tên)
        nam = "Không rõ"
        if doc.ngay_ky and len(doc.ngay_ky) >= 4:
            nam = doc.ngay_ky[-4:]
        import re
        year_match = re.search(r'(20\d{2})', doc.filename)
        if year_match:
            nam = year_match.group(1)
            
        nam_dict[nam] = nam_dict.get(nam, 0) + 1
        
    tb_conf = int((tb_conf / tong_doc * 100)) if tong_doc > 0 else 0
    
    theo_loai = [{"loai": k, "n": v} for k, v in sorted(loai_dict.items(), key=lambda x: x[1], reverse=True)[:5]]
    theo_chu_de = [{"chuDe": k, "n": v} for k, v in sorted(chu_de_dict.items(), key=lambda x: x[1], reverse=True)[:5]]
    theo_nam = [{"nam": k, "n": v} for k, v in sorted(nam_dict.items())[-4:]]

    return {
        "insights": {
            "luotVien": luot_vien,
            "thayThe": thay_the_count,
            "baiBo": bai_bo_count,
            "vbNhieuCanCu": 0, # Sẽ tính toán phức tạp hơn ở Epic sau
            "luotLuatMoi": 0, # Sẽ tính toán dựa vào Luật 2025 ở Epic sau
            "topCanCu": top_can_cu,
            "theoNam": theo_nam,
            "tapTrung": {"theoLoai": theo_loai, "theoChuDe": theo_chu_de},
            "tinCay": {"tb": tb_conf, "tong": tong_doc, "ocr": ocr_count, "duoi80": duoi80_count}
        }
    }


