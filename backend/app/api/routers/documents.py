from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
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
        
    existing_doc = db.query(Document).filter(Document.filename == file.filename).first()
    if existing_doc:
        raise HTTPException(status_code=400, detail="Văn bản với tên file này đã tồn tại trong hệ thống. Vui lòng đổi tên file hoặc kiểm tra lại hệ thống.")
        
    upload_dir = "data/uploads"
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
    
    # Bóc tách Siêu dữ liệu (Metadata) & Tóm tắt
    metadata = extractor.extract_document_metadata(text_content)
    tom_tat_toan_van = extractor.summarize_text(text_content)
    
    # 2. Tạo bản ghi Document
    new_doc = Document(
        filename=file.filename,
        source_folder="data/uploads",
        status="in_review",
        chu_de=chu_de,
        co_quan_ban_hanh=metadata.get("co_quan_ban_hanh", ""),
        ngay_ky=metadata.get("ngay_ky", ""),
        nguoi_ky=metadata.get("nguoi_ky", ""),
        hieu_luc_tu=metadata.get("hieu_luc_tu", ""),
        tags=metadata.get("tags", ""),
        tom_tat=tom_tat_toan_van
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
                status="published", # Tạm thời cho lên thẳng để vẽ biểu đồ
                nguyen_van=rel.get("nguyen_van", "")
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
    
    topics_dict = {}
    for chu_de, count in results:
        # Gom nhóm N/A và None thành "Khác"
        name = "Khác" if not chu_de or chu_de.strip().upper() == "N/A" else chu_de
        if name in topics_dict:
            topics_dict[name] += count
        else:
            topics_dict[name] = count
            
    topics = []
    for name, count in topics_dict.items():
        topics.append({
            "id": name,
            "name": name,
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
    if topic == "Khác":
        from sqlalchemy import or_
        docs = db.query(Document).filter(
            or_(Document.chu_de == "Khác", Document.chu_de == "N/A", Document.chu_de == None)
        ).all()
    else:
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
        
    han_chot_obligations = db.query(Obligation).filter(
        Obligation.han_chot.isnot(None),
        Obligation.han_chot != "",
        Obligation.status == "published"
    ).all()
    
    han_chot_list = []
    for nv in han_chot_obligations:
        han_chot_list.append({
            "hanChot": nv.han_chot,
            "noiDung": nv.noi_dung,
            "vb": nv.vb,
            "dieu": nv.dieu,
            "loai": nv.loai,
            "chuThe": nv.chu_the,
            "nguon": nv.nguon
        })
        
    chua_hieu_luc_docs = db.query(Document).filter(
        Document.trang_thai_hieu_luc == "Chưa có hiệu lực",
        Document.status == "published"
    ).all()
    
    chua_hieu_luc_list = []
    for doc in chua_hieu_luc_docs:
        chua_hieu_luc_list.append({
            "ngay": doc.hieu_luc_tu,
            "trichYeu": doc.tom_tat or doc.filename,
            "soHieu": doc.filename,
            "loai": "hiệu lực",
            "nguon": f"Theo dữ liệu hiệu lực của văn bản {doc.filename}"
        })
    
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
                "chuyenTiep": [],
                "nguyenVan": rel.nguyen_van
            })
            su_kien_hieu_luc.append({
                "cu": old_doc,
                "tenCu": "Văn bản cũ",
                "moi": new_doc,
                "tenMoi": "Văn bản mới",
                "lyDo": f"Bị thay thế toàn bộ",
                "phamVi": "toàn bộ",
                "tuNgay": "Theo hiệu lực",
                "nguon": f"Theo văn bản {new_doc}",
                "nguyenVan": rel.nguyen_van
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
                
    events = []
    impact = []
    
    for e in events_map.values():
        # -- Đồ thị ảnh hưởng (impact): Lấy TOÀN BỘ dây chuyền phụ thuộc --
        if len(e["docs"]) > 0:
            impact.append({
                "canCu": e["canCu"],
                "thayBang": e["thayBang"],
                "lyDo": e.get("lyDo", ""),
                "dependents": list(e["docs"]) # clone mảng docs
            })
            
        # -- Sự kiện cảnh báo (events): Chỉ lấy các dây chuyền có văn bản chưa rà soát (draft) --
        valid_docs = []
        for d in e["docs"]:
            so_hieu = d["soHieu"]
            # Kiểm tra xem văn bản này có Obligation hoặc Threshold nào ở trạng thái "draft" không
            has_draft_obl = db.query(Obligation).filter(Obligation.vb == so_hieu, Obligation.status == "draft").first()
            has_draft_thresh = db.query(Threshold).filter(Threshold.vb == so_hieu, Threshold.status == "draft").first()
            
            if has_draft_obl or has_draft_thresh:
                valid_docs.append(d)
                
        # Nếu có ít nhất 1 văn bản cần rà soát thì mới giữ lại sự kiện cảnh báo này
        if len(valid_docs) > 0:
            event_obj = dict(e)
            event_obj["docs"] = valid_docs
            events.append(event_obj)
            
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
    # Frontend đôi khi gửi kèm prefix "bo:" hoặc "truong:" để điều hướng giao diện cũ.
    # Ta cần cắt nó đi để khớp với filename trong DB.
    if so_hieu.startswith("bo:"):
        so_hieu = so_hieu[3:]
    elif so_hieu.startswith("truong:"):
        so_hieu = so_hieu[7:]
        
    doc = db.query(Document).filter(Document.filename == so_hieu).first()
    
    if doc:
        nghia_vu = []
        for nv in doc.obligations:
            if nv.status == 'published':
                nghia_vu.append({
                    "dieu": nv.dieu,
                    "loai": nv.loai,
                    "noiDung": nv.noi_dung,
                    "hanChot": nv.han_chot,
                    "nguon": nv.nguon
                })
        
        con_so = []
        for cs in doc.thresholds:
            if cs.status == 'published':
                con_so.append({
                    "dieu": cs.dieu,
                    "giaTri": cs.gia_tri,
                    "yNghia": cs.y_nghia,
                    "nguon": cs.nguon
                })
                
        # Lấy Căn cứ đã hết hiệu lực
        can_cu = db.query(DocumentRelation).filter(
            DocumentRelation.source_doc == doc.filename,
            DocumentRelation.relation_type == "căn cứ"
        ).all()
        
        can_cu_names = [r.target_doc for r in can_cu]
        items = []
        if can_cu_names:
            het_hieu_luc = db.query(DocumentRelation).filter(
                DocumentRelation.source_doc.in_(can_cu_names),
                DocumentRelation.relation_type.in_(["bị thay thế", "bị bãi bỏ"])
            ).all()
            
            for h in het_hieu_luc:
                items.append({
                    "canCu": h.source_doc,
                    "thayBang": h.target_doc,
                    "lyDo": h.relation_type
                })
        
        # Văn bản này làm văn bản khác hết hiệu lực (thay thế, bãi bỏ)
        # old_doc là source, new_doc (văn bản hiện tại) là target
        lam_het_hieu_luc = db.query(DocumentRelation).filter(
            DocumentRelation.target_doc == doc.filename,
            DocumentRelation.relation_type.in_(["bị thay thế", "bị bãi bỏ", "thay thế", "bãi bỏ"])
        ).all()
        
        thay_the = []
        bai_bo = []
        for r in lam_het_hieu_luc:
            rt = r.relation_type.lower()
            obj = {
                "soHieu": r.source_doc,
                "nguon": r.nguyen_van
            }
            if "thay thế" in rt:
                thay_the.append(obj)
            elif "bãi bỏ" in rt:
                bai_bo.append(obj)

        return {
            "type": "truong",
            "data": {
                "soHieu": doc.filename,
                "loai": doc.linh_vuc or "Văn bản",
                "coQuan": doc.co_quan_ban_hanh or "",
                "ngayKy": doc.ngay_ky or "",
                "ngayBanHanh": doc.ngay_ky or "",
                "nguoiKy": doc.nguoi_ky or "",
                "chucVu": "",
                "hieuLucTu": {
                    "ngay": doc.hieu_luc_tu or "",
                    "nguon": doc.dieu_khoan_hieu_luc_nguyen_van or ""
                },
                "hieuLucDen": doc.hieu_luc_den,
                "status": doc.trang_thai_hieu_luc or "Còn hiệu lực",
                "tomTat": doc.tom_tat or "",
                "trichYeu": doc.tom_tat or "",
                "ghiChu": doc.ghi_chu or "",
                "chuDe": [doc.chu_de] if doc.chu_de else [],
                "tags": doc.tags.split(',') if doc.tags else [],
                "nghiaVu": nghia_vu,
                "conSoChot": con_so,
                "dieuKhoan": doc.muc_luc_dieu_khoan or [],
                "thayThe": thay_the,
                "baiBo": bai_bo,
                "canCu": [{"soHieu": name} for name in can_cu_names],
                "conf": doc.conf,
                "ocr": doc.ocr
            },
            "items": items
        }
    
    # Fallback nếu không tìm thấy trong DB thì trả về rỗng để xoá sạch dữ liệu giả.
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



@router.post("/documents/process_crawled")
def process_crawled_document(request: ProcessCrawledRequest, db: Session = Depends(get_db)):
    """Processes an already crawled document synchronously to block the frontend."""
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
        domain = "Giáo dục"
        source_folder = f"vanban_caotudong/{category}"
    else:
        source_folder = f"vanban_caotudong/{domain}/{category}"
    
    try:
        _run_extraction(filepath, request.filename, source_folder, domain)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"status": "success", "message": f"Đã xử lý xong {request.filename}."}

def _run_extraction(filepath: str, filename: str, source_folder: str, domain: str):
    """Hàm chạy ngầm trong background thread - không chặn event loop của FastAPI."""
    import random
    from ...db.session import SessionLocal
    from ...db.models import Document, Obligation, Threshold, DocumentRelation
    from ...services.pdf_parser import extract_text_from_pdf, chunk_document
    from ...services.nlp_pipeline import extractor, classify_text
    
    db = SessionLocal()
    try:
        if db.query(Document).filter(Document.filename == filename).first():
            print(f"[BACKGROUND] Bỏ qua xử lý, văn bản đã tồn tại: {filename}")
            return
            
        text = extract_text_from_pdf(filepath)
        if not text:
            print(f"[BACKGROUND] Không thể đọc nội dung file: {filename}")
            return
        
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
        
        metadata = extractor.extract_document_metadata(text)
        tom_tat_toan_van = extractor.summarize_text(text)
        chu_de = classify_text(text)
        
        doc = Document(
            filename=filename,
            source_folder=source_folder,
            linh_vuc=domain_display,
            chu_de=chu_de,
            co_quan_ban_hanh=metadata.get("co_quan_ban_hanh", "Chính phủ"),
            ngay_ky=metadata.get("ngay_ky", ""),
            nguoi_ky=metadata.get("nguoi_ky", ""),
            hieu_luc_tu=metadata.get("hieu_luc_tu", ""),
            tags=metadata.get("tags", ""),
            tom_tat=tom_tat_toan_van,
            status="draft"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        if len(articles) > 0:
            art_obl = random.choice(articles)
            obl_info = extractor.extract_obligation(art_obl["raw"])
            obl_tom_tat = extractor.summarize_text(art_obl["raw"])
            obl_nli = extractor.verify_nli(art_obl["raw"], obl_tom_tat)
            
            db.add(Obligation(
                document_id=doc.id,
                vb=filename,
                dieu=art_obl["dieu_so"],
                loai="Nghĩa vụ",
                chu_the=obl_info["chu_the"],
                noi_dung=obl_info["noi_dung"],
                han_chot=obl_info["han_chot"],
                nguon=art_obl["raw"][:1000],
                status="pending_review",
                tom_tat=obl_tom_tat,
                nli_label=obl_nli
            ))
            
            art_thresh = random.choice(articles)
            thresh_info = extractor.extract_threshold(art_thresh["raw"])
            thresh_tom_tat = extractor.summarize_text(art_thresh["raw"])
            thresh_nli = extractor.verify_nli(art_thresh["raw"], thresh_tom_tat)
            
            db.add(Threshold(
                document_id=doc.id,
                vb=filename,
                dieu=art_thresh["dieu_so"],
                gia_tri=thresh_info["gia_tri"],
                y_nghia=thresh_info.get("y_nghia", ""),
                nguon=art_thresh["raw"][:1000],
                status="pending_review",
                tom_tat=thresh_tom_tat,
                nli_label=thresh_nli
            ))
            
            relations = extractor.extract_document_relations(text, filename)
            for rel in relations:
                db.add(DocumentRelation(
                    source_doc=rel["source_doc"],
                    target_doc=rel["target_doc"],
                    relation_type=rel["relation_type"],
                    status="published",
                    nguyen_van=rel.get("nguyen_van", "")
                ))
            db.commit()
        else:
            obl_info = extractor.extract_obligation(text[:2000])
            db.add(Obligation(
                document_id=doc.id,
                vb=filename,
                dieu="Toàn văn",
                loai="Nghĩa vụ",
                chu_the=obl_info["chu_the"],
                noi_dung=obl_info["noi_dung"],
                han_chot=obl_info["han_chot"],
                nguon=text[:1000],
                status="pending_review"
            ))
            db.commit()
        
        print(f"[BACKGROUND] Xử lý thành công: {filename}")
        from ...services.notifier import notifier
        notifier.push_sync("update")
    except Exception as e:
        db.rollback()
        print(f"[BACKGROUND] Lỗi khi xử lý {filename}: {e}")
        raise e
    finally:
        db.close()


@router.delete("/documents/crawled/{filename}")
async def delete_crawled_document(filename: str):
    """Xóa một file đã được cào về nhưng chưa xử lý."""
    from ...services.ingestion.crawl_documents import BASE_OUTPUT_DIR
    import os
    
    filepath = None
    for root, dirs, files in os.walk(BASE_OUTPUT_DIR):
        if filename in files:
            filepath = os.path.join(root, filename)
            break
            
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found in crawled directory.")
        
    try:
        os.remove(filepath)
        from ...services.notifier import notifier
        notifier.push_sync("update")
        return {"status": "success", "message": f"Deleted {filename} successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể xoá file: {str(e)}")

@router.get("/documents/rejected")
async def get_rejected_documents(db: Session = Depends(get_db)):
    """Trả về danh sách các văn bản bị từ chối."""
    docs = db.query(Document).filter(Document.status == "rejected").all()
    documents = []
    for doc in docs:
        documents.append({
            "id": doc.id,
            "soHieu": doc.filename,
            "loai": doc.linh_vuc or "Khác",
            "ngayKy": doc.ngay_ky or "N/A",
            "chuDe": [doc.chu_de] if doc.chu_de else [],
            "status": doc.status
        })
    return {"documents": documents}

def _find_physical_file(filename: str, source_folder: str) -> str:
    import os
    possible_paths = [
        os.path.join(source_folder, filename),
        os.path.join("data", source_folder, filename),
        os.path.join("data", "uploads", filename),
        os.path.join("data", "vanban_caotudong", filename)
    ]
    if os.path.exists(os.path.join("data", "vanban_caotudong")):
        for root, _, files in os.walk(os.path.join("data", "vanban_caotudong")):
            if filename in files:
                possible_paths.append(os.path.join(root, filename))
                
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None

@router.post("/documents/{doc_id}/reprocess")
async def reprocess_rejected_document(doc_id: int, db: Session = Depends(get_db)):
    """Đưa văn bản bị từ chối về lại tab Tải tài liệu bằng cách xóa DB và di chuyển file."""
    import os
    import shutil
    from ...services.ingestion.crawl_documents import BASE_OUTPUT_DIR
    
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    filename = doc.filename
    source_folder = doc.source_folder
    filepath = _find_physical_file(filename, source_folder)
    
    # 1. Move file back to crawled dir (BASE_OUTPUT_DIR)
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
    new_filepath = os.path.join(BASE_OUTPUT_DIR, filename)
    
    if filepath and os.path.exists(filepath):
        try:
            shutil.move(filepath, new_filepath)
        except Exception as e:
            print(f"Lỗi khi di chuyển file: {e}")
    
    # 2. Xóa các AuditTrails liên quan đến file này
    db.query(AuditTrail).filter(AuditTrail.vb == filename).delete()
    
    # 3. Xóa Document (các bảng liên kết sẽ bị xóa nhờ cascade)
    for d in db.query(Document).filter(Document.filename == filename).all():
        db.delete(d)
    db.commit()
    
    return {"status": "success", "message": f"Đã chuyển {filename} về hàng chờ xử lý."}

@router.delete("/documents/{doc_id}/hard_delete")
async def hard_delete_rejected_document(doc_id: int, db: Session = Depends(get_db)):
    """Xóa vĩnh viễn văn bản bị từ chối khỏi DB và ổ cứng."""
    import os
    
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    filename = doc.filename
    filepath = _find_physical_file(filename, doc.source_folder)
    
    # 1. Xóa file vật lý
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Lỗi khi xóa file: {e}")
            
    # 2. Xóa các AuditTrails liên quan
    db.query(AuditTrail).filter(AuditTrail.vb == filename).delete()
    
    # 3. Xóa Document
    for d in db.query(Document).filter(Document.filename == filename).all():
        db.delete(d)
    db.commit()
    
    return {"status": "success", "message": f"Đã xóa vĩnh viễn {filename}."}
