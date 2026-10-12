from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import os
import shutil
import random
import re
from ...db.session import get_db
from ...db.models import Document, Obligation, Threshold, DocumentRelation, AuditTrail
from ...services.nlp_pipeline import generate_rag_answer, extractor, classify_text
from ...services.pdf_parser import extract_text_from_pdf, chunk_document
from ...services.ingestion.crawl_documents import crawl_chinhphu, get_sync_status, BASE_OUTPUT_DIR
from ...core.security import get_current_user, get_current_admin
from ...db.models import User

class ExtractRequest(BaseModel):
    text: str

def clean_doc_title(s: Optional[str]) -> str:
    if not s:
        return ""
    return re.sub(r'[\)\.\,\;\:\/\-\s]+$', '', s.strip()).strip()

def norm_doc_key(s: Optional[str]) -> str:
    if not s:
        return ""
    return re.sub(r'[\)\.\,\;\:\/\-\s]+$', '', s.strip()).strip().lower()

def extract_year(text: str) -> str:
    if not text:
        return ""
    m = re.search(r'\b(20[0-2]\d)\b', text)
    if m:
        return m.group(1)
    m = re.search(r'/(20[0-2]\d)/', text)
    if m:
        return m.group(1)
    return ""

router = APIRouter()

class ProcessCrawledRequest(BaseModel):
    filename: str

@router.get("/documents/{document_id:path}/pdf")
async def get_document_pdf(document_id: str, token: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Trả về trực tiếp file PDF của văn bản để trình duyệt hiển thị.
    Có thể truyền token qua query param (?token=...) để xác thực vì khi mở tab mới, 
    trình duyệt sẽ không tự động gửi Header Authorization.
    """
    # 1. Truy vấn văn bản
    # Có thể document_id là int (id) hoặc string (số hiệu / filename)
    document = None
    if document_id.isdigit():
        document = db.query(Document).filter(Document.id == int(document_id)).first()
    
    if not document:
        # Thử tìm theo soHieu (filename)
        document = db.query(Document).filter(
            (Document.filename == document_id) | (Document.filename == f"{document_id}.pdf")
        ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy văn bản")
        
    # 2. Tìm đường dẫn vật lý của file
    source_folder = document.source_folder
    
    # Chuẩn hóa đường dẫn: Đảm bảo có prefix "data" nếu bị thiếu
    # Dùng .replace('\\', '/') để xử lý đường dẫn trên Windows
    if not source_folder.replace("\\", "/").startswith("data/"):
        source_folder = os.path.join("data", source_folder)
        
    filepath = os.path.join(source_folder, document.filename)
    
    if not os.path.exists(filepath):
        # Fallback thử tìm ở thư mục uploads
        fallback_path = os.path.join("data", "uploads", document.filename)
        if os.path.exists(fallback_path):
            filepath = fallback_path
        else:
            raise HTTPException(status_code=404, detail=f"File PDF không tồn tại trên hệ thống: {filepath}")
            
    # 3. Trả về file PDF cho trình duyệt
    return FileResponse(
        filepath, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"inline; filename={document.filename}"}
    )

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
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    """
    Nhận file PDF tải lên, lưu xuống ổ cứng và đưa vào Background Task để xử lý.
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
        
    # Thêm tác vụ bóc tách vào hàng đợi ngầm
    background_tasks.add_task(_run_extraction, file_path, file.filename, "data/uploads", "Khac")
    
    return {
        "status": "success",
        "message": f"Đã lưu {file.filename} và đưa vào hàng đợi xử lý AI ngầm."
    }


@router.get("/topics")
async def get_topics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
    return {"topics": topics}


@router.get("/topics/{topic}/documents")
async def get_documents_by_topic(topic: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
            "ngayKy": doc.ngay_ky or "Không rõ",
            "status": doc.status,
            "chuDe": [doc.chu_de]
        })
        
    return {"documents": documents}


@router.get("/legal-data")
async def get_legal_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
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
    
    # Lấy dữ liệu quan hệ văn bản thực tế
    relations = db.query(DocumentRelation).all()
    doc_dates_map = {d.filename: d.ngay_ky or "" for d in db.query(Document).all()}
    

    vb_tu_chet_map = {}
    su_kien_hieu_luc_map = {}
    events_map = {}
    
    for rel in relations:
        rt = rel.relation_type.lower().strip()
        
        if "thay thế" in rt or "bãi bỏ" in rt:
            # old_doc là văn bản cũ bị thay thế/bãi bỏ (target_doc)
            # new_doc là văn bản mới ban hành làm thay thế/bãi bỏ (source_doc)
            old_doc = clean_doc_title(rel.target_doc)
            new_doc = rel.source_doc
            
            if not old_doc:
                continue
                
            old_key = norm_doc_key(old_doc)
            key = (old_key, new_doc)
            
            ly_do_display = "Bị thay thế toàn bộ" if "thay thế" in rt else (
                "Bị bãi bỏ một phần" if "một phần" in rt else "Bị bãi bỏ toàn bộ"
            )
            raw_type = "thay_the" if "thay thế" in rt else "bai_bo"
            s_date = doc_dates_map.get(new_doc, "")
            nam_val = extract_year(s_date) or extract_year(new_doc) or extract_year(old_doc)
            
            co_quan_parsed, loai_parsed = parse_agency_and_type(old_doc)
            if old_key not in vb_tu_chet_map:
                vb_tu_chet_map[old_key] = {
                    "docId": old_doc,
                    "soHieu": old_doc,
                    "loai": loai_parsed,
                    "coQuan": co_quan_parsed,
                    "nam": nam_val,
                    "rawType": raw_type,
                    "tuNgay": s_date or "2026",
                    "thayBang": [new_doc],
                    "lyDo": ly_do_display,
                    "phamVi": "một phần" if "một phần" in rt else "toàn bộ",
                    "chuyenTiep": [],
                    "nguyenVan": rel.nguyen_van
                }
            else:
                if new_doc not in vb_tu_chet_map[old_key]["thayBang"]:
                    vb_tu_chet_map[old_key]["thayBang"].append(new_doc)
                if not vb_tu_chet_map[old_key].get("nguyenVan") and rel.nguyen_van:
                    vb_tu_chet_map[old_key]["nguyenVan"] = rel.nguyen_van
                
            if key not in su_kien_hieu_luc_map:
                su_kien_hieu_luc_map[key] = {
                    "cu": old_doc,
                    "tenCu": "Văn bản cũ bị thay thế/bãi bỏ",
                    "moi": new_doc,
                    "tenMoi": "Văn bản mới ban hành",
                    "lyDo": ly_do_display,
                    "phamVi": "một phần" if "một phần" in rt else "toàn bộ",
                    "tuNgay": s_date or "Theo hiệu lực",
                    "nam": nam_val,
                    "nguon": rel.nguyen_van or f"Theo văn bản {new_doc}",
                    "docId": new_doc,
                    "rawType": raw_type
                }
            
            # Gộp vào events_map cho Sự kiện thay đổi luật
            if old_key not in events_map:
                events_map[old_key] = {
                    "canCu": old_doc,
                    "thayBang": new_doc,
                    "lyDo": ly_do_display,
                    "rawType": raw_type,
                    "nam": nam_val,
                    "docs": []
                }
            else:
                events_map[old_key]["thayBang"] = new_doc
                events_map[old_key]["lyDo"] = ly_do_display
                if not events_map[old_key].get("nam") and nam_val:
                    events_map[old_key]["nam"] = nam_val
                
        elif rt == "căn cứ":
            old_doc = clean_doc_title(rel.target_doc)
            dep_doc = rel.source_doc
            old_key = norm_doc_key(old_doc)
            
            if not old_key:
                continue
                
            if old_key not in events_map:
                events_map[old_key] = {
                    "canCu": old_doc,
                    "thayBang": None,
                    "lyDo": "được dùng làm căn cứ",
                    "rawType": "can_cu",
                    "nam": extract_year(doc_dates_map.get(dep_doc, "")) or extract_year(dep_doc),
                    "docs": []
                }
            if not any(d["soHieu"] == dep_doc for d in events_map[old_key]["docs"]):
                events_map[old_key]["docs"].append({
                    "soHieu": dep_doc,
                    "loai": "Văn bản"
                })
                
    impact = []
    for e in events_map.values():
        if len(e["docs"]) > 0:
            impact.append({
                "canCu": e["canCu"],
                "thayBang": e["thayBang"],
                "lyDo": e.get("lyDo", ""),
                "dependents": list(e["docs"])
            })
            
    # Sự kiện cảnh báo: Tất cả sự kiện thay đổi luật thực tế trong CSDL
    # Sắp xếp ưu tiên các sự kiện có văn bản nội bộ bị ảnh hưởng lên đầu
    valid_events = [e for e in events_map.values() if e.get("thayBang")]
    valid_events.sort(key=lambda x: (len(x["docs"]), x.get("nam") or ""), reverse=True)
    events = valid_events
            
    vb_sap_chet = []
        
    return {
        "nghiaVu": nghia_vu_list,
        "conSoChot": con_so_chot_list,
        "hanChot": han_chot_list,
        "chuaHieuLuc": chua_hieu_luc_list,
        "vbTuChet": list(vb_tu_chet_map.values()),
        "vbSapChet": vb_sap_chet,
        "events": events,
        "impact": impact,
        "suKienHieuLuc": list(su_kien_hieu_luc_map.values())
    }


@router.get("/impact")
async def get_document_impact(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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


def parse_agency_and_type(doc_name: str) -> tuple[str, str]:
    if not doc_name:
        return ("Cơ quan ban hành nhà nước", "Văn bản")
    s_upper = doc_name.upper()
    
    # Type
    if "THÔNG TƯ" in s_upper or "/TT" in s_upper or "_TT" in s_upper:
        loai = "Thông tư"
    elif "NGHỊ ĐỊNH" in s_upper or "/NĐ" in s_upper or "/ND" in s_upper or "_ND" in s_upper or "_NĐ" in s_upper:
        loai = "Nghị định"
    elif "QUYẾT ĐỊNH" in s_upper or "/QĐ" in s_upper or "/QD" in s_upper or "_QD" in s_upper or "_QĐ" in s_upper:
        loai = "Quyết định"
    elif "LUẬT" in s_upper or "/QH" in s_upper:
        loai = "Luật"
    elif "NGHỊ QUYẾT" in s_upper or "/NQ" in s_upper:
        loai = "Nghị quyết"
    elif "CHỈ THỊ" in s_upper or "/CT" in s_upper:
        loai = "Chỉ thị"
    elif "THÔNG BÁO" in s_upper or "/TB" in s_upper:
        loai = "Thông báo"
    elif "CÔNG VĂN" in s_upper or "/CV" in s_upper:
        loai = "Công văn"
    elif "KẾ HOẠCH" in s_upper or "/KH" in s_upper:
        loai = "Kế hoạch"
    elif "HƯỚNG DẪN" in s_upper or "/HD" in s_upper:
        loai = "Hướng dẫn"
    elif "QUY CHẾ" in s_upper or "_QC" in s_upper:
        loai = "Quy chế"
    else:
        loai = "Văn bản"

    # Agency
    if "BCT" in s_upper:
        co_quan = "Bộ Công Thương"
    elif "BGDĐT" in s_upper or "BGD" in s_upper:
        co_quan = "Bộ Giáo dục và Đào tạo"
    elif "BTC" in s_upper:
        co_quan = "Bộ Tài chính"
    elif "CP" in s_upper or "CHÍNH PHỦ" in s_upper:
        co_quan = "Chính phủ"
    elif "TTG" in s_upper or "THỦ TƯỚNG" in s_upper:
        co_quan = "Thủ tướng Chính phủ"
    elif "BNNMT" in s_upper or "BNN" in s_upper:
        co_quan = "Bộ Nông nghiệp và Môi trường"
    elif "BTNMT" in s_upper:
        co_quan = "Bộ Tài nguyên và Môi trường"
    elif "BQP" in s_upper:
        co_quan = "Bộ Quốc phòng"
    elif "BVHTTDL" in s_upper:
        co_quan = "Bộ Văn hóa, Thể thao và Du lịch"
    elif "NHNN" in s_upper:
        co_quan = "Ngân hàng Nhà nước Việt Nam"
    elif "BXD" in s_upper:
        co_quan = "Bộ Xây dựng"
    elif "BNV" in s_upper:
        co_quan = "Bộ Nội vụ"
    elif "BYT" in s_upper:
        co_quan = "Bộ Y tế"
    elif "BTP" in s_upper:
        co_quan = "Bộ Tư pháp"
    elif "BCA" in s_upper:
        co_quan = "Bộ Công an"
    elif "VKSTC" in s_upper:
        co_quan = "Viện kiểm sát nhân dân tối cao"
    elif "TANDTC" in s_upper:
        co_quan = "Tòa án nhân dân tối cao"
    elif "QH" in s_upper:
        co_quan = "Quốc hội"
    elif "VPCP" in s_upper:
        co_quan = "Văn phòng Chính phủ"
    elif "DAU" in s_upper or "NT" in s_upper:
        co_quan = "Trường Đại học Kiến trúc Đà Nẵng (DAU)"
    else:
        co_quan = "Cơ quan ban hành nhà nước"
        
    return (co_quan, loai)


@router.get("/documents/detail/{so_hieu:path}")
async def get_document_detail(so_hieu: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Trả về chi tiết hồ sơ văn bản (cả văn bản có file trong kho lẫn văn bản ngoại dẫn bị khai tử/thay thế).
    """
    if so_hieu.startswith("bo:"):
        so_hieu = so_hieu[3:]
    elif so_hieu.startswith("truong:"):
        so_hieu = so_hieu[7:]
        
    so_hieu = so_hieu.strip()
    clean_so_hieu = re.sub(r'[\)\.\,\;\:\/\-\s]+$', '', so_hieu).strip()
    
    # 1. Tìm trong bảng Document
    doc = db.query(Document).filter(Document.filename == so_hieu).first()
    if not doc:
        doc = db.query(Document).filter(Document.filename.ilike(clean_so_hieu)).first()
    if not doc:
        doc = db.query(Document).filter(Document.filename.ilike(f"%{clean_so_hieu}%")).first()
        
    doc_dates_map = {d.filename: d.ngay_ky or "" for d in db.query(Document).all()}
    
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
                
        # Lấy Căn cứ mà văn bản này viện dẫn
        can_cu = db.query(DocumentRelation).filter(
            DocumentRelation.source_doc == doc.filename,
            DocumentRelation.relation_type == "căn cứ"
        ).all()
        can_cu_names = list(set([r.target_doc for r in can_cu]))
        
        # Căn cứ đã hết hiệu lực
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
        
        # Văn bản này làm văn bản khác hết hiệu lực (source là doc.filename)
        lam_het_hieu_luc = db.query(DocumentRelation).filter(
            DocumentRelation.source_doc == doc.filename,
            DocumentRelation.relation_type.in_(["bị thay thế", "bị bãi bỏ", "thay thế", "bãi bỏ"])
        ).all()
        thay_the = []
        bai_bo = []
        for r in lam_het_hieu_luc:
            rt = (r.relation_type or "").lower()
            obj = {
                "soHieu": r.target_doc,
                "nguon": r.nguyen_van,
                "phamVi": "một phần" if "một phần" in rt else "toàn bộ"
            }
            if "thay thế" in rt:
                thay_the.append(obj)
            elif "bãi bỏ" in rt:
                bai_bo.append(obj)
                
        # Văn bản này bị văn bản khác làm hết hiệu lực (target là doc.filename)
        bi_het_hieu_luc = db.query(DocumentRelation).filter(
            DocumentRelation.target_doc == doc.filename,
            DocumentRelation.relation_type.in_(["bị thay thế", "bị bãi bỏ", "thay thế", "bãi bỏ"])
        ).all()
        thay_the_boi = []
        for r in bi_het_hieu_luc:
            rt = (r.relation_type or "").lower()
            ly_do_val = "Bị thay thế toàn bộ" if "thay thế" in rt else (
                "Bị bãi bỏ một phần" if "một phần" in rt else "Bị bãi bỏ toàn bộ"
            )
            s_date = doc_dates_map.get(r.source_doc, "")
            thay_the_boi.append({
                "soHieu": r.source_doc,
                "lyDo": ly_do_val,
                "ngayHieuLuc": s_date or "2026",
                "nguon": r.nguyen_van or f"Theo quy định tại văn bản {r.source_doc}"
            })
            
        # Văn bản nội bộ phụ thuộc viện dẫn văn bản này
        dependents = db.query(DocumentRelation).filter(
            DocumentRelation.relation_type == "căn cứ",
            DocumentRelation.target_doc == doc.filename
        ).all()
        van_ban_anh_huong = []
        for dep in dependents:
            van_ban_anh_huong.append({
                "soHieu": dep.source_doc,
                "loai": "Văn bản nội bộ" if dep.source_doc.startswith("NT") else "Văn bản trong kho",
                "nguon": dep.nguyen_van or f"Viện dẫn {doc.filename} làm căn cứ pháp lý"
            })
            
        parsed_cq, parsed_loai = parse_agency_and_type(doc.filename)

        return {
            "type": "truong" if (doc.filename or "").startswith("NT") or "QĐ" in (doc.filename or "") else "bo",
            "data": {
                "soHieu": doc.filename,
                "loai": doc.linh_vuc if doc.linh_vuc and str(doc.linh_vuc).lower() not in ["data", "khac", "khác"] else parsed_loai,
                "coQuan": doc.co_quan_ban_hanh or parsed_cq,
                "ngayKy": doc.ngay_ky or "",
                "ngayBanHanh": doc.ngay_ky or "",
                "nguoiKy": doc.nguoi_ky or "",
                "chucVu": "",
                "hieuLucTu": {
                    "ngay": doc.hieu_luc_tu or "",
                    "nguon": doc.dieu_khoan_hieu_luc_nguyen_van or ""
                },
                "hieuLucDen": doc.hieu_luc_den,
                "status": "Đã hết hiệu lực" if thay_the_boi else (doc.trang_thai_hieu_luc or "Còn hiệu lực"),
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
                "thayTheBoi": thay_the_boi,
                "vanBanAnhHuong": van_ban_anh_huong,
                "canCu": [{"soHieu": name} for name in can_cu_names],
                "conf": doc.conf,
                "ocr": doc.ocr,
                "hasPdf": True
            },
            "items": items
        }

    # 2. Xử lý khi là văn bản pháp luật đối chiếu ngoại dẫn (như Thông tư 26/2026/TT-BCT...)
    target_rels = db.query(DocumentRelation).filter(
        (DocumentRelation.target_doc == so_hieu) |
        (DocumentRelation.target_doc.ilike(f"%{clean_so_hieu}%"))
    ).all()
    
    thay_the_boi = []
    is_replaced = False
    is_repealed_part = False
    is_repealed_all = False
    
    for r in target_rels:
        rt = (r.relation_type or "").lower().strip()
        if "thay thế" in rt or "bãi bỏ" in rt:
            if "thay thế" in rt:
                is_replaced = True
                ly_do_display = "Bị thay thế toàn bộ"
            elif "một phần" in rt:
                is_repealed_part = True
                ly_do_display = "Bị bãi bỏ một phần"
            else:
                is_repealed_all = True
                ly_do_display = "Bị bãi bỏ toàn bộ"
                
            s_date = doc_dates_map.get(r.source_doc, "")
            thay_the_boi.append({
                "soHieu": r.source_doc,
                "lyDo": ly_do_display,
                "ngayHieuLuc": s_date or "2026",
                "nguon": r.nguyen_van or f"Theo điều khoản thi hành của văn bản {r.source_doc}"
            })

    # Lọc trùng thay_the_boi theo soHieu
    seen_sources = set()
    unique_thay_the_boi = []
    for t in thay_the_boi:
        if t["soHieu"] not in seen_sources:
            seen_sources.add(t["soHieu"])
            unique_thay_the_boi.append(t)

    # Tìm văn bản nội bộ viện dẫn văn bản này làm căn cứ
    dependent_rels = db.query(DocumentRelation).filter(
        DocumentRelation.relation_type == "căn cứ",
        (DocumentRelation.target_doc == so_hieu) |
        (DocumentRelation.target_doc.ilike(f"%{clean_so_hieu}%"))
    ).all()
    
    seen_deps = set()
    van_ban_anh_huong = []
    for dep in dependent_rels:
        if dep.source_doc not in seen_deps:
            seen_deps.add(dep.source_doc)
            van_ban_anh_huong.append({
                "soHieu": dep.source_doc,
                "loai": "Văn bản nội bộ" if dep.source_doc.startswith("NT") else "Văn bản trong kho",
                "nguon": dep.nguyen_van or f"Viện dẫn {so_hieu} làm căn cứ ban hành"
            })
            
    co_quan_val, loai_val = parse_agency_and_type(so_hieu)
    year_val = extract_year(so_hieu)
    ngay_ban_hanh = f"Năm {year_val}" if year_val else ""
    
    if is_replaced:
        status_val = "Đã hết hiệu lực (Bị thay thế toàn bộ)"
    elif is_repealed_all:
        status_val = "Đã hết hiệu lực (Bị bãi bỏ toàn bộ)"
    elif is_repealed_part:
        status_val = "Hết hiệu lực một phần (Bị bãi bỏ một phần)"
    elif unique_thay_the_boi:
        status_val = "Đã hết hiệu lực"
    else:
        status_val = "Văn bản đối chiếu"
        
    new_names = [t["soHieu"] for t in unique_thay_the_boi]
    new_names_str = ", ".join(new_names) if new_names else "văn bản mới"
    
    tom_tat_val = (
        f"Văn bản {so_hieu} ({loai_val}) do {co_quan_val} ban hành. "
        f"Theo dữ liệu rà soát hiệu lực của hệ thống, văn bản này {status_val.lower()} bởi {new_names_str}. "
        f"Các quy định, điều khoản thuộc phạm vi bãi bỏ/thay thế không còn giá trị áp dụng trực tiếp. "
    )
    if van_ban_anh_huong:
        tom_tat_val += f"Hiện tại hệ thống ghi nhận {len(van_ban_anh_huong)} văn bản trong trường viện dẫn văn bản này làm căn cứ pháp lý cần rà soát cập nhật."
    else:
        tom_tat_val += "Chưa ghi nhận văn bản nội bộ nào của Trường viện dẫn văn bản này làm căn cứ."
        
    items = []
    for t in unique_thay_the_boi:
        items.append({
            "canCu": so_hieu,
            "thayBang": t["soHieu"],
            "lyDo": t["lyDo"]
        })
        
    return {
        "type": "truong" if so_hieu.startswith("NT") or "QĐ" in so_hieu else "bo",
        "data": {
            "soHieu": so_hieu,
            "loai": loai_val,
            "coQuan": co_quan_val,
            "ngayBanHanh": ngay_ban_hanh,
            "ngayKy": ngay_ban_hanh,
            "nguoiKy": "",
            "chucVu": "",
            "hieuLucTu": None,
            "hieuLucDen": None,
            "status": status_val,
            "tomTat": tom_tat_val,
            "trichYeu": tom_tat_val,
            "ghiChu": f"Đối chiếu hiệu lực tự động từ {len(unique_thay_the_boi)} văn bản mới trong kho.",
            "chuDe": [loai_val],
            "tags": [co_quan_val, loai_val],
            "nghiaVu": [],
            "conSoChot": [],
            "dieuKhoan": [],
            "thayThe": [],
            "baiBo": [],
            "thayTheBoi": unique_thay_the_boi,
            "vanBanAnhHuong": van_ban_anh_huong,
            "canCu": [],
            "hasPdf": False
        },
        "items": items
    }


@router.post("/documents/process_crawled")
def process_crawled_document(request: ProcessCrawledRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    """Processes an already crawled document in the background."""
    from ...services.ingestion.crawl_documents import BASE_OUTPUT_DIR
    import os
    
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
    
    background_tasks.add_task(_run_extraction, filepath, request.filename, source_folder, domain)
        
    return {"status": "success", "message": f"Đã đưa {request.filename} vào hàng đợi xử lý ngầm."}

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
        # Đưa dữ liệu vào Vector DB cho Chatbot RAG
        from ...services.vector_db import vector_db
        from ...services.nlp_pipeline import create_embedding
        
        embeddings = []
        metadatas = []
        if len(articles) > 0:
            for art in articles:
                emb = create_embedding(art["raw"])
                embeddings.append(emb)
                metadatas.append({
                    "id": str(doc.id),
                    "vb": filename,
                    "dieu": art["dieu_so"],
                    "nguon": art["raw"]
                })
        elif text:
            emb = create_embedding(text[:2000])
            embeddings.append(emb)
            metadatas.append({
                "id": str(doc.id),
                "vb": filename,
                "dieu": "Toàn văn",
                "nguon": text[:2000]
            })
            
        if embeddings:
            vector_db.add_texts(embeddings, metadatas)
            
        print(f"[BACKGROUND] Xử lý thành công: {filename}")
        from ...services.notifier import notifier
        notifier.push_sync("update")
        notifier.push_sync(f"success:{filename}")
    except Exception as e:
        db.rollback()
        err_msg = str(e)
        print(f"[BACKGROUND] Lỗi khi xử lý {filename}: {err_msg}")
        
        # Đơn giản hóa thông báo lỗi cho người dùng
        user_msg = "Có lỗi xảy ra trong quá trình phân tích văn bản. Vui lòng thử lại."
        if "tràn bộ nhớ" in err_msg or "Hệ thống đang quá tải" in err_msg:
            user_msg = "Hệ thống đang quá tải bộ nhớ, vui lòng thử lại sau."
        elif "Lỗi AI" in err_msg:
            user_msg = "Có lỗi trong quá trình phân tích thông minh, vui lòng xử lý lại."
        elif "quá lớn" in err_msg or "scan quá lớn" in err_msg:
            user_msg = "Văn bản quá lớn, hệ thống không thể xử lý. Vui lòng chia nhỏ file."
        elif "No such file" in err_msg:
            user_msg = "Không tìm thấy file văn bản trên hệ thống."
            
        from ...services.notifier import notifier
        notifier.push_sync(f"error:{filename}:{user_msg}")
        raise e
    finally:
        db.close()


@router.delete("/documents/crawled/{filename}")
async def delete_crawled_document(filename: str, current_user: User = Depends(get_current_admin)):
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
async def get_rejected_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
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
async def reprocess_rejected_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
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
async def hard_delete_rejected_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
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
