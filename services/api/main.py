"""FastAPI Backend Server cho DAU Second Brain.

Phục vụ dữ liệu thực tế từ data/processed/ (documents, chunks, relations) cho React Frontend.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="DAU Second Brain API",
    description="API Gateway phục vụ dữ liệu văn bản, chunking, quan hệ & kiểm duyệt cho Frontend UI.",
    version="1.0.0",
)

# Thêm CORS Middleware để kết nối React Vite Frontend (port 5173 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
TESTSET_DIR = BASE_DIR / "data" / "testset"


# --- HELPER DATA LOADERS ---
def load_jsonl(file_path: Path) -> List[Dict]:
    items = []
    if not file_path.exists():
        return items
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items


def load_json(file_path: Path) -> List[Dict]:
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_jsonl(file_path: Path, items: List[Dict]):
    with open(file_path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# --- API ENDPOINTS ---
@app.get("/api/health")
def health_check():
    docs = load_jsonl(PROCESSED_DIR / "documents.jsonl")
    chunks = load_jsonl(PROCESSED_DIR / "chunks.jsonl")
    relations = load_jsonl(PROCESSED_DIR / "document_relations.jsonl")
    return {
        "status": "online",
        "documents_count": len(docs),
        "chunks_count": len(chunks),
        "relations_count": len(relations),
    }


@app.get("/api/topics")
def get_topics_summary():
    docs = load_jsonl(PROCESSED_DIR / "documents.jsonl")
    
    topic_meta = {
        "DAO_TAO": {"title": "Đào tạo", "icon": "BookOpen"},
        "TUYEN_SINH": {"title": "Tuyển sinh", "icon": "Users"},
        "TAI_CHINH": {"title": "Tài chính - Học phí", "icon": "Banknote"},
        "NHAN_SU": {"title": "Nhân sự", "icon": "Users"},
        "CO_SO_VAT_CHAT": {"title": "Cơ sở vật chất", "icon": "Building"},
        "KHAC": {"title": "Chưa phân loại / Khác", "icon": "FileQuestion"},
    }
    
    topic_counts = {t: 0 for t in topic_meta}
    for doc in docs:
        t = doc.get("chu_de", "KHAC")
        if t in topic_counts:
            topic_counts[t] += 1
        else:
            topic_counts["KHAC"] += 1

    result = []
    for key, meta in topic_meta.items():
        result.append({
            "id": key,
            "title": meta["title"],
            "count": topic_counts[key],
            "icon": meta["icon"]
        })
    return result


@app.get("/api/documents")
def get_documents(
    topic: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None
):
    docs = load_jsonl(PROCESSED_DIR / "documents.jsonl")
    
    if topic:
        docs = [d for d in docs if d.get("chu_de") == topic]
        
    if status:
        docs = [d for d in docs if d.get("trang_thai_xuat_ban") == status]
        
    if search:
        s = search.lower()
        docs = [
            d for d in docs
            if s in d.get("ten_van_ban", "").lower()
            or s in d.get("so_hieu", "").lower()
            or s in d.get("trich_yeu", "").lower()
        ]

    return docs


@app.get("/api/documents/{doc_id}")
def get_document_detail(doc_id: str):
    docs = load_jsonl(PROCESSED_DIR / "documents.jsonl")
    target_doc = next((d for d in docs if d.get("doc_id") == doc_id), None)
    
    if not target_doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy văn bản!")

    all_chunks = load_jsonl(PROCESSED_DIR / "chunks.jsonl")
    doc_chunks = [c for c in all_chunks if c.get("doc_id") == doc_id]

    all_relations = load_jsonl(PROCESSED_DIR / "document_relations.jsonl")
    doc_relations = [
        r for r in all_relations
        if r.get("document_id_a") == doc_id or r.get("document_id_b") == doc_id
    ]

    return {
        "document": target_doc,
        "chunks": doc_chunks,
        "relations": doc_relations,
    }


@app.get("/api/review")
def get_review_items():
    docs = load_jsonl(PROCESSED_DIR / "documents.jsonl")
    pending_docs = [d for d in docs if d.get("trang_thai_xuat_ban") == "PENDING_REVIEW"]
    
    test_samples = load_json(TESTSET_DIR / "faithfulness_samples.json")
    
    return {
        "pending_count": len(pending_docs),
        "pending_documents": pending_docs,
        "faithfulness_samples": test_samples
    }


class UpdateStatusRequest(BaseModel):
    status: str  # "PUBLISHED", "REJECTED", "PENDING_REVIEW"


@app.put("/api/documents/{doc_id}/status")
def update_document_status(doc_id: str, req: UpdateStatusRequest):
    docs = load_jsonl(PROCESSED_DIR / "documents.jsonl")
    found = False
    for d in docs:
        if d.get("doc_id") == doc_id:
            d["trang_thai_xuat_ban"] = req.status
            found = True
            break
            
    if not found:
        raise HTTPException(status_code=404, detail="Không tìm thấy văn bản!")

    save_jsonl(PROCESSED_DIR / "documents.jsonl", docs)
    return {"message": "Đã cập nhật trạng thái văn bản thành công!", "doc_id": doc_id, "status": req.status}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.api.main:app", host="0.0.0.0", port=8000, reload=True)
