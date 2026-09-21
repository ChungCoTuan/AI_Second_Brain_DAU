import os
import re

file_path = "e:/AI_Second_Brain_DAU/backend/app/api/endpoints.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update publish_item
publish_pattern = r'(@router\.put\("/review/\{item_type\}/\{item_id\}/publish"\)\s*async def publish_item\(.*?\):.*?)(item\.status = "published"\s*db\.commit\(\)\s*return \{)'
def publish_repl(m):
    return m.group(1) + '''
    action_taken = "Duyệt giữ nguyên"
    
    # Check if there is edited_summary in request (if request exists)
    # The original function signature might not have request, let's keep it simple
    # if we can't extract edited_summary, we just log it as "Duyệt giữ nguyên"
    # Actually, let's just create the AuditTrail
    
    from datetime import datetime
    audit = AuditTrail(
        item_type=item_type,
        item_id=item_id,
        vb=item.vb,
        dieu=item.dieu,
        original_text=item.nguon,
        original_summary=item.tom_tat or "",
        edited_summary=None,
        action="Duyệt giữ nguyên",
        author="Admin",
        timestamp=datetime.now().isoformat()
    )
    db.add(audit)
    
    ''' + m.group(2)
content = re.sub(publish_pattern, publish_repl, content, flags=re.DOTALL)

# 2. Update reject_item
reject_pattern = r'(@router\.put\("/review/\{item_type\}/\{item_id\}/reject"\)\s*async def reject_item\(.*?\):.*?)(item\.status = "rejected"\s*db\.commit\(\)\s*return \{)'
def reject_repl(m):
    return m.group(1) + '''
    from datetime import datetime
    audit = AuditTrail(
        item_type=item_type,
        item_id=item_id,
        vb=item.vb,
        dieu=item.dieu,
        original_text=item.nguon,
        original_summary=item.tom_tat or "",
        edited_summary=None,
        action="Từ chối duyệt",
        author="Admin",
        timestamp=datetime.now().isoformat()
    )
    db.add(audit)
    ''' + m.group(2)
content = re.sub(reject_pattern, reject_repl, content, flags=re.DOTALL)

# 3. Add get_audit_logs if it doesn't exist
if "def get_audit_logs" not in content:
    content += '''

@router.get("/audit/logs")
async def get_audit_logs(db: Session = Depends(get_db)):
    """Returns all audit logs, ordered by timestamp descending."""
    logs = db.query(AuditTrail).order_by(AuditTrail.timestamp.desc()).all()
    log_list = []
    for log in logs:
        log_list.append({
            "id": log.id,
            "item_type": log.item_type,
            "item_id": log.item_id,
            "vb": log.vb,
            "dieu": log.dieu,
            "original_text": log.original_text,
            "original_summary": log.original_summary,
            "edited_summary": log.edited_summary,
            "action": log.action,
            "author": log.author,
            "timestamp": log.timestamp
        })
    return {"logs": log_list}
'''

# 4. Overwrite system/crawl and add new crawler endpoints
crawl_pattern = r'@router\.post\("/system/crawl"\).*?(?=@router|$)'
content = re.sub(crawl_pattern, '', content, flags=re.DOTALL)

content += '''

@router.post("/system/crawl")
def trigger_manual_crawl():
    """Manually triggers the document crawler synchronously."""
    crawl_chinhphu(5) # max 5 files per crawl for demo
    return {"status": "success", "message": "Crawler has finished."}

@router.get("/system/crawled_files")
def get_crawled_files(db: Session = Depends(get_db)):
    """Returns a list of crawled files that have not been processed yet."""
    from ..services.ingestion.crawl_documents import BASE_OUTPUT_DIR
    import os
    
    crawled_pdfs = []
    for root, dirs, files in os.walk(BASE_OUTPUT_DIR):
        for file in files:
            if file.lower().endswith(".pdf"):
                crawled_pdfs.append(file)
                
    processed_docs = db.query(Document.filename).all()
    processed_filenames = [doc[0] for doc in processed_docs]
    
    unprocessed = [f for f in crawled_pdfs if f not in processed_filenames]
    
    return {"unprocessed_files": unprocessed}

class ProcessCrawledRequest(BaseModel):
    filename: str

@router.post("/documents/process_crawled")
async def process_crawled_document(request: ProcessCrawledRequest, db: Session = Depends(get_db)):
    """Processes an already crawled document."""
    from ..services.ingestion.crawl_documents import BASE_OUTPUT_DIR
    import os
    from ..services.pdf_parser import extract_text_from_pdf
    
    filepath = None
    for root, dirs, files in os.walk(BASE_OUTPUT_DIR):
        if request.filename in files:
            filepath = os.path.join(root, request.filename)
            break
            
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found in crawled directory.")
        
    category = os.path.basename(os.path.dirname(filepath))
    source_folder = f"vanban_caotudong/{category}"
    
    try:
        text = extract_text_from_pdf(filepath)
        if not text:
            raise HTTPException(status_code=500, detail="Không thể đọc nội dung file PDF")
            
        result = extractor.process_document(text)
        
        doc = Document(
            filename=request.filename,
            source_folder=source_folder,
            chu_de="N/A",
            co_quan_ban_hanh="Chính phủ",
            status="draft"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        for obl_data in result["nghia_vu"]:
            obl = Obligation(
                document_id=doc.id,
                vb=obl_data.get("vb", request.filename),
                dieu=obl_data.get("dieu", ""),
                loai=obl_data.get("loai", ""),
                chu_the=obl_data.get("chu_the", ""),
                noi_dung=obl_data.get("noi_dung", ""),
                han_chot=obl_data.get("han_chot", ""),
                nguon=obl_data.get("nguon", ""),
                status="pending_review",
                tom_tat=obl_data.get("tom_tat", ""),
                nli_label=obl_data.get("nli_label", "neutral")
            )
            db.add(obl)
            
        for thresh_data in result["con_so_chot"]:
            thresh = Threshold(
                document_id=doc.id,
                vb=thresh_data.get("vb", request.filename),
                dieu=thresh_data.get("dieu", ""),
                gia_tri=thresh_data.get("gia_tri", ""),
                don_vi=thresh_data.get("don_vi", ""),
                doi_tuong=thresh_data.get("doi_tuong", ""),
                nguon=thresh_data.get("nguon", ""),
                status="pending_review",
                tom_tat=thresh_data.get("tom_tat", ""),
                nli_label=thresh_data.get("nli_label", "neutral")
            )
            db.add(thresh)
            
        db.commit()
        return {"status": "success", "message": f"Processed {request.filename} successfully.", "document_id": doc.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
'''

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Endpoints updated successfully")
