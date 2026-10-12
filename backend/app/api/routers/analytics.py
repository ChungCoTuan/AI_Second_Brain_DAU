import re
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

def normalize_doc_id(s: Optional[str]) -> str:
    """Chuẩn hóa số hiệu văn bản: loại bỏ dấu ngoặc, dấu chấm phẩy, khoảng trắng thừa."""
    if not s:
        return ""
    cleaned = s.strip()
    # Loại bỏ các ký tự dấu câu thường dính ở cuối số hiệu
    cleaned = re.sub(r'[\)\.\,\;\:\/\-\s]+$', '', cleaned)
    return cleaned.strip().lower()

def clean_display_title(s: Optional[str]) -> str:
    """Chuẩn hóa tiêu đề hiển thị: cắt bỏ ký tự rác ở cuối."""
    if not s:
        return ""
    cleaned = s.strip()
    return re.sub(r'[\)\.\,\;\:\/\-\s]+$', '', cleaned).strip()

def detect_doc_type(filename: str) -> str:
    """Nhận diện loại văn bản chuẩn xác từ tên file."""
    lower = filename.lower()
    if "vbhn" in lower or "văn bản hợp nhất" in lower:
        return "Văn bản hợp nhất"
    elif "nq" in lower or "nghị quyết" in lower:
        return "Nghị quyết"
    elif "qđ" in lower or "qd" in lower or "quyết định" in lower:
        return "Quyết định"
    elif "tt" in lower or "thông tư" in lower:
        return "Thông tư"
    elif "nđ" in lower or "nd" in lower or "nghị định" in lower:
        return "Nghị định"
    elif "luật" in lower or "luat" in lower or "qh" in lower:
        return "Luật"
    elif "công văn" in lower or "cv" in lower:
        return "Công văn"
    elif "tb" in lower or "thông báo" in lower:
        return "Thông báo"
    return "Khác"

@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Trả về dữ liệu tổng hợp tính toán 100% từ CSDL PostgreSQL cho Analytics Dashboard.
    """
    # 1. Tính tổng số văn bản bị thay thế / bãi bỏ thực tế
    thay_the_count = db.query(DocumentRelation).filter(DocumentRelation.relation_type.ilike("%thay thế%")).count()
    bai_bo_count = db.query(DocumentRelation).filter(DocumentRelation.relation_type.ilike("%bãi bỏ%")).count()
    
    # 2. Xây dựng danh mục văn bản đã hết hiệu lực / bị thay thế / bãi bỏ
    het_hieu_luc_relations = db.query(DocumentRelation).filter(
        DocumentRelation.relation_type.ilike("%thay thế%") | 
        DocumentRelation.relation_type.ilike("%bãi bỏ%")
    ).all()
    
    expired_map = {}
    for r in het_hieu_luc_relations:
        norm_key = normalize_doc_id(r.target_doc)
        if norm_key:
            expired_map[norm_key] = r
            
    # Bổ sung các văn bản trong kho có trạng thái Hết hiệu lực
    docs_expired = db.query(Document).filter(
        Document.trang_thai_hieu_luc.in_(["Hết hiệu lực", "Hết hiệu lực một phần", "Bị thay thế", "Bị bãi bỏ"])
    ).all()
    for d in docs_expired:
        norm_key = normalize_doc_id(d.filename)
        if norm_key and norm_key not in expired_map:
            expired_map[norm_key] = d
            
    # 3. Quét đối soát quan hệ "căn cứ"
    can_cu_relations = db.query(DocumentRelation).filter(DocumentRelation.relation_type == "căn cứ").all()
    
    luot_vien = 0
    top_can_cu_dict = {}
    invalid_docs_map = {}
    luot_luat_moi = 0
    top_invalid_bases = {}
    
    doc_dates_map = {d.filename: d.ngay_ky or "" for d in db.query(Document).all()}
    
    for rel in can_cu_relations:
        clean_target = clean_display_title(rel.target_doc)
        if clean_target:
            top_can_cu_dict[clean_target] = top_can_cu_dict.get(clean_target, 0) + 1
            
        norm_target = normalize_doc_id(rel.target_doc)
        if norm_target in expired_map:
            luot_vien += 1
            invalid_docs_map[rel.source_doc] = invalid_docs_map.get(rel.source_doc, 0) + 1
            top_invalid_bases[clean_target] = top_invalid_bases.get(clean_target, 0) + 1
            
            # Kiểm tra xem có dính vào đợt sửa đổi/văn bản mới 2025-2026 không
            source_date = doc_dates_map.get(rel.source_doc, "")
            is_new_period = (
                "2025" in rel.source_doc or "2026" in rel.source_doc or
                "2025" in source_date or "2026" in source_date or
                "2025" in rel.target_doc or "2026" in rel.target_doc
            )
            if is_new_period:
                luot_luat_moi += 1
                
    # Tính số văn bản dính từ 2 căn cứ hỏng trở lên
    vb_nhieu_can_cu = sum(1 for cnt in invalid_docs_map.values() if cnt >= 2)
    
    # Top căn cứ bị viện dẫn nhiều nhất trong toàn trường
    top_can_cu_sorted = sorted(top_can_cu_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    top_can_cu = [{"canCu": k, "n": v} for k, v in top_can_cu_sorted]
    
    # 4. Thống kê theo năm từ các sự kiện thay thế / bãi bỏ thực tế (Lọc bỏ năm rác như 2092)
    nam_dict = {}
    for r in het_hieu_luc_relations:
        y = None
        s_date = doc_dates_map.get(r.source_doc, "")
        if s_date:
            m = re.search(r'\b(20[0-2]\d)\b', s_date)
            if m:
                y = m.group(1)
        if not y:
            m = re.search(r'/(20[0-2]\d)/', r.target_doc)
            if m:
                y = m.group(1)
        if not y:
            m = re.search(r'[\/_ -](20[0-2]\d)[\._ -]', r.source_doc)
            if m:
                y = m.group(1)
        if y and 2000 <= int(y) <= 2026:
            nam_dict[y] = nam_dict.get(y, 0) + 1
            
    # Lấy 4 năm gần nhất có dữ liệu
    theo_nam = [{"nam": k, "n": v} for k, v in sorted(nam_dict.items())[-4:]]
    
    # 5. Rủi ro tập trung ở đâu & Độ tin cậy
    all_published_docs = db.query(Document).filter(Document.status == "published").all()
    tong_doc = len(all_published_docs)
    tb_conf = 0
    ocr_count = 0
    duoi80_count = 0
    
    loai_dict = {}
    chu_de_dict = {}
    
    for doc in all_published_docs:
        if doc.conf is not None:
            tb_conf += doc.conf
            if doc.conf < 0.80:
                duoi80_count += 1
        if doc.ocr:
            ocr_count += 1
            
        loai = detect_doc_type(doc.filename)
        loai_dict[loai] = loai_dict.get(loai, 0) + 1
        
        cd = doc.chu_de if (doc.chu_de and doc.chu_de != "N/A") else "Khác"
        chu_de_dict[cd] = chu_de_dict.get(cd, 0) + 1
        
    tb_conf = int((tb_conf / tong_doc * 100)) if tong_doc > 0 else 0
    theo_loai = [{"loai": k, "n": v} for k, v in sorted(loai_dict.items(), key=lambda x: x[1], reverse=True)[:5]]
    theo_chu_de = [{"chuDe": k, "n": v} for k, v in sorted(chu_de_dict.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    # 6. Tạo đoạn phân tích chân trang động (Dynamic Insights Summary)
    most_affected_doc = max(invalid_docs_map.items(), key=lambda x: x[1])[0] if invalid_docs_map else ""
    if luot_vien > 0:
        summary_text = (
            f"{luot_luat_moi}/{luot_vien} lượt viện căn cứ hết hiệu lực phát sinh từ đợt cập nhật văn bản pháp lý "
            f"giai đoạn 2025 tới 2026. Trong đó văn bản '{most_affected_doc}' đang có {max(invalid_docs_map.values())} "
            f"căn cứ cần cập nhật gấp. Càng để lâu, các quy định nội bộ đứng trên căn cứ đã bãi bỏ càng dồn rủi ro."
        )
    else:
        summary_text = (
            "Hiện tại hệ thống đối soát không ghi nhận văn bản nào viện dẫn căn cứ đã hết hiệu lực. "
            "Toàn bộ căn cứ pháp lý trong kho tài liệu đều ở trạng thái an toàn."
        )

    return {
        "insights": {
            "luotVien": luot_vien,
            "thayThe": thay_the_count,
            "baiBo": bai_bo_count,
            "vbNhieuCanCu": vb_nhieu_can_cu,
            "luotLuatMoi": luot_luat_moi,
            "topCanCu": top_can_cu,
            "theoNam": theo_nam,
            "tapTrung": {"theoLoai": theo_loai, "theoChuDe": theo_chu_de},
            "tinCay": {"tb": tb_conf, "tong": tong_doc, "ocr": ocr_count, "duoi80": duoi80_count},
            "summaryText": summary_text
        }
    }



