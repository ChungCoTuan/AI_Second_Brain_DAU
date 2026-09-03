# HƯỚNG DẪN THỰC THÀNH VÀ SỬ DỤNG DỮ LIỆU (DATA USAGE GUIDE)
## Dự Án: DAU Second Brain

> **Tài liệu liên quan:** [DAU_Second_Brain_Ke_Hoach_Du_Lieu.md](file:///e:/AISCBRAINDAU/docs/DAU_Second_Brain_Ke_Hoach_Du_Lieu.md) | [workflow.md](file:///e:/AISCBRAINDAU/docs/workflow.md) | [DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md](file:///e:/AISCBRAINDAU/docs/DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md) | [DAU_Second_Brain_Phan_Cong_RACI.md](file:///e:/AISCBRAINDAU/docs/DAU_Second_Brain_Phan_Cong_RACI.md)

Tài liệu này hướng dẫn chi tiết các bước cài đặt môi trường, chuẩn bị thư mục, chạy script tiền xử lý dữ liệu, định dạng các file JSON/JSONL đầu ra chuẩn Data Model (bao gồm đầy đủ `DocumentRelation`), và kiểm tra chất lượng bằng Pydantic.

---

## 1. Chuẩn Bị Môi Trường Làm Việc

### 1.1 Yêu cầu hệ thống
- Python **3.10+**
- Thư viện xử lý PDF và văn bản: `pdfplumber`, `PyMuPDF` (`fitz`), `pandas`, `pydantic`.
- Thư viện OCR (nếu xử lý văn bản dạng ảnh scan): `paddleocr` hoặc `pytesseract`.

### 1.2 Cài đặt dependencies
Mở terminal tại thư mục gốc dự án `AISCBRAINDAU` và thực hiện:

```bash
# 1. Khởi tạo môi trường ảo
python -m venv .venv

# 2. Kích hoạt môi trường ảo
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

# 3. Cài đặt các thư viện phục vụ xử lý dữ liệu
pip install pdfplumber PyMuPDF pandas pydantic python-dotenv
```

---

## 2. Chuẩn Bị Thư Mục & Thu Thập File Gốc

Tạo cấu trúc thư mục lưu trữ dữ liệu theo đúng quy ước:

```bash
mkdir -p data/raw/thong_tu
mkdir -p data/raw/quyet_dinh
mkdir -p data/raw/quy_che_noi_bo
mkdir -p data/processed
mkdir -p data/testset
```

### Đặt file PDF vào thư mục tương ứng:
- Đặt file PDF tải từ `chinhphu.vn` hoặc `moet.gov.vn` vào `data/raw/thong_tu/` hoặc `data/raw/quyet_dinh/`.
- Ví dụ file: `data/raw/thong_tu/08_2024_TT_BGDDT.pdf`

---

## 3. Quy Trình Chạy Script Xử Lý Dữ Liệu

### Bước 3.1: Viết & Chạy Script Preprocessing (`services/ingestion/preprocess.py`)
Script này chịu trách nhiệm:
1. Đọc tất cả các file PDF từ `data/raw/`.
2. Trích xuất text thô + số trang (`so_trang`), làm sạch header/footer/watermark và chuẩn hóa Unicode NFC.
3. Cắt đoạn văn bản theo **Điều / Khoản** (Structure Chunking).
4. Trích xuất 5 loại quan hệ `DocumentRelation` (`CAN_CU`, `THAY_THE`, `SUA_DOI`, `BAI_BO`, `LIEN_QUAN_NGU_NGHIA`).
5. Khởi tạo trạng thái xuất bản `trang_thai_xuat_ban = "PENDING_REVIEW"` cho cơ chế Publish Gate.
6. Xuất các file kết quả:
   - `data/processed/documents.jsonl`
   - `data/processed/chunks.jsonl`
   - `data/processed/document_relations.jsonl`

#### Ví dụ lệnh chạy:
```bash
python services/ingestion/preprocess.py --input_dir data/raw --output_dir data/processed
```

---

## 4. Định Dạng Cấu Trúc Các File Dữ Liệu Đầu Ra (Schemas)

### 📄 4.1 Schema File Metadata Văn Bản (`data/processed/documents.jsonl`)
Mỗi dòng là một đối tượng JSON đại diện cho 1 văn bản (Khớp chuẩn 100% Data Model `Document`):

```json
{
  "doc_id": "08_2024_TT_BGDDT",
  "so_hieu": "08/2024/TT-BGDĐT",
  "ten_van_ban": "Thông tư Ban hành Quy chế Đào tạo Đại học",
  "co_quan_ban_hanh": "Bộ Giáo dục và Đào tạo",
  "ngay_ban_hanh": "2024-03-15",
  "loai_van_ban": "Thông tư",
  "trich_yeu": "Ban hành quy chế đào tạo trình độ đại học áp dụng cho các cơ sở giáo dục đại học.",
  "chu_de": "DAO_TAO",
  "muc_do_lien_quan_dau": "GENERAL",
  "trang_thai_xuat_ban": "PENDING_REVIEW",
  "can_cu_dan_chieu": [
    "Luật Giáo dục đại học số 34/2018/QH14",
    "Nghị định 99/2019/NĐ-CP"
  ],
  "file_path": "data/raw/thong_tu/08_2024_TT_BGDDT.pdf"
}
```

---

### 🧩 4.2 Schema File Chunk Đoạn Văn Bản (`data/processed/chunks.jsonl`)
Mỗi dòng đại diện cho 1 Khoản / 1 Điều nhỏ đã chia (Bổ sung `so_trang` cho tính năng "Xem văn bản gốc" / Màn hình 4):

```json
{
  "chunk_id": "08_2024_TT_BGDDT_D5_K1",
  "doc_id": "08_2024_TT_BGDDT",
  "so_hieu": "08/2024/TT-BGDĐT",
  "dieu_so": 5,
  "khoan_so": 1,
  "so_trang": 4,
  "title": "Điều 5. Điều kiện cảnh báo học tập",
  "content": "Điều 5. Điều kiện cảnh báo học tập\n1. Sinh viên có điểm trung bình học kỳ dưới 1.0 sẽ bị cảnh báo học tập lần 1.",
  "token_count": 48,
  "chu_de": "DAO_TAO",
  "muc_do_lien_quan_dau": "GENERAL"
}
```

---

### 🕸️ 4.3 Schema File Quan Hệ Văn Bản (`data/processed/document_relations.jsonl`)
Mỗi dòng lưu trữ 1 mối quan hệ liên kết giữa 2 văn bản (Phục vụ Cây Văn Bản / WF-06), hỗ trợ đầy đủ 5 loại quan hệ trong `DocumentRelation`:

```json
{
  "relation_id": "rel_001",
  "document_id_a": "08_2024_TT_BGDDT",
  "document_id_b": "34_2018_QH14",
  "loai_quan_he": "CAN_CU",
  "mo_ta": "Căn cứ Luật Giáo dục đại học số 34/2018/QH14",
  "diem_tuong_dong": null
}
```

```json
{
  "relation_id": "rel_002",
  "document_id_a": "08_2024_TT_BGDDT",
  "document_id_b": "10_2016_TT_BGDDT",
  "loai_quan_he": "THAY_THE",
  "mo_ta": "Thay thế Thông tư số 10/2016/TT-BGDĐT",
  "diem_tuong_dong": null
}
```

---

### 🧪 4.4 Schema Tập Kiểm Thử Faithfulness Audit (`data/testset/faithfulness_samples.json`)
Dùng để đánh giá khả năng chống bịa đặt (Anti-Hallucination) và đối chiếu trích dẫn của hệ thống (Đầy đủ 3 nhãn NLI: `entailment`, `neutral`, `contradiction`):

```json
[
  {
    "sample_id": "test_001",
    "doc_id": "08_2024_TT_BGDDT",
    "chunk_id": "08_2024_TT_BGDDT_D5_K1",
    "premise": "Sinh viên có điểm trung bình học kỳ dưới 1.0 sẽ bị cảnh báo học tập lần 1.",
    "hypothesis": "Sinh viên đạt điểm trung bình 0.9/4.0 trong học kỳ 1 sẽ nhận cảnh báo học tập.",
    "label": "entailment",
    "notes": "Suy luận đúng hoàn toàn từ nội dung chunk_id"
  },
  {
    "sample_id": "test_002",
    "doc_id": "08_2024_TT_BGDDT",
    "chunk_id": "08_2024_TT_BGDDT_D5_K1",
    "premise": "Sinh viên có điểm trung bình học kỳ dưới 1.0 sẽ bị cảnh báo học tập lần 1.",
    "hypothesis": "Sinh viên bị cảnh báo học tập sẽ phải nộp phạt 500.000 VNĐ.",
    "label": "neutral",
    "notes": "Không đủ thông tin xác nhận trong văn bản (Trung lập)"
  },
  {
    "sample_id": "test_003",
    "doc_id": "08_2024_TT_BGDDT",
    "chunk_id": "08_2024_TT_BGDDT_D5_K1",
    "premise": "Sinh viên có điểm trung bình học kỳ dưới 1.0 sẽ bị cảnh báo học tập lần 1.",
    "hypothesis": "Sinh viên bị cảnh báo học tập lần 1 sẽ ngay lập tức bị buộc xuất học.",
    "label": "contradiction",
    "notes": "Bịa đặt / Mâu thuẫn trực tiếp với nội dung văn bản"
  }
]
```

---

## 5. Script Kiểm Tra Tính Hợp Lệ Dữ Liệu Chi Tiết Với Pydantic (`services/ingestion/validate_data.py`)

Dưới đây là mã nguồn Python hoàn chỉnh dùng thư viện `Pydantic` để kiểm duyệt tính hợp lệ của dữ liệu trước khi nạp vào hệ thống:

```python
"""Script kiểm tra tính hợp lệ dữ liệu (Data Quality Gate) cho DAU Second Brain."""

from enum import Enum
import json
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError


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
    print(f"✅ Documents ({file_path.name}): {count} văn bản hợp lệ!")
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
    print(f"✅ Chunks ({file_path.name}): {count} đoạn hợp lệ!")
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
    print(f"✅ Relations ({file_path.name}): {count} quan hệ văn bản hợp lệ!")
    return count


def validate_faithfulness_samples(file_path: Path) -> int:
    with open(file_path, "r", encoding="utf-8") as f:
        data_list = json.load(f)
    for idx, item in enumerate(data_list, 1):
        FaithfulnessSampleSchema(**item)
    print(f"✅ Faithfulness Samples ({file_path.name}): {len(data_list)} mẫu NLI hợp lệ!")
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
        print("🎉 TOÀN BỘ DỮ LIỆU ĐẠT TIÊU CHUẨN CHẤT LƯỢNG!")
    except ValidationError as e:
        print(f"❌ PHÁT HIỆN LỖI SCHEMA DỮ LIỆU:\n{e}")
```

#### Lệnh chạy kiểm duyệt:
```bash
python services/ingestion/validate_data.py
```

---

## 6. Bảng Phân Công Nhiệm Vụ Làm Dữ Liệu (Chuẩn RACI)

> **Căn cứ chiếu:** [DAU_Second_Brain_Phan_Cong_RACI.md](file:///e:/AISCBRAINDAU/docs/DAU_Second_Brain_Phan_Cong_RACI.md) — Thành viên 1 (TV1 / Track A - Data & Pipeline) giữ vai trò **R** (Responsible) và **A** (Accountable) toàn bộ các hạng mục thuộc Sprint 0 (Thu thập & Tiền xử lý dữ liệu). Thành viên 2 (TV2 / Track B - AI Core) đóng vai trò **C** (Consulted).

| Hạng mục Công việc | TV1 (Track A - Data & Pipeline) | TV2 (Track B - AI Core) |
|---|---|---|
| **Thu thập PDF chinhphu.vn & DAU** | **R / A** (Thực hiện & Phê duyệt chính) | **C** (Tư vấn nguồn/lĩnh vực) |
| **Viết Script Preprocessing, Chunking & so_trang** | **R / A** (Thực hiện & Phê duyệt chính) | **C** (Đóng góp regex) |
| **Trích xuất Quan Hệ DocumentRelation (5 Loại)** | **R / A** (Thực hiện & Phê duyệt chính) | **C** (Tư vấn similarity) |
| **Gán nhãn Gold Summary, Topic & Publish Status** | **R / A** (Thực hiện & Phê duyệt chính) | **C** (Review chất lượng) |
| **Xây tập Test Faithfulness (NLI Pairs 3 Nhãn)** | **R** (Hỗ trợ chuẩn bị context) | **R / A** (Chủ trì xây dựng & Đánh giá NLI) |
