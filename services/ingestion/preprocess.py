"""Script Preprocessing & Structure Chunking cho DAU Second Brain.

Tuân thủ đầy đủ Data Model và Schema quy định trong docs/usage.md & docs/workflow.md.
"""

import argparse
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



def normalize_nfc(text: str) -> str:
    """Chuẩn hóa chuỗi tiếng Việt về dạng Unicode NFC."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def clean_page_text(text: str) -> str:
    """Làm sạch header, footer, watermark và các dòng thừa."""
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^(Trang\s+\d+|\d+/\d+|\-\s*\d+\s*\-|\-\-\-\-\-)$", stripped, re.IGNORECASE):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def extract_metadata_from_text(file_path: Path, full_text: str, folder_type: str) -> Dict[str, Any]:
    """Trích xuất metadata cố định từ nội dung văn bản."""
    stem = file_path.stem
    doc_id = re.sub(r"[^\w\-]", "_", stem)

    # 2. Số hiệu
    so_hieu_match = re.search(r"Số:\s*([\d\w\-/]+(?:\-[A-ZĐ]+)?)", full_text, re.IGNORECASE)
    if so_hieu_match:
        so_hieu = so_hieu_match.group(1).strip()
    else:
        so_hieu = stem.replace("_", "/")

    # 3. Ngày ban hành
    ngay_bh_match = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", full_text, re.IGNORECASE)
    if ngay_bh_match:
        day, month, year = ngay_bh_match.groups()
        ngay_ban_hanh = f"{year}-{int(month):02d}-{int(day):02d}"
    else:
        ngay_ban_hanh = "2026-01-01"

    # 4. Cơ quan ban hành & Mức độ liên quan
    if "quy_che_noi_bo" in folder_type or "DAU" in stem:
        co_quan_ban_hanh = "Trường Đại học Kiến trúc Đà Nẵng"
        muc_do_lien_quan = "DIRECT"
    elif "CP_" in stem or "Nghị định" in full_text[:500]:
        co_quan_ban_hanh = "Chính phủ"
        muc_do_lien_quan = "GENERAL"
    elif "Luật" in stem or "QH" in stem:
        co_quan_ban_hanh = "Quốc hội"
        muc_do_lien_quan = "GENERAL"
    else:
        co_quan_ban_hanh = "Bộ Giáo dục và Đào tạo"
        muc_do_lien_quan = "GENERAL"

    # 5. Loại văn bản
    if "TT" in stem or "Thông tư" in full_text[:300]:
        loai_van_ban = "Thông tư"
    elif "QD" in stem or "Quyết định" in full_text[:300]:
        loai_van_ban = "Quyết định"
    elif "ND" in stem or "Nghị định" in full_text[:300]:
        loai_van_ban = "Nghị định"
    elif "Luật" in stem or "QH" in stem:
        loai_van_ban = "Luật"
    elif "CV" in stem or "Công văn" in full_text[:300]:
        loai_van_ban = "Công văn"
    else:
        loai_van_ban = "Quy định"

    # 6. Trích yếu
    trich_yeu_match = re.search(r"(Về việc\s+[^.\n]+|V/v\s+[^.\n]+|Ban hành\s+[^.\n]+)", full_text[:1500], re.IGNORECASE)
    if trich_yeu_match:
        trich_yeu = trich_yeu_match.group(0).strip()
    else:
        first_lines = [line.strip() for line in full_text.split("\n")[:10] if len(line.strip()) > 15]
        trich_yeu = first_lines[0] if first_lines else "Trích yếu văn bản"

    # 7. Chủ đề (TopicEnum)
    full_lower = full_text.lower()
    if any(k in full_lower for k in ["tuyển sinh", "xét tuyển", "chỉ tiêu"]):
        chu_de = "TUYEN_SINH"
    elif any(k in full_lower for k in ["học phí", "tài chính", "ngân sách", "lệ phí"]):
        chu_de = "TAI_CHINH"
    elif any(k in full_lower for k in ["giảng viên", "cán bộ", "nhân sự", "tuyển dụng"]):
        chu_de = "NHAN_SU"
    elif any(k in full_lower for k in ["chuyển đổi số", "cơ sở vật chất", "thiết bị"]):
        chu_de = "CO_SO_VAT_CHAT"
    elif any(k in full_lower for k in ["đào tạo", "chương trình", "tín chỉ", "quy chế"]):
        chu_de = "DAO_TAO"
    else:
        chu_de = "KHAC"

    # 8. Căn cứ dẫn chiếu
    can_cu_matches = re.findall(r"Căn cứ\s+([^;\n\.]+)", full_text[:3000], re.IGNORECASE)
    can_cu_list = [c.strip() for c in can_cu_matches if len(c.strip()) > 10][:5]

    try:
        rel_path = str(file_path.relative_to(file_path.parents[2]))
    except ValueError:
        rel_path = str(file_path)

    return {
        "doc_id": doc_id,
        "so_hieu": so_hieu,
        "ten_van_ban": f"{loai_van_ban} {so_hieu}: {trich_yeu}" if len(trich_yeu) < 100 else f"{loai_van_ban} {so_hieu}",
        "co_quan_ban_hanh": co_quan_ban_hanh,
        "ngay_ban_hanh": ngay_ban_hanh,
        "loai_van_ban": loai_van_ban,
        "trich_yeu": trich_yeu,
        "chu_de": chu_de,
        "muc_do_lien_quan_dau": muc_do_lien_quan,
        "trang_thai_xuat_ban": "PENDING_REVIEW",
        "can_cu_dan_chieu": can_cu_list,
        "file_path": rel_path,
    }


def chunk_document_by_dieu(pages_text: List[Tuple[int, str]], doc_meta: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Cắt đoạn văn bản theo Điều / Khoản và trích xuất DocumentRelation."""
    chunks = []
    relations = []

    doc_id = doc_meta["doc_id"]
    so_hieu = doc_meta["so_hieu"]
    chu_de = doc_meta["chu_de"]
    muc_do_lien_quan = doc_meta["muc_do_lien_quan_dau"]

    line_page_tuples = []
    for page_num, text in pages_text:
        for line in text.split("\n"):
            line_page_tuples.append((page_num, line))

    dieu_pattern = re.compile(r"^\s*(Điều\s+(\d+)\.?:?\s*(.*))", re.IGNORECASE)

    current_dieu_num = None
    current_dieu_title = ""
    current_chunk_lines = []
    current_page_start = 1
    chunk_index = 1
    rel_idx = 1

    for page_num, line in line_page_tuples:
        line_str = line.strip()
        if not line_str:
            continue

        rel_match_can_cu = re.search(r"Căn cứ\s+([^;\n\.]+)", line_str, re.IGNORECASE)
        if rel_match_can_cu:
            target_ref = rel_match_can_cu.group(1).strip()
            if len(target_ref) > 8:
                relations.append({
                    "relation_id": f"rel_{doc_id}_{rel_idx}",
                    "document_id_a": doc_id,
                    "document_id_b": re.sub(r"\W+", "_", target_ref)[:50],
                    "loai_quan_he": "CAN_CU",
                    "mo_ta": f"Căn cứ {target_ref}",
                    "diem_tuong_dong": None,
                })
                rel_idx += 1

        rel_match_thay_the = re.search(r"thay thế\s+([^;\n\.]+)", line_str, re.IGNORECASE)
        if rel_match_thay_the:
            target_ref = rel_match_thay_the.group(1).strip()
            relations.append({
                "relation_id": f"rel_{doc_id}_{rel_idx}",
                "document_id_a": doc_id,
                "document_id_b": re.sub(r"\W+", "_", target_ref)[:50],
                "loai_quan_he": "THAY_THE",
                "mo_ta": f"Thay thế {target_ref}",
                "diem_tuong_dong": None,
            })
            rel_idx += 1

        rel_match_sua_doi = re.search(r"sửa đổi,?\s+bổ sung\s+([^;\n\.]+)", line_str, re.IGNORECASE)
        if rel_match_sua_doi:
            target_ref = rel_match_sua_doi.group(1).strip()
            relations.append({
                "relation_id": f"rel_{doc_id}_{rel_idx}",
                "document_id_a": doc_id,
                "document_id_b": re.sub(r"\W+", "_", target_ref)[:50],
                "loai_quan_he": "SUA_DOI",
                "mo_ta": f"Sửa đổi, bổ sung {target_ref}",
                "diem_tuong_dong": None,
            })
            rel_idx += 1

        rel_match_bai_bo = re.search(r"bãi bỏ\s+([^;\n\.]+)", line_str, re.IGNORECASE)
        if rel_match_bai_bo:
            target_ref = rel_match_bai_bo.group(1).strip()
            relations.append({
                "relation_id": f"rel_{doc_id}_{rel_idx}",
                "document_id_a": doc_id,
                "document_id_b": re.sub(r"\W+", "_", target_ref)[:50],
                "loai_quan_he": "BAI_BO",
                "mo_ta": f"Bãi bỏ {target_ref}",
                "diem_tuong_dong": None,
            })
            rel_idx += 1

        dieu_m = dieu_pattern.match(line_str)
        if dieu_m:
            if current_chunk_lines:
                chunk_content = normalize_nfc("\n".join(current_chunk_lines))
                if len(chunk_content) > 20:
                    chunks.append({
                        "chunk_id": f"{doc_id}_D{current_dieu_num or chunk_index}",
                        "doc_id": doc_id,
                        "so_hieu": so_hieu,
                        "dieu_so": current_dieu_num or chunk_index,
                        "khoan_so": 1,
                        "so_trang": current_page_start,
                        "title": current_dieu_title or f"Điều {current_dieu_num or chunk_index}",
                        "content": chunk_content,
                        "token_count": max(1, len(chunk_content.split())),
                        "chu_de": chu_de,
                        "muc_do_lien_quan_dau": muc_do_lien_quan,
                    })
                    chunk_index += 1

            current_dieu_num = int(dieu_m.group(2))
            current_dieu_title = dieu_m.group(1)
            current_chunk_lines = [line_str]
            current_page_start = page_num
        else:
            current_chunk_lines.append(line_str)

    if current_chunk_lines:
        chunk_content = normalize_nfc("\n".join(current_chunk_lines))
        if len(chunk_content) > 20:
            chunks.append({
                "chunk_id": f"{doc_id}_D{current_dieu_num or chunk_index}",
                "doc_id": doc_id,
                "so_hieu": so_hieu,
                "dieu_so": current_dieu_num or chunk_index,
                "khoan_so": 1,
                "so_trang": current_page_start,
                "title": current_dieu_title or f"Điều {current_dieu_num or chunk_index}",
                "content": chunk_content,
                "token_count": max(1, len(chunk_content.split())),
                "chu_de": chu_de,
                "muc_do_lien_quan_dau": muc_do_lien_quan,
            })

    return chunks, relations


def process_pdf_file(file_path: Path, folder_type: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Xử lý 1 file PDF: trích xuất text, metadata, chunks và relations."""
    doc = fitz.open(file_path)
    pages_text = []
    full_text_list = []

    for page_num, page in enumerate(doc, 1):
        raw_page_text = page.get_text("text")
        cleaned_text = clean_page_text(raw_page_text)
        pages_text.append((page_num, cleaned_text))
        full_text_list.append(cleaned_text)

    full_text = normalize_nfc("\n".join(full_text_list))
    doc_meta = extract_metadata_from_text(file_path, full_text, folder_type)
    chunks, relations = chunk_document_by_dieu(pages_text, doc_meta)

    return doc_meta, chunks, relations


def main():
    parser = argparse.ArgumentParser(description="Preprocess PDF documents into structured JSONL format.")
    parser.add_argument("--input_dir", type=str, default="data/raw", help="Input raw data directory")
    parser.add_argument("--output_dir", type=str, default="data/processed", help="Output processed directory")
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    all_docs = []
    all_chunks = []
    all_relations = []

    pdf_files = list(input_path.rglob("*.pdf"))
    print(f"🚀 Bắt đầu xử lý {len(pdf_files)} file PDF từ {input_path}...")

    for pdf_file in pdf_files:
        folder_type = pdf_file.parent.name
        try:
            doc_meta, chunks, relations = process_pdf_file(pdf_file, folder_type)
            all_docs.append(doc_meta)
            all_chunks.extend(chunks)
            all_relations.extend(relations)
            print(f"  ✅ Đã xử lý [{pdf_file.name}]: {len(chunks)} chunks, {len(relations)} quan hệ.")
        except Exception as e:
            print(f"  ❌ Lỗi khi xử lý file [{pdf_file.name}]: {e}")

    docs_file = output_path / "documents.jsonl"
    with open(docs_file, "w", encoding="utf-8") as f:
        for doc_item in all_docs:
            f.write(json.dumps(doc_item, ensure_ascii=False) + "\n")

    chunks_file = output_path / "chunks.jsonl"
    with open(chunks_file, "w", encoding="utf-8") as f:
        for chunk_item in all_chunks:
            f.write(json.dumps(chunk_item, ensure_ascii=False) + "\n")

    relations_file = output_path / "document_relations.jsonl"
    with open(relations_file, "w", encoding="utf-8") as f:
        for rel_item in all_relations:
            f.write(json.dumps(rel_item, ensure_ascii=False) + "\n")

    print("\n🎉 HOÀN THÀNH BƯỚC 3 PREPROCESSING & CHUNKING!")
    print(f"📊 Tổng số Văn bản: {len(all_docs)} -> {docs_file}")
    print(f"📊 Tổng số Chunks: {len(all_chunks)} -> {chunks_file}")
    print(f"📊 Tổng số Quan hệ: {len(all_relations)} -> {relations_file}")


if __name__ == "__main__":
    main()
