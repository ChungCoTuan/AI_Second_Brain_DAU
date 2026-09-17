"""Script kiểm tra tính hợp lệ dữ liệu (Data Quality Gate) cho DAU Second Brain.

Tuân thủ đầy đủ Data Model và Schema quy định trong docs/usage.md & docs/workflow.md.
"""

from enum import Enum
import json
from pathlib import Path
import sys
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


# --- ENUM DEFINITIONS ---
class TopicEnum(str, Enum):
    DAO_TAO = "DAO_TAO"
    TAI_CHINH = "TAI_CHINH"
    NHAN_SU = "NHAN_SU"
    TUYEN_SINH = "TUYEN_SINH"
    CO_SO_VAT_CHAT = "CO_SO_VAT_CHAT"
    KHAC = "KHAC"


class DAURelevanceEnum(str, Enum):
    DIRECT = "DIRECT"
    GENERAL = "GENERAL"
    REFERENCE = "REFERENCE"


class PublishStatusEnum(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"


class RelationTypeEnum(str, Enum):
    CAN_CU = "CAN_CU"
    THAY_THE = "THAY_THE"
    SUA_DOI = "SUA_DOI"
    BAI_BO = "BAI_BO"
    LIEN_QUAN_NGU_NGHIA = "LIEN_QUAN_NGU_NGHIA"


class NLILabelEnum(str, Enum):
    ENTAILMENT = "entailment"
    NEUTRAL = "neutral"
    CONTRADICTION = "contradiction"


# --- PYDANTIC SCHEMAS ---
class DocumentSchema(BaseModel):
    doc_id: str
    so_hieu: str
    ten_van_ban: str
    co_quan_ban_hanh: str
    ngay_ban_hanh: str
    loai_van_ban: str
    trich_yeu: str
    chu_de: TopicEnum
    muc_do_lien_quan_dau: DAURelevanceEnum
    trang_thai_xuat_ban: PublishStatusEnum = PublishStatusEnum.PENDING_REVIEW
    can_cu_dan_chieu: List[str] = Field(default_factory=list)
    file_path: str


class DocumentChunkSchema(BaseModel):
    chunk_id: str
    doc_id: str
    so_hieu: str
    dieu_so: Optional[int] = None
    khoan_so: Optional[int] = None
    so_trang: int = Field(gt=0, description="Số trang trong file PDF gốc (1-indexed)")
    title: str
    content: str
    token_count: int = Field(gt=0)
    chu_de: TopicEnum
    muc_do_lien_quan_dau: DAURelevanceEnum


class DocumentRelationSchema(BaseModel):
    relation_id: str
    document_id_a: str
    document_id_b: str
    loai_quan_he: RelationTypeEnum
    mo_ta: Optional[str] = None
    diem_tuong_dong: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class FaithfulnessSampleSchema(BaseModel):
    sample_id: str
    doc_id: str
    chunk_id: str
    premise: str
    hypothesis: str
    label: NLILabelEnum
    notes: Optional[str] = None


# --- VALIDATION FUNCTIONS ---
def validate_documents(file_path: Path) -> int:
    count = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            data = json.loads(line)
            DocumentSchema(**data)
            count += 1
    print(f"  ✅ Documents ({file_path.name}): {count} văn bản hợp lệ 100%!")
    return count


def validate_chunks(file_path: Path) -> int:
    count = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            data = json.loads(line)
            DocumentChunkSchema(**data)
            count += 1
    print(f"  ✅ Chunks ({file_path.name}): {count} đoạn hợp lệ 100%!")
    return count


def validate_relations(file_path: Path) -> int:
    count = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            data = json.loads(line)
            DocumentRelationSchema(**data)
            count += 1
    print(f"  ✅ Relations ({file_path.name}): {count} quan hệ hợp lệ 100%!")
    return count


def validate_faithfulness_samples(file_path: Path) -> int:
    with open(file_path, "r", encoding="utf-8") as f:
        data_list = json.load(f)
    for idx, item in enumerate(data_list, 1):
        FaithfulnessSampleSchema(**item)
    print(f"  ✅ Faithfulness Samples ({file_path.name}): {len(data_list)} mẫu NLI hợp lệ 100%!")
    return len(data_list)


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[2]
    processed_dir = base_dir / "data" / "processed"
    testset_dir = base_dir / "data" / "testset"

    print("🔍 Đang tiến hành kiểm duyệt dữ liệu (Data Quality Gate)...")
    try:
        if (processed_dir / "documents.jsonl").exists():
            validate_documents(processed_dir / "documents.jsonl")
        if (processed_dir / "chunks.jsonl").exists():
            validate_chunks(processed_dir / "chunks.jsonl")
        if (processed_dir / "document_relations.jsonl").exists():
            validate_relations(processed_dir / "document_relations.jsonl")
        if (testset_dir / "faithfulness_samples.json").exists():
            validate_faithfulness_samples(testset_dir / "faithfulness_samples.json")
        print("\n🎉 TOÀN BỘ DỮ LIỆU ĐẠT TIÊU CHUẨN CHẤT LƯỢNG DATA MODEL!")
    except ValidationError as e:
        print(f"\n❌ PHÁT HIỆN LỖI SCHEMA DỮ LIỆU:\n{e}")
        sys.exit(1)
