from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import os
import shutil
import random
from ...db.session import get_db
from ...db.models import Document, Obligation, Threshold, DocumentRelation, AuditTrail
from ...services.nlp_pipeline import generate_rag_answer, extractor, classify_text
from ...services.pdf_parser import extract_text_from_pdf, chunk_document
from ...services.ingestion.crawl_documents import crawl_chinhphu, get_sync_status, BASE_OUTPUT_DIR

class ExtractRequest(BaseModel):
    text: str

router = APIRouter()

class ProcessCrawledRequest(BaseModel):
    filename: str

@router.post("/extract")
async def extract_information(request: ExtractRequest) -> Dict[str, Any]:
    """
    Placeholder endpoint for information extraction using Gemini.
    """
    # This will later call llm_service
    return {
        "message": "Information extraction endpoint ready.",
        "input_text_length": len(request.text)
    }


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Nhận file PDF tải lên, đọc text thô, và tạo bản ghi Document.
    Đồng thời sinh dữ liệu mock vào bảng Obligation/Threshold.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file PDF")
        
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 1. Gọi OCR/Parser đọc text
        text_content = extract_text_from_pdf(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi parse PDF: {str(e)}")
        
    # Phân loại chủ đề
    chu_de = classify_text(text_content)
    
    # 2. Tạo bản ghi Document
    new_doc = Document(
        filename=file.filename,
        source_folder="uploads",
        status="in_review",
        chu_de=chu_de
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # 3. Chạy thuật toán chia nhỏ văn bản (Document Structuring)
    articles = chunk_document(text_content)
    
    # 4. Chạy AI / Luật để bóc tách dữ liệu từ các Chunk có thật
    if len(articles) > 0:
        # Chọn ngẫu nhiên 1 Điều làm Nghĩa vụ
        art_obl = random.choice(articles)
        # Sử dụng Extractor để bóc tách thay vì Mock cứng
        obl_info = extractor.extract_obligation(art_obl["raw"])
        
        # Tóm tắt và đánh giá NLI
        obl_tom_tat = extractor.summarize_text(art_obl["raw"])
        obl_nli = extractor.verify_nli(art_obl["raw"], obl_tom_tat)
        # Nếu NLI báo mâu thuẫn (contradiction), đánh dấu pending_review đỏ
        obl_status = "pending_review"
        if obl_nli == "contradiction":
            pass # Vẫn pending_review nhưng UI sẽ hiện đỏ
        
        mock_obl = Obligation(
            document_id=new_doc.id,
            vb=file.filename,
            dieu=art_obl["dieu_so"],
            loai="Nghĩa vụ",
            chu_the=obl_info["chu_the"],
            noi_dung=obl_info["noi_dung"],
            han_chot=obl_info["han_chot"],
            nguon=art_obl["raw"][:1000], # Lấy trọn vẹn text của Điều (giới hạn 1000 ký tự)
            status=obl_status,
            tom_tat=obl_tom_tat,
            nli_label=obl_nli
        )
        db.add(mock_obl)
        
        # Chọn ngẫu nhiên 1 Điều làm Con số chốt
        art_thresh = random.choice(articles)
        thresh_info = extractor.extract_threshold(art_thresh["raw"])
        
        thresh_tom_tat = extractor.summarize_text(art_thresh["raw"])
        thresh_nli = extractor.verify_nli(art_thresh["raw"], thresh_tom_tat)
        
        mock_thresh = Threshold(
            document_id=new_doc.id,
            vb=file.filename,
            dieu=art_thresh["dieu_so"],
            gia_tri=thresh_info["gia_tri"],
            y_nghia=thresh_info["y_nghia"],
            nguon=art_thresh["raw"][:1000],
            status="pending_review",
            tom_tat=thresh_tom_tat,
            nli_label=thresh_nli
        )
        db.add(mock_thresh)
        
        # 5. Khởi động Động cơ Liên kết (Linkage Engine) để tìm các mối quan hệ (Thay thế, Bãi bỏ, Căn cứ)
        relations = extractor.extract_document_relations(text_content, file.filename)
        for rel in relations:
            new_rel = DocumentRelation(
                source_doc=rel["source_doc"],
                target_doc=rel["target_doc"],
                relation_type=rel["relation_type"],
                status="published" # Tạm thời cho lên thẳng để vẽ biểu đồ
            )
            db.add(new_rel)
            
        db.commit()
    else:
        # Fallback nếu không parse được Điều nào
        obl_info = extractor.extract_obligation(text_content[:2000])
        mock_obl = Obligation(
            document_id=new_doc.id,
            vb=file.filename,
            dieu="Toàn văn",
            loai="Nghĩa vụ",
            chu_the=obl_info["chu_the"],
            noi_dung=obl_info["noi_dung"],
            han_chot=obl_info["han_chot"],
            nguon=text_content[:500] + "...",
            status="pending_review"
        )
        db.add(mock_obl)
        db.commit()
    
    return {
        "status": "success",
        "message": f"Tải lên và xử lý thành công file {file.filename}",
        "document_id": new_doc.id
    }


@router.get("/topics")
async def get_topics(db: Session = Depends(get_db)):
    """
    Trả về danh sách các chủ đề và số lượng văn bản của mỗi chủ đề.
    """
    from sqlalchemy import func
    
    # Đếm số lượng văn bản theo từng chủ đề
    results = db.query(Document.chu_de, func.count(Document.id)).filter(
        Document.chu_de != None
    ).group_by(Document.chu_de).all()
    
    topics = []
    for chu_de, count in results:
        topics.append({
            "id": chu_de,
            "name": chu_de,
            "count": count
        })
        
    # Thêm mock chủ đề nếu db trống để UI không bị trắng
    if not topics:
        topics = [
            {"id": "Tuyển sinh", "name": "Tuyển sinh", "count": 0},
            {"id": "Đào tạo", "name": "Đào tạo", "count": 0},
            {"id": "Tài chính", "name": "Tài chính", "count": 0}
        ]
        
    return {"topics": topics}


@router.get("/topics/{topic}/documents")
async def get_documents_by_topic(topic: str, db: Session = Depends(get_db)):
    """
    Lấy danh sách các văn bản thuộc một chủ đề cụ thể.
    """
    docs = db.query(Document).filter(Document.chu_de == topic).all()
    
    documents = []
    for doc in docs:
        documents.append({
            "soHieu": doc.filename,
            "loai": "Văn bản",
            "ngayKy": "2026", # Mock date
            "status": doc.status,
            "chuDe": [doc.chu_de]
        })
        
    return {"documents": documents}


@router.get("/legal-data")
async def get_legal_data(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns the extracted legal data from PostgreSQL Database that are PUBLISHED.
    """
    obligations = db.query(Obligation).filter(Obligation.status == "published").all()
    thresholds = db.query(Threshold).filter(Threshold.status == "published").all()
    
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
        
    # Dữ liệu hạn chót và chưa hiệu lực sẽ được phát triển ở Epic tiếp theo (Trích xuất sự kiện thời gian)
    han_chot_list = []
    chua_hieu_luc_list = []
    
    # Lấy dữ liệu quan hệ văn bản thực tế (Epic 6)
    relations = db.query(DocumentRelation).filter(DocumentRelation.status == "published").all()
    
    vb_tu_chet = []
    su_kien_hieu_luc = []
    events_map = {}
    
    for rel in relations:
        rt = rel.relation_type.lower().strip()
        
        if rt in ["thay thế", "bãi bỏ", "bị thay thế"]:
            # Nếu DB có "bị thay thế", old_doc là source, new là target. Ngược lại.
            if rt == "bị thay thế":
                old_doc = rel.source_doc
                new_doc = rel.target_doc
            else:
                old_doc = rel.target_doc
                new_doc = rel.source_doc
                
            vb_tu_chet.append({
                "docId": old_doc,
                "soHieu": old_doc,
                "loai": "Văn bản",
                "tuNgay": "2026",
                "thayBang": [new_doc],
                "lyDo": f"Bị thay thế toàn bộ",
                "phamVi": "toàn bộ",
                "chuyenTiep": []
            })
            su_kien_hieu_luc.append({
                "cu": old_doc,
                "tenCu": "Văn bản cũ",
                "moi": new_doc,
                "tenMoi": "Văn bản mới",
                "lyDo": f"Bị thay thế toàn bộ",
                "phamVi": "toàn bộ",
                "tuNgay": "Theo hiệu lực",
                "nguon": f"Theo văn bản {new_doc}"
            })
            
            # Gộp vào events_map cho Cây gia phả
            if old_doc not in events_map:
                events_map[old_doc] = {"canCu": old_doc, "thayBang": new_doc, "lyDo": f"bị thay thế", "docs": []}
            else:
                events_map[old_doc]["thayBang"] = new_doc
                events_map[old_doc]["lyDo"] = f"bị thay thế"
                
        elif rt == "căn cứ":
            old_doc = rel.target_doc
            dep_doc = rel.source_doc
            
            if old_doc not in events_map:
                events_map[old_doc] = {"canCu": old_doc, "thayBang": None, "lyDo": "được dùng làm căn cứ", "docs": []}
            if not any(d["soHieu"] == dep_doc for d in events_map[old_doc]["docs"]):
                events_map[old_doc]["docs"].append({
                    "soHieu": dep_doc,
                    "loai": "Văn bản"
                })
                
    events = list(events_map.values())
    
    impact = []
    for e in events:
        impact.append({
            "canCu": e["canCu"],
            "thayBang": e["thayBang"],
            "lyDo": e.get("lyDo", ""),
            "dependents": e["docs"]
        })
            
    # Không còn dữ liệu giả. Nếu DB trống, UI sẽ hiển thị mảng rỗng và hiển thị trạng thái Empty state.
    vb_sap_chet = []
        
    return {
        "nghiaVu": nghia_vu_list,
        "conSoChot": con_so_chot_list,
        "hanChot": han_chot_list,
        "chuaHieuLuc": chua_hieu_luc_list,
        "vbTuChet": vb_tu_chet,
        "vbSapChet": vb_sap_chet,
        "events": events,
        "impact": impact,
        "suKienHieuLuc": su_kien_hieu_luc
    }


@router.get("/impact")
async def get_document_impact(db: Session = Depends(get_db)):
    """
    Trả về dữ liệu cây văn bản (impact) dựa trên các sự kiện trong CSDL.
    """
    impacts = []
    # Tìm các sự kiện thay thế
    replaced_events = db.query(DocumentRelation).filter(DocumentRelation.relation_type == "bị thay thế").all()
    
    for event in replaced_events:
        # Tìm các văn bản phụ thuộc (căn cứ vào văn bản cũ)
        dependents = db.query(DocumentRelation).filter(
            DocumentRelation.target_doc == event.source_doc,
            DocumentRelation.relation_type == "căn cứ"
        ).all()
        
        impacts.append({
            "canCu": event.source_doc,
            "thayBang": event.target_doc,
            "lyDo": event.relation_type,
            "dependents": [{"docId": str(dep.id), "soHieu": dep.source_doc, "loai": "Văn bản"} for dep in dependents]
        })
        
    return {"impact": impacts}


@router.get("/documents/detail/{so_hieu:path}")
async def get_document_detail(so_hieu: str, db: Session = Depends(get_db)):
    """
    Trả về chi tiết hồ sơ văn bản.
    """
    # TODO: Khi bảng Document hoàn thiện, sẽ query lấy chi tiết tại đây.
    # Hiện tại trả về rỗng để xoá sạch dữ liệu giả.
    return {
        "type": "truong" if "QĐ" in so_hieu else "bo",
        "data": {
            "soHieu": so_hieu,
            "loai": "Văn bản",
            "coQuan": "",
            "ngayBanHanh": "",
            "nguoiKy": "",
            "hieuLucTu": None,
            "trichYeu": "Đang cập nhật",
            "thayThe": [],
            "baiBo": [],
            "canCu": [],
            "dieuKhoan": [],
            "nghiaVu": [],
            "conSoChot": []
        }
    }

    # 1. Tra cứu các văn bản liên quan mà văn bản này CĂN CỨ
    can_cu = db.query(DocumentRelation).filter(
        DocumentRelation.source_doc == so_hieu,
        DocumentRelation.relation_type == "căn cứ"
    ).all()
    
    # 2. Kiểm tra xem các căn cứ này có bị thay thế/bãi bỏ không
    can_cu_names = [r.target_doc for r in can_cu]
    het_hieu_luc = db.query(DocumentRelation).filter(
        DocumentRelation.source_doc.in_(can_cu_names),
        DocumentRelation.relation_type.in_(["bị thay thế", "bị bãi bỏ"])
    ).all()
    
    items = []
    for h in het_hieu_luc:
        items.append({
            "canCu": h.source_doc,
            "thayBang": h.target_doc,
            "lyDo": h.relation_type
        })
        
    return {
        "type": "truong",
        "data": {
            "soHieu": so_hieu,
            "loai": "Văn bản",
            "coQuan": "",
            "ngayKy": "",
            "hieuLucTu": "",
            "hieuLucDen": None,
            "status": "Còn hiệu lực",
            "conf": 0.98,
            "ocr": True,
            "tomTat": "Đang cập nhật",
            "chuDe": [],
            "tags": []
        },
        "items": items
    }


@router.get("/topics")
async def get_topics(db: Session = Depends(get_db)):
    """
    Trả về danh sách các chủ đề (mock động).
    """
    return {
        "topics": []
    }


@router.get("/topics/{topic_id}/documents")
async def get_topic_documents(topic_id: str, db: Session = Depends(get_db)):
    """
    Trả về danh sách văn bản của một chủ đề.
    """
    # Xoá mock data, trả về mảng rỗng chờ implement thực tế
    docs = []
    return {"documents": docs}


@router.post("/documents/process_crawled")
async def process_crawled_document(request: ProcessCrawledRequest, db: Session = Depends(get_db)):
    """Processes an already crawled document."""
    from ...services.ingestion.crawl_documents import BASE_OUTPUT_DIR
    import os
    from ...services.pdf_parser import extract_text_from_pdf
    
    filepath = None
    for root, dirs, files in os.walk(BASE_OUTPUT_DIR):
        if request.filename in files:
            filepath = os.path.join(root, request.filename)
            break
            
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found in crawled directory.")
        
    category = os.path.basename(os.path.dirname(filepath))
    domain = os.path.basename(os.path.dirname(os.path.dirname(filepath)))
    if domain == "vanban_caotudong":
        domain = "Giáo dục" # Fallback for old crawler structure
        source_folder = f"vanban_caotudong/{category}"
    else:
        source_folder = f"vanban_caotudong/{domain}/{category}"
    
    try:
        text = extract_text_from_pdf(filepath)
        if not text:
            raise HTTPException(status_code=500, detail="Không thể đọc nội dung file PDF")
            
        # 3. Chạy thuật toán chia nhỏ văn bản (Document Structuring)
        from ...services.pdf_parser import chunk_document
        import random
        
        articles = chunk_document(text)
        
        domain_display = {
            "Giao_duc": "Giáo dục",
            "Tai_chinh": "Tài chính",
            "Nhan_su": "Nhân sự",
            "Khoa_hoc": "Khoa học",
            "Hanh_chinh": "Hành chính",
            "Phap_luat_khung": "Pháp luật khung",
            "Khac": "Khác"
        }.get(domain, domain)
        
        doc = Document(
            filename=request.filename,
            source_folder=source_folder,
            linh_vuc=domain_display,
            chu_de="N/A",
            co_quan_ban_hanh="Chính phủ",
            status="draft"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # 4. Chạy AI / Luật để bóc tách dữ liệu từ các Chunk có thật
        if len(articles) > 0:
            # Chọn ngẫu nhiên 1 Điều làm Nghĩa vụ
            art_obl = random.choice(articles)
            obl_info = extractor.extract_obligation(art_obl["raw"])
            
            obl_tom_tat = extractor.summarize_text(art_obl["raw"])
            obl_nli = extractor.verify_nli(art_obl["raw"], obl_tom_tat)
            obl_status = "pending_review"
            
            mock_obl = Obligation(
                document_id=doc.id,
                vb=request.filename,
                dieu=art_obl["dieu_so"],
                loai="Nghĩa vụ",
                chu_the=obl_info["chu_the"],
                noi_dung=obl_info["noi_dung"],
                han_chot=obl_info["han_chot"],
                nguon=art_obl["raw"][:1000],
                status=obl_status,
                tom_tat=obl_tom_tat,
                nli_label=obl_nli
            )
            db.add(mock_obl)
            
            # Chọn ngẫu nhiên 1 Điều làm Con số chốt
            art_thresh = random.choice(articles)
            thresh_info = extractor.extract_threshold(art_thresh["raw"])
            
            thresh_tom_tat = extractor.summarize_text(art_thresh["raw"])
            thresh_nli = extractor.verify_nli(art_thresh["raw"], thresh_tom_tat)
            
            mock_thresh = Threshold(
                document_id=doc.id,
                vb=request.filename,
                dieu=art_thresh["dieu_so"],
                gia_tri=thresh_info["gia_tri"],
                y_nghia=thresh_info.get("y_nghia", ""),
                nguon=art_thresh["raw"][:1000],
                status="pending_review",
                tom_tat=thresh_tom_tat,
                nli_label=thresh_nli
            )
            db.add(mock_thresh)
            
            # 5. Khởi động Động cơ Liên kết
            relations = extractor.extract_document_relations(text, request.filename)
            for rel in relations:
                new_rel = DocumentRelation(
                    source_doc=rel["source_doc"],
                    target_doc=rel["target_doc"],
                    relation_type=rel["relation_type"],
                    status="published"
                )
                db.add(new_rel)
                
            db.commit()
        else:
            # Fallback nếu không parse được Điều nào
            obl_info = extractor.extract_obligation(text[:2000])
            mock_obl = Obligation(
                document_id=doc.id,
                vb=request.filename,
                dieu="Toàn văn",
                loai="Nghĩa vụ",
                chu_the=obl_info["chu_the"],
                noi_dung=obl_info["noi_dung"],
                han_chot=obl_info["han_chot"],
                nguon=text[:1000],
                status="pending_review"
            )
            db.add(mock_obl)
            db.commit()
            
        return {"status": "success", "message": f"Processed {request.filename} successfully.", "document_id": doc.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

