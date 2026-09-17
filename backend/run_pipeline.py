"""Pipeline End-to-End — DAU Second Brain.

Script chạy toàn bộ pipeline LangChain theo thứ tự:
  Step 1: Build FAISS Index (từ chunks.jsonl đã có)
  Step 2: Summarization Hybrid (BARTpho + NLI check, tự fallback extractive)
  Step 3: Test RAG Query (tra cứu ngữ nghĩa)
  Step 4: Test Report Suggestion
  Step 5: Test Document Tree (Cây Văn Bản)

Cách dùng:
  # Chạy toàn bộ pipeline
  python run_pipeline.py

  # Chỉ build index
  python run_pipeline.py --step index

  # Chỉ test RAG
  python run_pipeline.py --step rag

  # Test với PENDING_REVIEW (khi chưa có PUBLISHED data)
  python run_pipeline.py --include_pending

Ghi chú:
  - Lần đầu chạy, embedding model sẽ tự động tải về (~280MB cho vietnamese-bi-encoder)
  - Sau khi build index lần đầu, các lần sau sẽ nhanh hơn (load từ cache)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
CHUNKS_PATH = ROOT / "data" / "processed" / "chunks.jsonl"
DOCS_PATH = ROOT / "data" / "processed" / "documents.jsonl"
RELATIONS_PATH = ROOT / "data" / "processed" / "document_relations.jsonl"
INDEX_PATH = ROOT / "data" / "vector_db" / "faiss_index"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def load_first_doc_with_chunks() -> tuple[dict, list[dict]]:
    """Load văn bản đầu tiên cùng tất cả chunk của nó."""
    with open(DOCS_PATH, "r", encoding="utf-8") as f:
        first_doc = json.loads(f.readline().strip())

    doc_id = first_doc["doc_id"]
    chunks = []

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            chunk = json.loads(line.strip())
            if chunk.get("doc_id") == doc_id:
                chunks.append(chunk)

    return first_doc, chunks


# ─── Step 1: Build FAISS Index ────────────────────────────────────────────────

def step_build_index(include_pending: bool = False):
    print_section("STEP 1: Build FAISS Index")

    if not CHUNKS_PATH.exists():
        logger.error(f"❌ Không tìm thấy {CHUNKS_PATH}")
        logger.error("   Hãy chạy trước: python -m services.ingestion.preprocess")
        return False

    try:
        from services.retrieval.build_index import build_faiss_index

        logger.info(f"📂 Chunks path: {CHUNKS_PATH}")
        logger.info(f"💾 Index path:  {INDEX_PATH}")

        start = time.time()
        build_faiss_index(
            chunks_path=str(CHUNKS_PATH),
            index_path=str(INDEX_PATH),
            include_pending=include_pending,
        )
        elapsed = time.time() - start
        logger.info(f"⏱️  Build hoàn thành trong {elapsed:.1f}s")
        return True

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("   Chạy: pip install -r requirements_langchain.txt")
        return False
    except Exception as e:
        logger.error(f"❌ Lỗi build index: {e}")
        return False


# ─── Step 2: Summarization (Hybrid BARTpho/ViT5 + Extractive Fallback) ─────────────────────

def step_summarization(strategy: str = "extractive", run_nli: bool = False):
    print_section(f"STEP 2: Summarization (strategy={strategy}, nli={run_nli})")

    try:
        from services.summarization.summarizer import DocumentSummarizer

        first_doc, chunks = load_first_doc_with_chunks()

        logger.info(f"📄 Văn bản: {first_doc.get('ten_van_ban', first_doc['doc_id'])}")
        logger.info(f"   Số chunks: {len(chunks)}")

        summarizer = DocumentSummarizer(
            strategy=strategy,
            run_nli_check=run_nli,
        )

        # Test 3 chunks đầu
        test_chunks = chunks[:3]

        import time
        t0 = time.time()
        result = summarizer.summarize_document(
            doc_id=first_doc["doc_id"],
            chunks=test_chunks,
        )
        elapsed = time.time() - t0

        logger.info(f"✅ Kết quả tóm tắt:")
        logger.info(f"   Status        : {result['trang_thai_xuat_ban']}")
        logger.info(f"   Action        : {result['overall_action']}")
        logger.info(f"   Total sentences: {result['total_sentences']}")
        logger.info(f"   Strategy used : {result.get('strategies_used', [strategy])}")
        if result.get('avg_faithfulness') is not None:
            logger.info(f"   Avg Faithfulness: {result['avg_faithfulness']:.4f}")

        nli_stats = result.get('nli_stats', {})
        if nli_stats.get('total', 0) > 0:
            logger.info(
                f"   NLI Stats : ✅ entailment={nli_stats['entailment']} "
                f"🟡 neutral={nli_stats['neutral']} "
                f"🔴 contradiction={nli_stats['contradiction']}"
            )

        # Hiển thị vài câu mẫu
        for cr in result["chunk_results"][:2]:
            for sent in cr["sentences"][:1]:
                nli = sent.get('nhan_nli', 'N/A')
                score = sent.get('diem_faithfulness')
                method = sent.get('method', 'N/A')
                score_str = f"{score:.3f}" if score is not None else 'N/A'
                logger.info(f"   [{nli}|{score_str}|{method}] {sent['sentence'][:120]}")

        logger.info(f"   ⏱️  Thời gian: {elapsed:.2f}s")
        return True

    except Exception as e:
        logger.error(f"❌ Lỗi summarization: {e}")
        import traceback
        traceback.print_exc()
        return False


# ─── Step 3: Test RAG Query ───────────────────────────────────────────────────

def step_rag_query():
    print_section("STEP 3: RAG Query (Semantic Search + Citation)")

    if not INDEX_PATH.exists():
        logger.warning("⚠️  FAISS index chưa có. Bỏ qua step RAG.")
        logger.warning("   Chạy step 1 trước: python run_pipeline.py --step index")
        return False

    try:
        from services.retrieval.rag_chain import query_with_citation

        test_questions = [
            "Quy định về báo cáo định kỳ cho Bộ Giáo dục như thế nào?",
            "Điều kiện tuyển sinh đại học là gì?",
            "Thông tư nào quy định về kiểm định chất lượng?",
        ]

        for q in test_questions:
            logger.info(f"\n❓ Câu hỏi: {q}")
            result = query_with_citation(
                question=q,
                index_path=str(INDEX_PATH),
                run_nli_check=False,
            )

            if result.get("answer"):
                logger.info(f"✅ Trả lời: {result['answer'][:200]}...")
                logger.info(f"   📎 Citations: {len(result['citations'])} nguồn")
                for cit in result["citations"][:2]:
                    logger.info(
                        f"      [{cit['index']}] {cit['ten_van_ban']} — {cit['dieu_khoan']}"
                    )
            else:
                logger.warning(f"⚠️  {result.get('message', 'Không có kết quả')}")

        return True

    except Exception as e:
        logger.error(f"❌ Lỗi RAG query: {e}")
        import traceback
        traceback.print_exc()
        return False


# ─── Step 4: Test Report Suggestion ──────────────────────────────────────────

def step_report_suggestion():
    print_section("STEP 4: Report Suggestion")

    try:
        from services.report_suggestion.report_chain import suggest_report

        first_doc, chunks = load_first_doc_with_chunks()

        logger.info(f"📄 Văn bản: {first_doc.get('ten_van_ban', first_doc['doc_id'])}")

        result = suggest_report(
            doc_metadata=first_doc,
            chunks=chunks[:5],
        )

        logger.info(f"✅ Loại báo cáo: {result['loai_bao_cao']}")
        logger.info(f"   Template: {result.get('template_id', 'Tự dựng từ văn bản')}")
        logger.info(f"   Source: {result['source']}")
        logger.info("   Đề mục:")
        for dm in result["de_muc"][:6]:
            logger.info(f"     {dm}")
        logger.info(f"   Căn cứ pháp lý:")
        for cc in result["can_cu_phap_ly"][:2]:
            logger.info(f"     - {cc}")

        return True

    except Exception as e:
        logger.error(f"❌ Lỗi report suggestion: {e}")
        return False


# ─── Step 5: Test Document Tree ──────────────────────────────────────────────

def step_document_tree():
    print_section("STEP 5: Document Tree / Cây Văn Bản")

    try:
        from services.document_tree.related_docs import DocumentTree

        first_doc, chunks = load_first_doc_with_chunks()
        doc_id = first_doc["doc_id"]
        doc_content = chunks[0]["content"] if chunks else ""

        logger.info(f"📄 Văn bản: {first_doc.get('ten_van_ban', doc_id)}")

        tree = DocumentTree(
            index_path=str(INDEX_PATH),
            relations_path=str(RELATIONS_PATH),
        )

        result = tree.find_related(
            doc_id=doc_id,
            doc_content=doc_content[:512],
            include_semantic=INDEX_PATH.exists(),
        )

        logger.info(f"✅ Quan hệ tường minh: {len(result['explicit_relations'])} kết quả")
        for rel in result["explicit_relations"][:5]:
            logger.info(
                f"   [{rel['loai_quan_he']}] → {rel['doc_id_related']}: "
                f"{rel['mo_ta'][:60]}"
            )

        logger.info(f"✅ Quan hệ ngữ nghĩa: {len(result['semantic_relations'])} kết quả")
        for rel in result["semantic_relations"][:3]:
            logger.info(
                f"   [LIEN_QUAN] → {rel['doc_id_related']} "
                f"(score={rel['diem_tuong_dong']:.3f})"
            )

        if not result["semantic_relations"] and not INDEX_PATH.exists():
            logger.warning(
                "   (Quan hệ ngữ nghĩa chưa có — cần build FAISS index trước)"
            )

        return True

    except Exception as e:
        logger.error(f"❌ Lỗi document tree: {e}")
        return False


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="DAU Second Brain — LangChain Pipeline Runner"
    )
    parser.add_argument(
        "--step",
        choices=["all", "index", "summarize", "summarize-hybrid", "rag", "report", "tree"],
        default="all",
        help="Bước cần chạy (default: all — chạy toàn bộ)",
    )
    parser.add_argument(
        "--include_pending",
        action="store_true",
        help=(
            "Index cả PENDING_REVIEW (dùng khi chưa có PUBLISHED data). "
            "Chú ý: vi phạm ràng buộc WF-05, chỉ dùng khi test!"
        ),
    )
    args = parser.parse_args()

    print("\n" + "🧠 " * 20)
    print("   DAU SECOND BRAIN — LangChain Integration Pipeline")
    print("🧠 " * 20)

    # Kiểm tra dữ liệu đầu vào
    if not DOCS_PATH.exists() or not CHUNKS_PATH.exists():
        logger.error("❌ Thiếu dữ liệu processed. Chạy trước:")
        logger.error("   python -m services.ingestion.preprocess")
        sys.exit(1)

    with open(DOCS_PATH, "r", encoding="utf-8") as f:
        n_docs = sum(1 for _ in f)
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        n_chunks = sum(1 for _ in f)

    logger.info(f"📊 Dữ liệu: {n_docs} văn bản | {n_chunks} chunks")
    if args.include_pending:
        logger.warning(
            "⚠️  --include_pending: Sẽ index cả PENDING_REVIEW. "
            "Chỉ dùng để test!"
        )

    results = {}
    step = args.step

    if step in ("all", "index"):
        results["index"] = step_build_index(include_pending=args.include_pending)

    if step in ("all", "summarize"):
        results["summarize"] = step_summarization(strategy="extractive", run_nli=False)

    if step == "summarize-hybrid":
        results["summarize-hybrid"] = step_summarization(strategy="hybrid", run_nli=True)

    if step in ("all", "rag"):
        results["rag"] = step_rag_query()

    if step in ("all", "report"):
        results["report"] = step_report_suggestion()

    if step in ("all", "tree"):
        results["tree"] = step_document_tree()

    # Summary
    print_section("KẾT QUẢ PIPELINE")
    all_ok = True
    for name, ok in results.items():
        status = "✅ OK" if ok else "❌ FAIL"
        logger.info(f"  {status} — {name}")
        if not ok:
            all_ok = False

    if all_ok:
        logger.info("\n🎉 Toàn bộ pipeline chạy thành công!")
        logger.info("   Log đã lưu tại: pipeline.log")
    else:
        logger.warning("\n⚠️  Một số bước gặp lỗi. Xem log bên trên để biết chi tiết.")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
