"""Build FAISS Index — DAU Second Brain (EPIC-5).

Script xây dựng FAISS vector index từ data/processed/chunks.jsonl.
Chỉ index các chunk thuộc văn bản PUBLISHED (ràng buộc WF-05).

Cách dùng:
  python -m services.retrieval.build_index
  python -m services.retrieval.build_index --chunks_path data/processed/chunks.jsonl
  python -m services.retrieval.build_index --include_pending  # Index cả PENDING_REVIEW (chỉ dùng để test)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ─── Hằng số ─────────────────────────────────────────────────────────────────

# Embedding model tốt nhất cho tiếng Việt (local, không cần API)
EMBEDDING_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"

# Fallback nếu RAM/disk hạn chế
EMBEDDING_MODEL_FALLBACK = "intfloat/multilingual-e5-small"

DEFAULT_INDEX_PATH = "data/vector_db/faiss_index"
DEFAULT_CHUNKS_PATH = "data/processed/chunks.jsonl"


# ─── Load Chunks ──────────────────────────────────────────────────────────────

def load_doc_lookup(docs_path: str = "data/processed/documents.jsonl") -> dict[str, str]:
    """Load documents.jsonl để tạo doc_id -> ten_van_ban lookup table."""
    lookup = {}
    p = Path(docs_path)
    if not p.exists():
        return lookup
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    d = json.loads(line)
                    if "doc_id" in d:
                        lookup[d["doc_id"]] = d.get("ten_van_ban") or d.get("so_hieu", "")
                except (json.JSONDecodeError, KeyError):
                    continue
    return lookup


def load_chunks_as_documents(
    chunks_path: str,
    include_pending: bool = False,
) -> list:
    """
    Load chunks từ JSONL, tạo LangChain Document objects.
    Mỗi Document giữ nguyên toàn bộ metadata để phục vụ citation (WF-05).

    Args:
        chunks_path: Đường dẫn tới chunks.jsonl
        include_pending: Nếu True, cũng index cả PENDING_REVIEW (chỉ test)

    Returns:
        list[Document]: Danh sách Document sẵn sàng đưa vào FAISS
    """
    from langchain_core.documents import Document

    doc_lookup = load_doc_lookup()
    documents = []
    skipped = 0
    total = 0

    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            chunk = json.loads(line)

            # ── Ràng buộc WF-05: chỉ index văn bản PUBLISHED ──────────────
            publish_status = chunk.get("trang_thai_xuat_ban", "PENDING_REVIEW")
            if not include_pending and publish_status != "PUBLISHED":
                skipped += 1
                continue

            # Nội dung chính để embed
            content = chunk.get("content", "").strip()
            if len(content) < 30:  # Bỏ qua chunk quá ngắn
                skipped += 1
                continue

            doc_id = chunk.get("doc_id", "")
            ten_van_ban = chunk.get("ten_van_ban") or doc_lookup.get(doc_id, "")

            # Metadata đầy đủ cho citation
            doc = Document(
                page_content=content,
                metadata={
                    "chunk_id": chunk.get("chunk_id", ""),
                    "doc_id": doc_id,
                    "so_hieu": chunk.get("so_hieu", ""),
                    "ten_van_ban": ten_van_ban,
                    "dieu_so": chunk.get("dieu_so"),
                    "khoan_so": chunk.get("khoan_so"),
                    "title": chunk.get("title", ""),
                    "so_trang": chunk.get("so_trang", 1),
                    "chu_de": chunk.get("chu_de", "KHAC"),
                    "muc_do_lien_quan_dau": chunk.get("muc_do_lien_quan_dau", "GENERAL"),
                    "trang_thai_xuat_ban": publish_status,
                },
            )
            documents.append(doc)

    logger.info(
        f"📊 Đã load {len(documents)}/{total} chunks "
        f"(bỏ qua {skipped} chunk PENDING_REVIEW/ngắn)."
    )
    return documents


# ─── Build & Save Index ───────────────────────────────────────────────────────

def build_faiss_index(
    chunks_path: str = DEFAULT_CHUNKS_PATH,
    index_path: str = DEFAULT_INDEX_PATH,
    model_name: str = EMBEDDING_MODEL_NAME,
    device: str = "cpu",
    include_pending: bool = False,
    batch_size: int = 64,
) -> None:
    """
    Xây dựng và lưu FAISS index.

    Args:
        chunks_path: Đường dẫn chunks.jsonl
        index_path: Thư mục lưu FAISS index
        model_name: Tên embedding model HuggingFace
        device: "cpu" hoặc "cuda"
        include_pending: Index cả PENDING_REVIEW hay không
        batch_size: Batch size khi encode (giảm nếu ít RAM)
    """
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
    except ImportError as e:
        logger.error(f"Thiếu dependency: {e}")
        logger.error("Chạy: pip install langchain-huggingface langchain-community faiss-cpu")
        sys.exit(1)

    # ── 1. Load documents ──────────────────────────────────────────────────
    logger.info(f"📂 Đang load chunks từ: {chunks_path}")
    documents = load_chunks_as_documents(chunks_path, include_pending=include_pending)

    if not documents:
        logger.warning(
            "⚠️ Không có document nào để index. "
            "Kiểm tra trang_thai_xuat_ban trong chunks.jsonl — "
            "hiện tại tất cả đang PENDING_REVIEW. "
            "Dùng --include_pending để index tạm thời khi test."
        )
        return

    # ── 2. Load embedding model ────────────────────────────────────────────
    logger.info(f"🤖 Đang tải embedding model: {model_name} (device={device})...")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": device},
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": batch_size,
            },
        )
    except Exception as e:
        logger.warning(f"⚠️ Không tải được {model_name}: {e}")
        logger.info(f"🔄 Thử fallback model: {EMBEDDING_MODEL_FALLBACK}")
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_FALLBACK,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True},
        )

    # ── 3. Build FAISS index ───────────────────────────────────────────────
    logger.info(f"⚙️ Đang build FAISS index từ {len(documents)} documents...")
    vector_store = FAISS.from_documents(documents, embeddings)

    # ── 4. Save index ──────────────────────────────────────────────────────
    Path(index_path).mkdir(parents=True, exist_ok=True)
    vector_store.save_local(index_path)
    logger.info(f"✅ FAISS index đã lưu tại: {index_path}")
    logger.info(f"   Tổng số vectors: {vector_store.index.ntotal}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build FAISS index cho DAU Second Brain")
    parser.add_argument(
        "--chunks_path",
        default=DEFAULT_CHUNKS_PATH,
        help=f"Đường dẫn chunks.jsonl (default: {DEFAULT_CHUNKS_PATH})",
    )
    parser.add_argument(
        "--index_path",
        default=DEFAULT_INDEX_PATH,
        help=f"Thư mục lưu FAISS index (default: {DEFAULT_INDEX_PATH})",
    )
    parser.add_argument(
        "--model",
        default=EMBEDDING_MODEL_NAME,
        help="Tên HuggingFace embedding model",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device để chạy embedding model",
    )
    parser.add_argument(
        "--include_pending",
        action="store_true",
        help="Bao gồm cả chunk PENDING_REVIEW (chỉ dùng để test)",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=64,
        help="Batch size khi encode embeddings",
    )
    args = parser.parse_args()

    build_faiss_index(
        chunks_path=args.chunks_path,
        index_path=args.index_path,
        model_name=args.model,
        device=args.device,
        include_pending=args.include_pending,
        batch_size=args.batch_size,
    )
