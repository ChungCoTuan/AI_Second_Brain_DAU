"""Script Phân loại Chủ đề & Trích xuất Thực thể NER cho DAU Second Brain (Sprint 2 - EPIC-2).

Tuân thủ đầy đủ Data Model và Schema quy định trong docs/usage.md & docs/workflow.md.
"""

import argparse
from enum import Enum
import json
import os
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import pymupdf as fitz
from pydantic import ValidationError

# Import schemas for validation
sys.path.append(str(Path(__file__).resolve().parents[2]))
from services.ingestion.validate_data import (
    DocumentChunkSchema,
    DocumentSchema,
    TopicEnum,
    DAURelevanceEnum,
    PublishStatusEnum,
)


def normalize_nfc(text: str) -> str:
    """Chuẩn hóa chuỗi tiếng Việt về dạng Unicode NFC."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_full_text_from_pdf(pdf_path: Path) -> str:
    """Đọc toàn bộ văn bản từ file PDF raw nếu tồn tại."""
    if not pdf_path.exists():
        return ""
    full_text_list = []
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text = page.get_text()
            if text:
                full_text_list.append(text)
        doc.close()
    except Exception as e:
        print(f"  ⚠️ Warning: Không thể đọc file PDF {pdf_path}: {e}", file=sys.stderr)
    return normalize_nfc("\n".join(full_text_list))


def classify_topic(doc_id: str, title: str, trich_yeu: str, full_text: str) -> TopicEnum:
    """Phân loại chủ đề văn bản dựa trên từ khóa tiếng Việt và tên file (Rule-based Topic Classification)."""
    combined = normalize_nfc(f"{doc_id} {title} {trich_yeu} {full_text[:4000]}").lower()

    # 1. Tuyen sinh
    tuyen_sinh_kw = [
        "tuyển sinh", "tuyensinh", "chỉ tiêu tuyển sinh", "chitietuyensinh", "xét tuyển",
        "phương thức tuyển sinh", "nguyện vọng", "thi tốt nghiệp thpt", "trúng tuyển", "tuyển sinh 20"
    ]
    if any(kw in combined for kw in tuyen_sinh_kw):
        return TopicEnum.TUYEN_SINH

    # 2. Tai chinh
    tai_chinh_kw = [
        "học phí", "hocphi", "miễn giảm học phí", "lệ phí", "lephi", "ngân sách", "tài chính",
        "dự toán", "chế độ chính sách", "trợ cấp", "chi tiêu nội bộ"
    ]
    if any(kw in combined for kw in tai_chinh_kw):
        return TopicEnum.TAI_CHINH

    # 3. Nhan su
    nhan_su_kw = [
        "giảng viên", "giangvien", "định mức giờ dạy", "khen thưởng", "khenthuong", "kỷ luật",
        "viên chức", "vithanthuongxuyen", "người lao động", "bổ nhiệm", "thi đua khen thưởng",
        "thidua", "tiêu chuẩn xét thi đua", "chỉ tiêu giảng dạy"
    ]
    if any(kw in combined for kw in nhan_su_kw):
        return TopicEnum.NHAN_SU

    # 4. Co so vat chat
    co_so_vat_chat_kw = [
        "cơ sở vật chất", "cosovatchat", "trang thiết bị", "phòng học", "thư viện", "ký túc xá",
        "tài sản", "mua sắm", "sửa chữa", "ai-native", "competency-based"
    ]
    if any(kw in combined for kw in co_so_vat_chat_kw):
        return TopicEnum.CO_SO_VAT_CHAT

    # 5. Dao tao
    dao_tao_kw = [
        "đào tạo", "daotao", "chương trình đào tạo", "chuongtrinh", "học phần", "hocphan",
        "tín chỉ", "tinchi", "đồ án", "doan", "datn", "tốt nghiệp", "totnghiep", "thi trực tuyến",
        "thitructuyen", "cảnh báo học tập", "xét miễn học phần", "xetmien", "chuẩn đầu ra", "chuandaura",
        "quy chế đào tạo", "kiểm định chất lượng", "kiemdinh", "đại học", "thạc sĩ", "thacsi",
        "văn bằng", "vanbang", "chứng chỉ", "chungchi", "thực tập", "thuctap", "ngành đào tạo",
        "khung trình độ quốc gia"
    ]
    if any(kw in combined for kw in dao_tao_kw):
        return TopicEnum.DAO_TAO

    return TopicEnum.KHAC


def extract_ner_entities(doc_item: Dict[str, Any], full_text: str) -> Dict[str, Any]:
    """Trích xuất thực thể NER nâng cao (Số hiệu, Cơ quan ban hành, Ngày ban hành, Loại văn bản, Trích yếu)."""
    file_path_str = doc_item.get("file_path", "")
    stem = Path(file_path_str).stem if file_path_str else doc_item.get("doc_id", "")
    header_text = full_text[:1500] if full_text else doc_item.get("ten_van_ban", "")

    # 1. Cơ quan ban hành & Mức độ liên quan DAU
    if "Trường Đại học Kiến trúc Đà Nẵng" in header_text or "ĐẠI HỌC KIẾN TRÚC ĐÀ NẴNG" in header_text or "NT" in stem:
        co_quan_ban_hanh = "Trường Đại học Kiến trúc Đà Nẵng"
        muc_do_lien_quan = DAURelevanceEnum.DIRECT
    elif "CHÍNH PHỦ" in header_text or "CP" in stem:
        co_quan_ban_hanh = "Chính phủ"
        muc_do_lien_quan = DAURelevanceEnum.GENERAL
    elif "QUỐC HỘI" in header_text or "QH" in stem:
        co_quan_ban_hanh = "Quốc hội"
        muc_do_lien_quan = DAURelevanceEnum.GENERAL
    else:
        co_quan_ban_hanh = "Bộ Giáo dục và Đào tạo"
        muc_do_lien_quan = DAURelevanceEnum.GENERAL

    # 2. Loại văn bản
    if re.search(r"\bThông tư\b", header_text, re.IGNORECASE) or "TT" in stem:
        loai_van_ban = "Thông tư"
    elif re.search(r"\bQuyết định\b", header_text, re.IGNORECASE) or "QD" in stem or "QĐ" in stem:
        loai_van_ban = "Quyết định"
    elif re.search(r"\bNghị định\b", header_text, re.IGNORECASE) or "ND" in stem or "NĐ" in stem:
        loai_van_ban = "Nghị định"
    elif re.search(r"\bThông báo\b", header_text, re.IGNORECASE) or "TB" in stem:
        loai_van_ban = "Thông báo"
    elif re.search(r"\bHướng dẫn\b", header_text, re.IGNORECASE) or "HD" in stem or "HĐ" in stem:
        loai_van_ban = "Hướng dẫn"
    elif re.search(r"\bQuy chế\b", header_text, re.IGNORECASE) or "QC" in stem:
        loai_van_ban = "Quy chế"
    elif re.search(r"\bLuật\b", header_text, re.IGNORECASE) or "Luật" in stem:
        loai_van_ban = "Luật"
    elif re.search(r"\bCông văn\b", header_text, re.IGNORECASE) or "CV" in stem:
        loai_van_ban = "Công văn"
    else:
        loai_van_ban = "Quy định"

    # 3. Số hiệu văn bản
    so_hieu = doc_item.get("so_hieu", "")
    so_hieu_match = re.search(r"(?:Số|Số:)\s*([\d\w\-/]+(?:\-[A-ZĐ]+)?)", header_text, re.IGNORECASE)
    if so_hieu_match:
        extracted_so_hieu = so_hieu_match.group(1).strip()
        if len(extracted_so_hieu) > 3:
            so_hieu = extracted_so_hieu
    if not so_hieu or "/" not in so_hieu:
        clean_stem = stem.replace("_", "/").replace("-", "/")
        so_hieu = doc_item.get("so_hieu", clean_stem)

    # 4. Ngày ban hành
    ngay_ban_hanh = doc_item.get("ngay_ban_hanh", "2026-01-01")
    ngay_bh_match = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", header_text, re.IGNORECASE)
    if ngay_bh_match:
        day, month, year = ngay_bh_match.groups()
        ngay_ban_hanh = f"{year}-{int(month):02d}-{int(day):02d}"

    # 5. Trích yếu
    trich_yeu = doc_item.get("trich_yeu", "")
    trich_yeu_match = re.search(r"(Về việc\s+[^.\n]+|V/v\s+[^.\n]+|Ban hành\s+[^.\n]+|Quy định\s+[^.\n]+|Quy chế\s+[^.\n]+)", header_text, re.IGNORECASE)
    if trich_yeu_match:
        extracted_ty = trich_yeu_match.group(0).strip()
        if len(extracted_ty) > 10 and "BỘ GIÁO DỤC" not in extracted_ty and "TRƯỜNG ĐẠI HỌC" not in extracted_ty:
            trich_yeu = extracted_ty

    if not trich_yeu or trich_yeu in ["Trích yếu văn bản", "BỘ GIÁO DỤC VÀ ĐÀO TẠO"]:
        clean_name = stem.replace("BGD_TT_", "Thông tư ").replace("NT_QD_", "Quyết định ").replace("NT_QC_", "Quy chế ").replace("_", " ")
        trich_yeu = f"Về việc {clean_name}"

    # 6. Tên văn bản
    ten_van_ban = f"{loai_van_ban} {so_hieu}: {trich_yeu}"

    # 7. Phân loại chủ đề
    doc_id = doc_item.get("doc_id", "")
    chu_de = classify_topic(doc_id, ten_van_ban, trich_yeu, full_text)

    return {
        "co_quan_ban_hanh": co_quan_ban_hanh,
        "muc_do_lien_quan_dau": muc_do_lien_quan,
        "loai_van_ban": loai_van_ban,
        "so_hieu": so_hieu,
        "ngay_ban_hanh": ngay_ban_hanh,
        "trich_yeu": trich_yeu,
        "ten_van_ban": ten_van_ban,
        "chu_de": chu_de
    }


def process_extraction_and_classification(input_dir: Path, output_dir: Path):
    """Tiến hành phân loại chủ đề và trích xuất thực thể NER cho toàn bộ dữ liệu."""
    base_dir = input_dir.parents[0] if input_dir.name == "processed" else input_dir
    raw_dir = base_dir / "data" / "raw" if (base_dir / "data" / "raw").exists() else base_dir / "raw"

    docs_file = input_dir / "documents.jsonl"
    chunks_file = input_dir / "chunks.jsonl"

    if not docs_file.exists():
        print(f"❌ Error: Không tìm thấy {docs_file}", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Bắt đầu Phân loại Chủ đề & Trích xuất Thực thể NER từ {input_dir}...")

    # Load documents
    updated_documents = []
    topic_counts = {t.value: 0 for t in TopicEnum}
    doc_topic_map = {}
    doc_relevance_map = {}

    with open(docs_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            doc_item = json.loads(line)
            file_path_str = doc_item.get("file_path", "")

            # Resolve actual PDF path
            pdf_path = base_dir / file_path_str if file_path_str else None
            if not pdf_path or not pdf_path.exists():
                pdf_path = raw_dir / Path(file_path_str).name if file_path_str else None

            full_text = extract_full_text_from_pdf(pdf_path) if pdf_path and pdf_path.exists() else ""

            # Extract NER & Classify Topic
            ner_result = extract_ner_entities(doc_item, full_text)

            # Update Document item
            doc_item["co_quan_ban_hanh"] = ner_result["co_quan_ban_hanh"]
            doc_item["muc_do_lien_quan_dau"] = ner_result["muc_do_lien_quan_dau"].value
            doc_item["loai_van_ban"] = ner_result["loai_van_ban"]
            doc_item["so_hieu"] = ner_result["so_hieu"]
            doc_item["ngay_ban_hanh"] = ner_result["ngay_ban_hanh"]
            doc_item["trich_yeu"] = ner_result["trich_yeu"]
            doc_item["ten_van_ban"] = ner_result["ten_van_ban"]
            doc_item["chu_de"] = ner_result["chu_de"].value

            # Validate against Pydantic DocumentSchema
            DocumentSchema(**doc_item)

            updated_documents.append(doc_item)
            topic_counts[ner_result["chu_de"].value] += 1
            doc_topic_map[doc_item["doc_id"]] = doc_item["chu_de"]
            doc_relevance_map[doc_item["doc_id"]] = doc_item["muc_do_lien_quan_dau"]

            print(f"  ✅ [{doc_item['doc_id']}]: Loại = '{doc_item['loai_van_ban']}', Chủ đề = '{doc_item['chu_de']}', Ngày BH = '{doc_item['ngay_ban_hanh']}'")

    # Update Chunks if chunks.jsonl exists
    updated_chunks = []
    if chunks_file.exists():
        with open(chunks_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                chunk_item = json.loads(line)
                doc_id = chunk_item.get("doc_id")
                if doc_id in doc_topic_map:
                    chunk_item["chu_de"] = doc_topic_map[doc_id]
                if doc_id in doc_relevance_map:
                    chunk_item["muc_do_lien_quan_dau"] = doc_relevance_map[doc_id]

                # Validate against Pydantic DocumentChunkSchema
                DocumentChunkSchema(**chunk_item)
                updated_chunks.append(chunk_item)

    # Save updated outputs
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "documents.jsonl", "w", encoding="utf-8") as f:
        for doc in updated_documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    if updated_chunks:
        with open(output_dir / "chunks.jsonl", "w", encoding="utf-8") as f:
            for chunk in updated_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print("\n🎉 HOÀN THÀNH PHÂN LOẠI CHỦ ĐỀ & TRÍCH XUẤT NER!")
    print(f"📊 Tổng số văn bản đã xử lý: {len(updated_documents)}")
    print(f"📊 Tổng số chunks đã cập nhật: {len(updated_chunks)}")
    print("📈 Thống kê phân bố Chủ đề (TopicEnum):")
    for topic, count in topic_counts.items():
        print(f"   - {topic}: {count} văn bản")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract NER and classify topics for DAU Second Brain.")
    parser.add_argument("--input_dir", type=str, default="data/processed", help="Path to processed data directory")
    parser.add_argument("--output_dir", type=str, default="data/processed", help="Path to output processed data directory")
    args = parser.parse_args()

    input_path = Path(args.input_dir).resolve()
    output_path = Path(args.output_dir).resolve()

    process_extraction_and_classification(input_path, output_path)
