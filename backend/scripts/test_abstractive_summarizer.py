"""Test script cho AbstractiveSummarizer (BARTpho + NLI check).

Cách dùng:
  # Test nhanh extractive (không cần model):
  python scripts/test_abstractive_summarizer.py --strategy extractive

  # Test hybrid (BARTpho với fallback):
  python scripts/test_abstractive_summarizer.py --strategy hybrid

  # Test hybrid + NLI check:
  python scripts/test_abstractive_summarizer.py --strategy hybrid --nli

  # Test abstractive thuần (cần kết nối internet để tải BARTpho ~1.2GB):
  python scripts/test_abstractive_summarizer.py --strategy abstractive --nli
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Setup path
BACKEND_DIR = Path(__file__).parent.parent
ROOT_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


CHUNKS_PATH = ROOT_DIR / "data" / "processed" / "chunks.jsonl"
DOCS_PATH = ROOT_DIR / "data" / "processed" / "documents.jsonl"


def load_test_data(n_chunks: int = 3) -> tuple[dict, list[dict]]:
    """Load văn bản đầu tiên cùng N chunk đầu tiên."""
    with open(DOCS_PATH, "r", encoding="utf-8") as f:
        first_doc = json.loads(f.readline().strip())

    doc_id = first_doc["doc_id"]
    chunks = []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            chunk = json.loads(line.strip())
            if chunk.get("doc_id") == doc_id:
                chunks.append(chunk)
                if len(chunks) >= n_chunks:
                    break

    return first_doc, chunks


def print_section(title: str):
    print(f"\n{'=' * 65}")
    print(f"  {title}")
    print("=" * 65)


def print_chunk_result(result: dict, verbose: bool = False):
    """In kết quả summarization của 1 chunk."""
    print(f"\n  📄 Chunk: {result['chunk_id']}")
    print(f"     Strategy: {result['strategy_used']}")
    print(f"     Status  : {result['trang_thai_xuat_ban']} | Action: {result['overall_action']}")

    stats = result.get("nli_stats", {})
    if stats.get("total", 0) > 0:
        print(
            f"     NLI     : ✅ entailment={stats['entailment']}  "
            f"🟡 neutral={stats['neutral']}  "
            f"🔴 contradiction={stats['contradiction']}"
        )

    for i, sent in enumerate(result["sentences"][:3]):
        nli = sent.get("nhan_nli", "N/A")
        score = sent.get("diem_faithfulness")
        method = sent.get("method", "N/A")
        score_str = f"{score:.3f}" if score is not None else "N/A"
        label_icon = {
            "entailment": "✅",
            "contradiction": "🔴",
            "neutral": "🟡",
            "PENDING": "⏳",
        }.get(nli, "❓")
        print(f"     [{i+1}] {label_icon} [{nli}|{score_str}|{method}]")
        if verbose:
            print(f"         {sent['sentence'][:150]}")
        else:
            print(f"         {sent['sentence'][:100]}{'...' if len(sent['sentence']) > 100 else ''}")


def main():
    parser = argparse.ArgumentParser(description="Test AbstractiveSummarizer (BARTpho + NLI)")
    parser.add_argument(
        "--strategy",
        choices=["extractive", "abstractive", "hybrid"],
        default="extractive",
        help="Chiến lược tóm tắt (default: extractive để test nhanh, không cần model)",
    )
    parser.add_argument(
        "--nli", action="store_true",
        help="Chạy NLI check sau khi tóm tắt (cần torch + transformers)",
    )
    parser.add_argument(
        "--chunks", type=int, default=3,
        help="Số chunk để test (default: 3)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Hiện đầy đủ câu tóm tắt (không cắt ngắn)",
    )
    args = parser.parse_args()

    print_section(f"TEST ABSTRACTIVE SUMMARIZER — strategy={args.strategy}")
    print(f"  📋 Config: nli={args.nli}, chunks={args.chunks}, verbose={args.verbose}")

    # ── Kiểm tra dữ liệu ────────────────────────────────────────────────
    if not CHUNKS_PATH.exists():
        print(f"❌ Không tìm thấy {CHUNKS_PATH}")
        sys.exit(1)

    first_doc, test_chunks = load_test_data(n_chunks=args.chunks)
    print(f"\n  📂 Văn bản: {first_doc.get('ten_van_ban', first_doc['doc_id'])}")
    print(f"  📊 Số chunk để test: {len(test_chunks)}")

    # ── Khởi tạo Summarizer ──────────────────────────────────────────────
    from services.summarization.summarizer import DocumentSummarizer

    print(f"\n  ⚙️  Khởi tạo DocumentSummarizer(strategy='{args.strategy}', run_nli={args.nli})...")
    t_init = time.time()
    try:
        summarizer = DocumentSummarizer(
            strategy=args.strategy,
            run_nli_check=args.nli,
        )
        print(f"  ✅ Khởi tạo thành công ({time.time() - t_init:.2f}s)")
    except Exception as e:
        print(f"  ❌ Khởi tạo thất bại: {e}")
        sys.exit(1)

    # ── Tóm tắt từng chunk ──────────────────────────────────────────────
    print_section("KẾT QUẢ TÓM TẮT TỪNG CHUNK")
    t_start = time.time()

    all_results = []
    for chunk in test_chunks:
        t_chunk = time.time()
        result = summarizer.summarize_chunk(chunk)
        elapsed = time.time() - t_chunk
        all_results.append(result)
        print_chunk_result(result, verbose=args.verbose)
        print(f"     ⏱️  Thời gian chunk này: {elapsed:.2f}s")

    total_elapsed = time.time() - t_start

    # ── Tóm tắt toàn bộ văn bản ──────────────────────────────────────────
    print_section("TỔNG HỢP VĂN BẢN")
    doc_result = summarizer.summarize_document(
        doc_id=first_doc["doc_id"],
        chunks=test_chunks,
    )

    print(f"  📄 Văn bản    : {first_doc.get('ten_van_ban', first_doc['doc_id'])}")
    print(f"  🏷️  Action    : {doc_result['overall_action']}")
    print(f"  📊 Status    : {doc_result['trang_thai_xuat_ban']}")
    print(f"  📝 Chunks    : {doc_result['total_chunks']}")
    print(f"  📃 Sentences : {doc_result['total_sentences']}")
    print(f"  🤖 Strategy  : {doc_result['strategies_used']}")
    if doc_result.get("avg_faithfulness") is not None:
        print(f"  💯 Avg Faith.: {doc_result['avg_faithfulness']:.4f}")

    stats = doc_result.get("nli_stats", {})
    if stats.get("total", 0) > 0:
        print(
            f"  🔬 NLI stats : ✅{stats['entailment']} / "
            f"🟡{stats['neutral']} / 🔴{stats['contradiction']} "
            f"(total={stats['total']})"
        )

    print(f"\n  ⏱️  Tổng thời gian: {total_elapsed:.2f}s")

    # ── Kiểm tra Publish Gate ────────────────────────────────────────────
    print_section("KIỂM TRA PUBLISH GATE (WF-03)")
    if doc_result["trang_thai_xuat_ban"] == "PUBLISHED":
        print("  ✅ PUBLISH GATE PASSED: Văn bản tự động PUBLISHED (không có contradiction)")
    elif doc_result["trang_thai_xuat_ban"] == "PENDING_REVIEW":
        if any(r.get("has_contradiction") for r in doc_result["chunk_results"]):
            print("  🔴 PUBLISH GATE BLOCKED: Có câu CONTRADICTION — văn bản phải rà soát trước")
        else:
            print("  🟡 PUBLISH GATE WARNED: Có câu NEUTRAL — cần rà soát nhưng chưa chặn")
    else:
        print(f"  ❓ Trạng thái không xác định: {doc_result['trang_thai_xuat_ban']}")

    print(f"\n{'=' * 65}")
    print("  ✅ Test hoàn tất!")
    print("=" * 65)

    return 0


if __name__ == "__main__":
    sys.exit(main())
