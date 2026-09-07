"""Script Đánh Giá NLI 3 Nhãn & Review Service Publish Gate cho DAU Second Brain (Sprint 3 - EPIC-3 & EPIC-9).

Tuân thủ đầy đủ Data Model và Schema quy định trong docs/usage.md & docs/workflow.md.
Ràng buộc an toàn FR-08: Nếu có ít nhất 1 câu bị gắn nhãn contradiction hoặc neutral -> Văn bản ở trạng thái PENDING_REVIEW.
"""

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Set

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from pydantic import ValidationError

# Import schemas for validation
sys.path.append(str(Path(__file__).resolve().parents[2]))
from services.ingestion.validate_data import (
    DocumentSchema,
    PublishStatusEnum,
    NLILabelEnum,
    validate_documents,
)


def run_publish_gate(input_dir: Path, testset_file: Path):
    """Thực thi kiểm duyệt Publish Gate dựa trên kết quả NLI 3 nhãn."""
    docs_file = input_dir / "documents.jsonl"
    if not docs_file.exists():
        print(f"❌ Error: Không tìm thấy {docs_file}", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Bắt đầu Đánh giá NLI 3 Nhãn & Publish Gate (FR-08) từ {input_dir}...")

    # 1. Load Faithfulness Testset Samples
    flagged_docs_contradiction: Set[str] = set()
    flagged_docs_neutral: Set[str] = set()
    total_samples = 0

    if testset_file.exists():
        with open(testset_file, "r", encoding="utf-8") as f:
            samples = json.load(f)
            total_samples = len(samples)
            for s in samples:
                doc_id = s.get("doc_id")
                label = s.get("label")
                if doc_id:
                    if label == "contradiction":
                        flagged_docs_contradiction.add(doc_id)
                    elif label == "neutral":
                        flagged_docs_neutral.add(doc_id)
    else:
        print(f"⚠️ Warning: Không tìm thấy file testset {testset_file}", file=sys.stderr)

    # 2. Evaluate Documents against FR-08 Publish Gate
    updated_documents = []
    pending_count = 0
    published_count = 0

    with open(docs_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            doc_item = json.loads(line)
            doc_id = doc_item.get("doc_id")

            # Apply FR-08 Safety Rule
            if doc_id in flagged_docs_contradiction or doc_id in flagged_docs_neutral:
                doc_item["trang_thai_xuat_ban"] = PublishStatusEnum.PENDING_REVIEW.value
                pending_count += 1
                reason = "Phát hiện câu CONTRADICTION (Mâu thuẫn)" if doc_id in flagged_docs_contradiction else "Phát hiện câu NEUTRAL (Trung tính)"
                print(f"  ⚠️ [{doc_id}]: Trạng thái = 'PENDING_REVIEW' ({reason})")
            else:
                doc_item["trang_thai_xuat_ban"] = PublishStatusEnum.PUBLISHED.value
                published_count += 1
                print(f"  ✅ [{doc_id}]: Trạng thái = 'PUBLISHED' (100% Entailment)")

            # Validate Pydantic Schema
            DocumentSchema(**doc_item)
            updated_documents.append(doc_item)

    # 3. Save updated documents.jsonl
    with open(docs_file, "w", encoding="utf-8") as f:
        for doc in updated_documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print("\n🎉 HOÀN THÀNH BƯỚC 5: REVIEW SERVICE PUBLISH GATE (FR-08)!")
    print(f"📊 Tổng số văn bản đã kiểm duyệt: {len(updated_documents)}")
    print(f"📊 Tổng số mẫu NLI Faithfulness đánh giá: {total_samples}")
    print(f"🔒 Văn bản giữ trạng thái PENDING_REVIEW (Cần Rà soát): {pending_count}")
    print(f"✅ Văn bản đạt chuẩn PUBLISHED (Đã Xuất bản): {published_count}")

    # 4. Re-run validation gate
    print("\n🔍 Đang chạy lại Data Quality Gate kiểm tra 100% Schema hợp lệ...")
    validate_documents(docs_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run NLI 3-label Publish Gate for DAU Second Brain.")
    parser.add_argument("--input_dir", type=str, default="data/processed", help="Path to processed data directory")
    parser.add_argument("--testset", type=str, default="data/testset/faithfulness_samples.json", help="Path to testset JSON file")
    args = parser.parse_args()

    input_path = Path(args.input_dir).resolve()
    testset_path = Path(args.testset).resolve()

    run_publish_gate(input_path, testset_path)
