import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from sqlalchemy.orm import Session
from backend.db.models import (
    Document, DocumentChunk, DocumentRelation,
    Summary, Citation, ReviewItem
)
from backend.services.ingestion.preprocess import process_pdf_file
from backend.services.summarization.summarizer import summarize_document

logger = logging.getLogger(__name__)

def run_ingestion_pipeline(db: Session, file_path: Path, chu_de_thu_muc: str = "KHAC") -> Dict[str, Any]:
    """
    Chạy toàn bộ quy trình nạp 1 văn bản:
    1. Trích xuất text, chia đoạn (chunking).
    2. Lưu vào CSDL PostgreSQL (Document, Chunks).
    3. Tóm tắt & Kiểm định NLI.
    4. Lưu kết quả tóm tắt và đẩy vào Review Queue nếu có lỗi NLI.
    """
    logger.info(f"Bắt đầu pipeline xử lý file: {file_path.name}")
    
    # 1. Trích xuất PDF
    doc_meta, chunks_data, relations_data = process_pdf_file(file_path, chu_de_thu_muc)
    doc_id = doc_meta["doc_id"]
    
    # Parse ngày ban hành
    ngay_bh_str = doc_meta.get("ngay_ban_hanh", "2026-01-01")
    try:
        ngay_bh = datetime.strptime(ngay_bh_str, "%Y-%m-%d").date()
    except ValueError:
        ngay_bh = datetime.now().date()
        
    # Xóa văn bản cũ nếu đã tồn tại để nạp lại
    existing_doc = db.query(Document).filter(Document.id == doc_id).first()
    if existing_doc:
        db.delete(existing_doc)
        db.commit()
        
    # 2. Lưu vào DB
    doc_db = Document(
        id=doc_id,
        ten_van_ban=doc_meta.get("ten_van_ban", ""),
        so_hieu=doc_meta.get("so_hieu", ""),
        loai_van_ban=doc_meta.get("loai_van_ban", ""),
        chu_de=chu_de_thu_muc if chu_de_thu_muc != "KHAC" else doc_meta.get("chu_de", "KHAC"),
        pham_vi_ap_dung="GENERAL",
        nguon_du_lieu="upload",
        ngay_ban_hanh=ngay_bh,
        co_quan_ban_hanh=doc_meta.get("co_quan_ban_hanh", ""),
        trang_thai_xuat_ban="pending_review"  # Sẽ cập nhật lại sau
    )
    db.add(doc_db)
    
    # Lưu Chunks
    for c in chunks_data:
        chunk_db = DocumentChunk(
            id=c["chunk_id"],
            document_id=doc_id,
            dieu_khoan=c.get("title", ""),
            noi_dung=c.get("content", ""),
            so_trang=c.get("so_trang", 1)
        )
        db.add(chunk_db)
        
    db.commit()
    
    # Lưu Relations
    for r in relations_data:
        rel_db = DocumentRelation(
            document_id_a=r["document_id_a"],
            document_id_b=r["document_id_b"],
            loai_quan_he=r.get("loai_quan_he", "CAN_CU").lower(),
            diem_tuong_dong=r.get("diem_tuong_dong")
        )
        db.add(rel_db)
        
    db.commit()
    logger.info(f"Đã lưu {len(chunks_data)} chunks cho văn bản {doc_id}")
    
    # 3. Chạy Summarization
    # Truyền vào định dạng dictionary giống với dữ liệu load từ JSONL
    sum_result = summarize_document(doc_id, chunks_data, strategy="hybrid", run_nli_check=True)
    
    # 4. Lưu Summary và Citations
    summary_db = Summary(
        document_id=doc_id,
        noi_dung_tom_tat=doc_meta.get("trich_yeu", ""), # Ta lưu trích yếu chung vào bảng này (hoặc có thể để trống)
        phien_ban_model="hybrid-bartpho-v1"
    )
    db.add(summary_db)
    db.commit()
    db.refresh(summary_db)
    
    review_items_count = 0
    
    for chunk_res in sum_result.get("chunk_results", []):
        for sent_res in chunk_res.get("sentences", []):
            nhan = sent_res.get("nhan_nli", "entailment")
            diem = sent_res.get("diem_faithfulness", 1.0)
            
            cit_db = Citation(
                summary_id=summary_db.id,
                chunk_id=sent_res["chunk_id"],
                cau_tom_tat=sent_res["sentence"],
                diem_faithfulness=diem,
                nhan_nli=nhan
            )
            db.add(cit_db)
            db.commit()
            db.refresh(cit_db)
            
            # Đẩy vào Review Queue nếu NLI gắn cờ
            if nhan in ["contradiction", "neutral"]:
                priority = "high" if nhan == "contradiction" else "medium"
                ri = ReviewItem(
                    citation_id=cit_db.id,
                    document_id=doc_id,
                    nhan_nli=nhan,
                    do_uu_tien=priority,
                    trang_thai="pending"
                )
                db.add(ri)
                review_items_count += 1
                
    # Cập nhật trạng thái tổng
    doc_db.trang_thai_xuat_ban = sum_result.get("trang_thai_xuat_ban", "pending_review").lower()
    db.commit()
    
    logger.info(f"Hoàn tất pipeline {doc_id}. Tạo {review_items_count} review items.")
    
    return {
        "doc_id": doc_id,
        "ten_van_ban": doc_db.ten_van_ban,
        "total_chunks": len(chunks_data),
        "review_items_generated": review_items_count,
        "trang_thai_xuat_ban": doc_db.trang_thai_xuat_ban,
        "message": "Nạp và phân tích văn bản thành công"
    }
