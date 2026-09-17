"""DAU Second Brain — FastAPI Backend REST API.

Cung cấp các endpoints cho Frontend React:
  - POST /api/query                    : RAG Query với Citations & NLI check
  - GET  /api/documents                : Danh sách văn bản (phân trang, search, filter)
  - GET  /api/documents/{doc_id}       : Chi tiết văn bản & danh sách chunks
  - POST /api/publish/{doc_id}         : Duyệt / xuất bản văn bản
  - POST /api/summarize/{doc_id}       : Tóm tắt văn bản (BARTpho/TextRank + NLI check)
  - GET  /api/stats                    : Thống kê số lượng văn bản, chunks, trạng thái
  - GET  /api/health                   : Health check
  - POST /api/admin/reset-nli          : Reset NLI Checker singleton
  - POST /api/admin/reset-summarizer   : Reset Abstractive Summarizer singleton
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from fastapi import Depends, FastAPI, HTTPException, Query, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Thêm backend directory vào sys.path để import các services
BACKEND_DIR = Path(__file__).parent.parent
ROOT_DIR = BACKEND_DIR.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

logger = logging.getLogger("dau_brain_api")

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager để warm-up RAG Vector Store khi uvicorn khởi động."""
    logger.info("🚀 Đang khởi động FastAPI Backend Server...")
    try:
        from services.retrieval.rag_chain import warmup_rag
        warmup_rag(index_path=str(INDEX_PATH))
    except Exception as e:
        logger.warning(f"⚠️ Warmup RAG thất bại khi startup: {e}")
    yield
    logger.info("🛑 Đang tắt FastAPI Backend Server...")


app = FastAPI(
    title="DAU Second Brain API",
    description="REST API server kết nối RAG & NLI Backend với React Frontend",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Paths ────────────────────────────────────────────────────────────────────
DOCS_PATH = ROOT_DIR / "data" / "processed" / "documents.jsonl"
CHUNKS_PATH = ROOT_DIR / "data" / "processed" / "chunks.jsonl"
INDEX_PATH = ROOT_DIR / "data" / "vector_db" / "faiss_index"


# ── DB Dependency ─────────────────────────────────────────────────────────────
def get_db():
    """FastAPI Dependency: SQLAlchemy Session — auto-close sau mỗi request."""
    try:
        from db.session import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"DB session không khả dụng: {e}. Các endpoint dùng DB sẽ fallback.")
        yield None


# ── Helpers ──────────────────────────────────────────────────────────────────
def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return items


# ── Pydantic Models ──────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str = Field(..., description="Câu hỏi cần tra cứu pháp quy")
    k: int = Field(default=5, ge=1, le=20, description="Số lượng chunk lấy từ FAISS")
    run_nli: bool = Field(default=True, description="Có kiểm tra NLI faithfulness không")
    fast_nli: bool = Field(default=True, description="Dùng Fast Rule-Based NLI (<1ms) cho phản hồi siêu tốc")


class CitationItem(BaseModel):
    index: int
    chunk_id: str
    doc_id: str
    so_hieu: str
    ten_van_ban: str
    dieu_khoan: str
    so_trang: int
    content_preview: str


class QueryResponse(BaseModel):
    answer: Optional[str] = None
    citations: List[CitationItem] = []
    message: str = "OK"
    nli_status: str = "SKIPPED"
    nli_detail: Optional[Dict[str, Any]] = None


class ReviewActionRequest(BaseModel):
    action: str = Field(..., description="Hành động: 'approve', 'edit', hoặc 'reject'")
    edited_sentence: Optional[str] = Field(default=None, description="Câu chỉnh sửa (nếu action='edit')")
    reviewer_id: str = Field(default="can_bo_dao_tao", description="Mã cán bộ thực hiện rà soát")


class SummarizeRequest(BaseModel):
    strategy: str = Field(
        default="hybrid",
        description="Chiến lược tóm tắt: 'extractive' (TextRank), 'abstractive' (BARTpho/ViT5), 'hybrid' (tự động fallback)",
    )
    run_nli: bool = Field(default=True, description="Có chạy NLI check từng câu sau abstractive không")
    max_chunks: Optional[int] = Field(default=None, description="Giới hạn số chunk xử lý (None = tất cả)")


class SentenceResult(BaseModel):
    sentence: str
    chunk_id: str
    method: str
    nhan_nli: str
    diem_faithfulness: Optional[float] = None
    publish_action: str


class ChunkSummaryResult(BaseModel):
    chunk_id: str
    doc_id: str
    sentences: List[SentenceResult]
    overall_action: str
    trang_thai_xuat_ban: str
    has_contradiction: bool = False
    has_neutral: bool = False
    strategy_used: str
    nli_stats: Dict[str, int] = {}


class SummarizeResponse(BaseModel):
    doc_id: str
    ten_van_ban: str
    so_hieu: str
    strategy: str
    overall_action: str
    trang_thai_xuat_ban: str
    total_chunks: int
    total_sentences: int
    strategies_used: List[str] = []
    avg_faithfulness: Optional[float] = None
    nli_stats: Dict[str, int] = {}
    chunk_results: List[ChunkSummaryResult] = []


# ── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/review/queue", summary="Hàng đợi Rà soát (UC-04)")
def get_review_items(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status: str = Query(default="pending", description="Lọc theo trang_thai: 'pending', 'approved', 'edited', 'rejected'"),
    priority: Optional[str] = Query(default=None, description="Lọc theo do_uu_tien: 'high', 'medium', 'low'"),
):
    """
    Trả về danh sách câu tóm tắt/căn cứ bị NLI gắn cờ cần rà soát (UC-04).
    Được sắp xếp theo ưu tiên: contradiction (high) xếp trước, neutral (medium) xếp sau.
    """
    try:
        from backend.db.session import SessionLocal
        from backend.services.review import get_review_queue
        db = SessionLocal()
        result = get_review_queue(db, page=page, limit=limit, status_filter=status, priority_filter=priority)
        db.close()
        return result
    except Exception as e:
        logger.error(f"Lỗi lấy hàng đợi rà soát: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hàng đợi rà soát: {str(e)}",
        )


@app.post("/api/review/{item_id}/action", summary="Xử lý Hành động Rà soát (UC-04)")
def submit_review_action(item_id: int, req: ReviewActionRequest):
    """
    Thực hiện Duyệt / Sửa & Re-validate NLI / Loại bỏ một câu bị gắn cờ:
    - action = 'approve' | 'edit' | 'reject'
    - Nếu action = 'edit': Tự động chạy lại NLI check trên câu mới vừa sửa trước khi lưu.
    - Tự động nâng trạng thái văn bản sang PUBLISHED khi đã xử lý hết các câu bị cờ (Publish Gate).
    - Ghi log Audit Trail vào review_logs.
    """
    try:
        from backend.db.session import SessionLocal
        from backend.services.review import process_review_action
        db = SessionLocal()
        result = process_review_action(
            db=db,
            item_id=item_id,
            action=req.action,
            edited_sentence=req.edited_sentence,
            reviewer_id=req.reviewer_id,
        )
        db.close()
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Lỗi xử lý rà soát item {item_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xử lý rà soát: {str(e)}",
        )


@app.get("/api/review/audit-logs", summary="Nhật ký Duyệt Audit Trail (UC-04)")
def get_review_audit_logs(limit: int = Query(default=50, ge=1, le=200)):
    """Trả về danh sách nhật ký Audit Trail các thao tác rà soát của cán bộ."""
    try:
        from backend.db.session import SessionLocal
        from backend.services.review import get_audit_logs
        db = SessionLocal()
        logs = get_audit_logs(db, limit=limit)
        db.close()
        return {"total": len(logs), "logs": logs}
    except Exception as e:
        logger.error(f"Lỗi lấy audit log: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy audit log: {str(e)}",
        )


from fastapi import Response


@app.get("/api/report/suggest/{doc_id}", summary="Gợi ý Khung Báo Cáo (UC-05)")
def suggest_report_outline(doc_id: str):
    """
    Tự động gợi ý cấu trúc khung báo cáo theo loại văn bản và chủ đề (UC-05).
    - Căn cứ pháp lý: Tự động điền.
    - Số liệu & Kết luận: ĐỂ TRỐNG cho giảng viên tự nhập (Chống bịa số liệu).
    """
    try:
        from backend.db.session import SessionLocal
        from backend.services.report_suggestion import generate_report_outline
        db = SessionLocal()
        outline = generate_report_outline(db, doc_id)
        db.close()
        return outline
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.error(f"Lỗi gợi ý khung báo cáo {doc_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi gợi ý khung báo cáo: {str(e)}",
        )


@app.get("/api/report/export-docx/{doc_id}", summary="Xuất File Word .docx Khung Báo Cáo (UC-05)")
def export_report_docx(doc_id: str):
    """
    Xuất và tải trực tiếp file Microsoft Word (.docx) chuẩn định dạng cho giảng viên.
    """
    try:
        from backend.db.session import SessionLocal
        from backend.services.report_suggestion import build_report_docx_stream
        db = SessionLocal()
        docx_bytes = build_report_docx_stream(db, doc_id)
        db.close()

        filename = f"Khung_Bao_Cao_{doc_id}.docx"
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.error(f"Lỗi xuất file docx {doc_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xuất file Word: {str(e)}",
        )


@app.get("/api/health", summary="Health Check")

def health_check():
    """Kiểm tra sức khỏe hệ thống và trạng thái FAISS index."""
    docs = _load_jsonl(DOCS_PATH)
    chunks = _load_jsonl(CHUNKS_PATH)
    published_docs = sum(1 for d in docs if d.get("trang_thai_xuat_ban") == "PUBLISHED")
    published_chunks = sum(1 for c in chunks if c.get("trang_thai_xuat_ban") == "PUBLISHED")

    index_ready = INDEX_PATH.exists()

    return {
        "status": "healthy",
        "version": "1.0.0",
        "total_documents": len(docs),
        "published_documents": published_docs,
        "total_chunks": len(chunks),
        "published_chunks": published_chunks,
        "faiss_index_ready": index_ready,
    }


@app.post("/api/query", response_model=QueryResponse, summary="RAG Query với Citations")
def rag_query(req: QueryRequest):
    """
    Thực hiện RAG query (Tốc độ siêu nhanh <0.2s):
    1. Retrieve các chunk pháp quy PUBLISHED từ FAISS index.
    2. Tổng hợp câu trả lời theo trích dẫn (Extractive với Sentence Scoring).
    3. Kiểm tra NLI faithfulness trước khi trả về (nếu run_nli=True).
    """
    try:
        from services.retrieval.rag_chain import query_with_citation
        result = query_with_citation(
            question=req.question,
            index_path=str(INDEX_PATH),
            k=req.k,
            run_nli_check=req.run_nli,
            use_rule_based_nli=req.fast_nli,
        )
        return result
    except Exception as e:
        logger.error(f"Lỗi RAG Query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý câu hỏi: {str(e)}",
        )


@app.get("/api/documents", summary="Danh sách Văn bản Pháp quy")
def get_documents(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    q: Optional[str] = Query(default=None, description="Tìm kiếm theo từ khóa"),
    chu_de: Optional[str] = Query(default=None, description="Lọc theo chủ đề"),
    trang_thai: Optional[str] = Query(default=None, description="Lọc theo trang_thai_xuat_ban"),
    db: Session = Depends(get_db)
):
    """
    Trả về danh sách văn bản có hỗ trợ phân trang, tìm kiếm và bộ lọc.
    Ưu tiên đọc từ PostgreSQL Database, fallback sang JSONL nếu DB trống hoặc lỗi.
    """
    if db is not None:
        try:
            from backend.db.models import Document
            query = db.query(Document)
            if trang_thai:
                query = query.filter(Document.trang_thai_xuat_ban == trang_thai.lower())
            if chu_de:
                query = query.filter(Document.chu_de == chu_de)
            if q:
                q_like = f"%{q}%"
                query = query.filter(
                    (Document.ten_van_ban.ilike(q_like)) |
                    (Document.so_hieu.ilike(q_like))
                )
            total = query.count()
            items_db = query.offset((page - 1) * limit).limit(limit).all()
            items = []
            for d in items_db:
                items.append({
                    "doc_id": d.id,
                    "so_hieu": d.so_hieu or "",
                    "ten_van_ban": d.ten_van_ban,
                    "co_quan_ban_hanh": d.co_quan_ban_hanh or "",
                    "ngay_ban_hanh": str(d.ngay_ban_hanh) if d.ngay_ban_hanh else "",
                    "loai_van_ban": d.loai_van_ban or "",
                    "trich_yeu": d.ten_van_ban,
                    "chu_de": d.chu_de or "KHAC",
                    "muc_do_lien_quan_dau": d.pham_vi_ap_dung or "GENERAL",
                    "trang_thai_xuat_ban": (d.trang_thai_xuat_ban or "PUBLISHED").upper(),
                    "can_cu_dan_chieu": [],
                    "file_path": d.file_goc_url or ""
                })
            return {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": max(1, (total + limit - 1) // limit),
                "items": items,
            }
        except Exception as e:
            logger.warning(f"DB query documents failed: {e}. Fallback to JSONL.")

    docs = _load_jsonl(DOCS_PATH)

    # Filtering
    filtered = docs
    if trang_thai:
        filtered = [d for d in filtered if d.get("trang_thai_xuat_ban") == trang_thai]
    if chu_de:
        filtered = [d for d in filtered if d.get("chu_de") == chu_de]
    if q:
        q_lower = q.lower()
        filtered = [
            d for d in filtered
            if q_lower in d.get("ten_van_ban", "").lower()
            or q_lower in d.get("so_hieu", "").lower()
            or q_lower in d.get("trich_yeu", "").lower()
        ]

    # Pagination
    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": max(1, (total + limit - 1) // limit),
        "items": paginated,
    }


@app.get("/api/documents/{doc_id}", summary="Chi tiết Văn bản & Chunks")
def get_document_detail(doc_id: str, db: Session = Depends(get_db)):
    """Trả về chi tiết 1 văn bản và tất cả các chunks thuộc văn bản đó từ PostgreSQL DB (fallback JSONL)."""
    if db is not None:
        try:
            from backend.db.models import Document, DocumentChunk
            found_doc = db.query(Document).filter(Document.id == doc_id).first()
            if found_doc:
                chunks_db = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).all()
                formatted_chunks = [
                    {
                        "chunk_id": c.id,
                        "doc_id": c.document_id,
                        "dieu_so": c.chunk_index,
                        "title": c.dieu_khoan or f"Đoạn {c.chunk_index}",
                        "content": c.noi_dung,
                        "so_trang": c.so_trang
                    }
                    for c in chunks_db
                ]
                return {
                    "document": {
                        "doc_id": found_doc.id,
                        "so_hieu": found_doc.so_hieu or "",
                        "ten_van_ban": found_doc.ten_van_ban,
                        "co_quan_ban_hanh": found_doc.co_quan_ban_hanh or "",
                        "ngay_ban_hanh": str(found_doc.ngay_ban_hanh) if found_doc.ngay_ban_hanh else "",
                        "loai_van_ban": found_doc.loai_van_ban or "",
                        "trich_yeu": found_doc.ten_van_ban,
                        "chu_de": found_doc.chu_de or "KHAC",
                        "muc_do_lien_quan_dau": found_doc.pham_vi_ap_dung or "GENERAL",
                        "trang_thai_xuat_ban": (found_doc.trang_thai_xuat_ban or "PUBLISHED").upper(),
                        "can_cu_dan_chieu": [],
                        "file_path": found_doc.file_goc_url or ""
                    },
                    "total_chunks": len(formatted_chunks),
                    "chunks": formatted_chunks,
                }
        except Exception as e:
            logger.warning(f"DB query document detail failed: {e}. Fallback to JSONL.")

    docs = _load_jsonl(DOCS_PATH)
    found_doc = next((d for d in docs if d["doc_id"] == doc_id), None)
    if not found_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy văn bản với doc_id: {doc_id}",
        )

    chunks = _load_jsonl(CHUNKS_PATH)
    doc_chunks = [c for c in chunks if c.get("doc_id") == doc_id]

    return {
        "document": found_doc,
        "total_chunks": len(doc_chunks),
        "chunks": doc_chunks,
    }


@app.post("/api/documents/upload", summary="Nạp Văn Bản Mới (UC-01 & UC-02)")
def upload_document(
    file: UploadFile = File(...),
    chu_de: str = Form("KHAC"),
    db: Session = Depends(get_db)
):
    """
    Nạp file PDF vào hệ thống.
    Thực hiện trích xuất text, chia đoạn, sinh tóm tắt, kiểm tra NLI,
    và lưu vào PostgreSQL. Trả về kết quả pipeline.
    """
    try:
        import shutil
        from backend.services.ingestion.ingest_service import run_ingestion_pipeline
        
        # Tạo thư mục upload tạm
        upload_dir = ROOT_DIR / "data" / "raw" / chu_de
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = run_ingestion_pipeline(db, file_path, chu_de_thu_muc=chu_de)
        
        # Cập nhật lại các file JSON tĩnh nếu cần, để đồng bộ với UI (UI có thể đang load từ JSONL)
        # Tạm thời ta chỉ ghi đè JSONL khi publish_documents.py chạy,
        # nhưng tốt nhất là cập nhật JSONL ngay ở đây để API GET /api/documents đọc được nếu nó đọc từ file.
        
        return result
        
    except Exception as e:
        logger.error(f"Lỗi upload file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý file upload: {str(e)}"
        )


@app.post("/api/publish/{doc_id}", summary="Phê duyệt / Đổi trạng thái Văn bản")
def publish_document(doc_id: str, req: PublishRequest):
    """Duyệt hoặc chuyển trạng thái văn bản giữa PUBLISHED và PENDING_REVIEW."""
    try:
        from scripts.publish_documents import _update_status
        d_updated, c_updated = _update_status({doc_id}, req.new_status)
        return {
            "message": f"Đã cập nhật văn bản [{doc_id}] sang {req.new_status}",
            "doc_id": doc_id,
            "new_status": req.new_status,
            "docs_updated": d_updated,
            "chunks_updated": c_updated,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật trạng thái: {str(e)}",
        )


@app.get("/api/stats", summary="Thống kê Tổng quan")
def get_stats():
    """Trả về số liệu thống kê văn bản, chunks, quan hệ từ PostgreSQL DB."""
    try:
        from backend.db.session import SessionLocal
        from backend.db.models import Document, DocumentChunk
        db = SessionLocal()
        total_docs = db.query(Document).count()
        pub_docs = db.query(Document).filter(Document.trang_thai_xuat_ban == "published").count()
        total_chunks = db.query(DocumentChunk).count()
        
        # Topic counts
        docs = db.query(Document).all()
        topics_count: Dict[str, int] = {}
        for d in docs:
            topic = d.chu_de or "KHAC"
            topics_count[topic] = topics_count.get(topic, 0) + 1
        db.close()
        return {
            "total_documents": total_docs,
            "published_documents": pub_docs,
            "pending_documents": total_docs - pub_docs,
            "total_chunks": total_chunks,
            "published_chunks": total_chunks,
            "topics": topics_count,
            "faiss_index_exists": INDEX_PATH.exists(),
            "database_source": "PostgreSQL"
        }
    except Exception as e:
        logger.warning(f"PostgreSQL stats failed: {e}. Falling back to JSONL.")
        docs = _load_jsonl(DOCS_PATH)
        chunks = _load_jsonl(CHUNKS_PATH)

        pub_docs = sum(1 for d in docs if d.get("trang_thai_xuat_ban") == "PUBLISHED")
        pub_chunks = sum(1 for c in chunks if c.get("trang_thai_xuat_ban") == "PUBLISHED")

        topics_count: Dict[str, int] = {}
        for d in docs:
            topic = d.get("chu_de", "KHAC")
            topics_count[topic] = topics_count.get(topic, 0) + 1

        return {
            "total_documents": len(docs),
            "published_documents": pub_docs,
            "pending_documents": len(docs) - pub_docs,
            "total_chunks": len(chunks),
            "published_chunks": pub_chunks,
            "topics": topics_count,
            "faiss_index_exists": INDEX_PATH.exists(),
            "database_source": "JSONL_Fallback"
        }



# --- UC-06: CÂY VĂN BẢN & MỨC ĐỘ ÁP DỤNG CHO DAU ---

class UpdateScopeRequest(BaseModel):
    pham_vi_ap_dung: str = Field(..., description="DIRECT_DAU | GENERAL | REFERENCE")


@app.get("/api/documents/{doc_id}/tree", summary="Lấy Cây văn bản & mối quan hệ pháp lý / tương đồng (UC-06)")
def get_document_tree(doc_id: str, db: Session = Depends(get_db)):
    """Trả về quan hệ Căn cứ, Thay thế, Sửa đổi, Bãi bỏ & Tương đồng ngữ nghĩa của văn bản."""
    try:
        from backend.services.document_tree.tree_service import build_document_tree
        return build_document_tree(db, doc_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn Cây văn bản: {str(e)}")


@app.put("/api/documents/{doc_id}/scope", summary="Cập nhật Phạm vi Áp dụng cho Trường ĐH Kiến trúc Đà Nẵng (UC-06)")
def update_scope(doc_id: str, req: UpdateScopeRequest, db: Session = Depends(get_db)):
    """Cập nhật nhãn pham_vi_ap_dung (DIRECT_DAU, GENERAL, REFERENCE) cho văn bản."""
    try:
        from backend.services.document_tree.tree_service import update_document_scope
        return update_document_scope(db, doc_id, req.pham_vi_ap_dung)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật phạm vi áp dụng: {str(e)}")


# --- UC-08: DASHBOARD DUYỆT & QUẢN LÝ THEO CHỦ ĐỀ ---

TOPIC_METADATA = {
    "DAO_TAO": {"name": "Đào Tạo & Học Vụ", "icon": "🎓"},
    "TUYEN_SINH": {"name": "Tuyển Sinh & Nhập Học", "icon": "🎯"},
    "TAI_CHINH": {"name": "Tài Chính & Học Phí", "icon": "💰"},
    "NHAN_SU": {"name": "Nhân Sự & Giảng Viên", "icon": "👔"},
    "CO_SO_VAT_CHAT": {"name": "Cơ Sở Vật Chất", "icon": "🏢"},
    "KHAC": {"name": "Văn Bản Hành Chính Khác", "icon": "📂"}
}


@app.get("/api/topics/summary", summary="Thống kê danh mục văn bản theo Chủ đề (UC-08)")
def get_topics_summary(db: Session = Depends(get_db)):
    """Trả về danh sách thẻ chủ đề kèm số lượng tổng, đã duyệt, cần rà soát & tỷ lệ % xuất bản."""
    try:
        from backend.db.models import Document, DocumentChunk
        docs = db.query(Document).all()
        chunks = db.query(DocumentChunk).all()

        topic_stats = {code: {"total": 0, "published": 0, "pending": 0, "chunks": 0} for code in TOPIC_METADATA}

        for d in docs:
            t_code = d.chu_de if d.chu_de in TOPIC_METADATA else "KHAC"
            topic_stats[t_code]["total"] += 1
            if d.trang_thai_xuat_ban == "published":
                topic_stats[t_code]["published"] += 1
            else:
                topic_stats[t_code]["pending"] += 1

        for c in chunks:
            parent = next((d for d in docs if d.id == c.document_id), None)
            t_code = parent.chu_de if parent and parent.chu_de in TOPIC_METADATA else "KHAC"
            topic_stats[t_code]["chunks"] += 1

        result = []
        for code, meta in TOPIC_METADATA.items():
            st = topic_stats[code]
            total = st["total"]
            comp_rate = round((st["published"] / total * 100), 1) if total > 0 else 0.0
            result.append({
                "code": code,
                "name": meta["name"],
                "icon": meta["icon"],
                "total_documents": total,
                "published_documents": st["published"],
                "pending_documents": st["pending"],
                "total_chunks": st["chunks"],
                "completion_rate": comp_rate
            })

        return {"topics": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tổng hợp chủ đề: {str(e)}")


@app.post("/api/summarize/{doc_id}", response_model=SummarizeResponse, summary="Tóm tắt văn bản (UC-03, WF-03)")
def summarize_document_endpoint(
    doc_id: str,
    request: SummarizeRequest,
    db: Session = Depends(get_db)
):
    """
    Tóm tắt văn bản theo WF-03:
      - strategy='extractive': TextRank — chọn câu gốc, không hallucinate
      - strategy='abstractive': BARTpho/ViT5 + NLI check từng câu
      - strategy='hybrid': Thử BARTpho trước, tự fallback TextRank nếu model không tải được

    Kết quả bao gồm:
      - Từng câu tóm tắt kèm nhãn NLI (entailment/contradiction/neutral)
      - Điểm faithfulness
      - overall_action: AUTO_PUBLISH / WARN_PENDING_REVIEW / BLOCK_PENDING_REVIEW
      - trang_thai_xuat_ban theo WF-03 (không auto-publish nếu có contradiction)
    """
    doc_meta = None
    doc_chunks = []

    if db is not None:
        try:
            from backend.db.models import Document, DocumentChunk
            doc_obj = db.query(Document).filter(Document.id == doc_id).first()
            if doc_obj:
                doc_meta = {
                    "doc_id": doc_obj.id,
                    "ten_van_ban": doc_obj.ten_van_ban,
                    "so_hieu": doc_obj.so_hieu or doc_obj.id
                }
                chunks_obj = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).all()
                doc_chunks = [
                    {
                        "chunk_id": c.id,
                        "doc_id": c.document_id,
                        "content": c.noi_dung,
                        "title": c.dieu_khoan or "",
                        "so_trang": c.so_trang
                    }
                    for c in chunks_obj
                ]
        except Exception as e:
            logger.warning(f"DB load for summarize failed: {e}. Fallback to JSONL.")

    if not doc_meta:
        all_docs = _load_jsonl(DOCS_PATH)
        doc_meta = next((d for d in all_docs if d.get("doc_id") == doc_id), None)

    if not doc_meta:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy văn bản: {doc_id}")

    if not doc_chunks:
        all_chunks = _load_jsonl(CHUNKS_PATH)
        doc_chunks = [c for c in all_chunks if c.get("doc_id") == doc_id]

    if not doc_chunks:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy chunks cho văn bản {doc_id}. Kiểm tra pipeline.",
        )

    if request.max_chunks:
        doc_chunks = doc_chunks[:request.max_chunks]

    # ── 3. Chạy summarization ──────────────────────────────────────────────
    try:
        from backend.services.summarization.summarizer import DocumentSummarizer

        summarizer = DocumentSummarizer(
            strategy=request.strategy,
            run_nli_check=request.run_nli,
        )
        result = summarizer.summarize_document(doc_id=doc_id, chunks=doc_chunks)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Lỗi summarization cho {doc_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi tóm tắt văn bản: {str(e)}",
        )

    # ── 4. Định dạng response ──────────────────────────────────────────────
    formatted_chunks = []
    for cr in result.get("chunk_results", []):
        sentences_formatted = [
            SentenceResult(
                sentence=s.get("sentence", ""),
                chunk_id=s.get("chunk_id", ""),
                method=s.get("method", "unknown"),
                nhan_nli=s.get("nhan_nli", "PENDING"),
                diem_faithfulness=s.get("diem_faithfulness"),
                publish_action=s.get("publish_action", "PENDING_NLI_CHECK"),
            )
            for s in cr.get("sentences", [])
        ]
        formatted_chunks.append(
            ChunkSummaryResult(
                chunk_id=cr.get("chunk_id", ""),
                doc_id=cr.get("doc_id", doc_id),
                sentences=sentences_formatted,
                overall_action=cr.get("overall_action", "SKIP_EMPTY"),
                trang_thai_xuat_ban=cr.get("trang_thai_xuat_ban", "PENDING_REVIEW"),
                has_contradiction=cr.get("has_contradiction", False),
                has_neutral=cr.get("has_neutral", False),
                strategy_used=cr.get("strategy_used", request.strategy),
                nli_stats=cr.get("nli_stats", {}),
            )
        )

    return SummarizeResponse(
        doc_id=doc_id,
        ten_van_ban=doc_meta.get("ten_van_ban", ""),
        so_hieu=doc_meta.get("so_hieu", ""),
        strategy=request.strategy,
        overall_action=result.get("overall_action", "SKIP_EMPTY"),
        trang_thai_xuat_ban=result.get("trang_thai_xuat_ban", "PENDING_REVIEW"),
        total_chunks=result.get("total_chunks", 0),
        total_sentences=result.get("total_sentences", 0),
        strategies_used=result.get("strategies_used", []),
        avg_faithfulness=result.get("avg_faithfulness"),
        nli_stats=result.get("nli_stats", {}),
        chunk_results=formatted_chunks,
    )


@app.post("/api/admin/reset-nli", summary="Reset NLI Checker Singleton")
def reset_nli():
    """Reset NLI Checker model singleton (cho phép đổi model hoặc làm sạch bộ nhớ)."""
    try:
        from services.nli.nli_checker import reset_nli_checker
        reset_nli_checker()
        return {"message": "NLI Checker singleton đã được reset thành công."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi reset NLI: {str(e)}",
        )


@app.post("/api/admin/reset-summarizer", summary="Reset Abstractive Summarizer Singleton")
def reset_summarizer():
    """Reset Abstractive Summarizer singleton (cho phép đổi model hoặc giải phóng bộ nhớ)."""
    try:
        from services.summarization.summarizer import _abstractive_lock
        import services.summarization.summarizer as _sum_module
        with _abstractive_lock:
            _sum_module._abstractive_singleton = None
        return {"message": "Abstractive Summarizer singleton đã được reset thành công."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi reset summarizer: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
