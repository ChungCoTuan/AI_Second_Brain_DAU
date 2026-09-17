"""Report Suggestion Service — DAU Second Brain (SVC-04, WF-04, EPIC-4).

Sinh khung báo cáo theo từng loại văn bản pháp quy.
Mỗi văn bản có template riêng (không dùng khung chung).
Tuyệt đối KHÔNG tự sinh nội dung/số liệu báo cáo — chỉ gợi ý CẤU TRÚC.

Chiến lược:
  1. Tra cứu ReportTemplate khớp với (loai_bao_cao, chu_de)
  2. Nếu không tìm thấy template → tự dựng từ nội dung văn bản gốc
  3. Điền "Căn cứ pháp lý" từ trích dẫn văn bản gốc
  4. Xuất JSON outline (đề mục) cho frontend render

Cách dùng:
  from services.report_suggestion.report_chain import suggest_report
  result = suggest_report(doc_metadata, chunks)
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

logger = logging.getLogger(__name__)


# ─── Thư viện Template mặc định (theo loại báo cáo) ─────────────────────────
# Mở rộng thêm template vào đây khi có thêm loại văn bản

TEMPLATE_LIBRARY: list[dict] = [
    {
        "template_id": "TPL-001",
        "loai_bao_cao": "Báo cáo định kỳ",
        "chu_de_ap_dung": ["DAO_TAO", "KHAC"],
        "de_muc": [
            "I. Căn cứ pháp lý",
            "II. Thực trạng và kết quả thực hiện",
            "  1. Tình hình chung",
            "  2. Kết quả cụ thể theo từng chỉ tiêu",
            "  3. Những hạn chế, khó khăn",
            "III. Đánh giá, nhận xét",
            "IV. Phương hướng, nhiệm vụ kỳ tiếp theo",
            "V. Kiến nghị, đề xuất",
        ],
        "ghi_chu": "Dùng cho báo cáo định kỳ theo thông tư/quyết định của Bộ GD&ĐT.",
    },
    {
        "template_id": "TPL-002",
        "loai_bao_cao": "Báo cáo tổng kết năm học",
        "chu_de_ap_dung": ["DAO_TAO"],
        "de_muc": [
            "I. Căn cứ pháp lý",
            "II. Tổng quan tình hình năm học [Năm]",
            "  1. Quy mô đào tạo",
            "  2. Chất lượng đào tạo",
            "  3. Hoạt động nghiên cứu khoa học",
            "  4. Công tác tuyển sinh",
            "III. Đánh giá kết quả thực hiện các chỉ tiêu",
            "IV. Phương hướng năm học [Năm+1]",
            "V. Phụ lục số liệu",
        ],
        "ghi_chu": "Template cho báo cáo tổng kết năm học, thay [Năm] bằng năm học cụ thể.",
    },
    {
        "template_id": "TPL-003",
        "loai_bao_cao": "Báo cáo tự đánh giá kiểm định",
        "chu_de_ap_dung": ["DAO_TAO"],
        "de_muc": [
            "I. Căn cứ pháp lý và mục tiêu tự đánh giá",
            "II. Tổng quan về cơ sở đào tạo",
            "III. Tự đánh giá theo từng tiêu chuẩn/tiêu chí",
            "  Tiêu chuẩn 1: Mục tiêu và chuẩn đầu ra",
            "  Tiêu chuẩn 2: Chương trình đào tạo",
            "  Tiêu chuẩn 3: Đội ngũ giảng viên",
            "  Tiêu chuẩn 4: Cơ sở vật chất",
            "IV. Kế hoạch cải tiến chất lượng",
            "V. Kết luận và cam kết",
        ],
        "ghi_chu": "Dùng cho báo cáo tự đánh giá kiểm định chất lượng theo Thông tư 12.",
    },
    {
        "template_id": "TPL-004",
        "loai_bao_cao": "Báo cáo tuyển sinh",
        "chu_de_ap_dung": ["TUYEN_SINH"],
        "de_muc": [
            "I. Căn cứ pháp lý",
            "II. Chỉ tiêu tuyển sinh được giao",
            "III. Kết quả tuyển sinh thực tế",
            "  1. Số lượng thí sinh đăng ký",
            "  2. Kết quả xét tuyển theo phương thức",
            "  3. Tỷ lệ nhập học",
            "IV. Đánh giá và điều chỉnh",
            "V. Phụ lục thống kê chi tiết",
        ],
        "ghi_chu": "Dùng cho báo cáo tuyển sinh theo Thông tư 03/2022.",
    },
    {
        "template_id": "TPL-005",
        "loai_bao_cao": "Báo cáo tài chính - học phí",
        "chu_de_ap_dung": ["TAI_CHINH"],
        "de_muc": [
            "I. Căn cứ pháp lý",
            "II. Tình hình thu học phí và các khoản thu hợp pháp",
            "III. Tình hình sử dụng nguồn thu",
            "IV. Chính sách miễn giảm học phí đã thực hiện",
            "V. Kiến nghị và đề xuất",
        ],
        "ghi_chu": "Dùng cho báo cáo liên quan đến học phí và tài chính.",
    },
]


# ─── Template Matcher ─────────────────────────────────────────────────────────

def find_template(loai_bao_cao: str, chu_de: str) -> Optional[dict]:
    """
    Tìm template phù hợp nhất với loại báo cáo và chủ đề.
    Returns None nếu không tìm thấy.
    """
    # Tìm exact match trước
    for tpl in TEMPLATE_LIBRARY:
        name_match = (
            loai_bao_cao.lower() in tpl["loai_bao_cao"].lower()
            or tpl["loai_bao_cao"].lower() in loai_bao_cao.lower()
        )
        topic_match = chu_de in tpl.get("chu_de_ap_dung", [])

        if name_match and topic_match:
            return tpl

    # Tìm chỉ theo chủ đề nếu không có exact match
    for tpl in TEMPLATE_LIBRARY:
        if chu_de in tpl.get("chu_de_ap_dung", []):
            return tpl

    return None


# ─── Content Extractor (từ văn bản gốc) ──────────────────────────────────────

def extract_report_requirements(chunks: list[dict]) -> dict:
    """
    Trích xuất yêu cầu báo cáo từ nội dung văn bản.
    Tìm kiếm các đề mục/mục yêu cầu liệt kê trong văn bản.
    """
    requirements = {
        "yeu_cau_bao_cao": [],
        "han_nop": None,
        "don_vi_chiu_trach_nhiem": None,
        "loai_bao_cao_goi_y": "Báo cáo định kỳ",
        "de_muc_tu_van_ban": [],
    }

    bao_cao_pattern = re.compile(
        r"(báo cáo|tổng kết|thống kê)[^.]{5,100}", re.IGNORECASE
    )
    han_nop_pattern = re.compile(
        r"(trước ngày|hạn nộp|chậm nhất)[^.]{5,80}", re.IGNORECASE
    )
    muc_pattern = re.compile(
        r"^[a-z\d]\)|^\d+\.\s|^-\s|^[IVXLC]+\.\s",
        re.MULTILINE | re.IGNORECASE,
    )

    for chunk in chunks:
        content = chunk.get("content", "")

        # Tìm yêu cầu báo cáo
        matches = bao_cao_pattern.findall(content)
        requirements["yeu_cau_bao_cao"].extend(matches[:3])

        # Tìm hạn nộp
        han_match = han_nop_pattern.search(content)
        if han_match and not requirements["han_nop"]:
            requirements["han_nop"] = han_match.group(0).strip()

        # Tìm đề mục liệt kê trong văn bản
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if muc_pattern.match(line) and len(line) > 10:
                requirements["de_muc_tu_van_ban"].append(line)

    # Phân loại loại báo cáo
    all_text = " ".join(
        chunk.get("content", "") for chunk in chunks
    ).lower()
    if "tổng kết" in all_text:
        requirements["loai_bao_cao_goi_y"] = "Báo cáo tổng kết năm học"
    elif "tuyển sinh" in all_text:
        requirements["loai_bao_cao_goi_y"] = "Báo cáo tuyển sinh"
    elif "kiểm định" in all_text or "tự đánh giá" in all_text:
        requirements["loai_bao_cao_goi_y"] = "Báo cáo tự đánh giá kiểm định"
    elif "học phí" in all_text or "tài chính" in all_text:
        requirements["loai_bao_cao_goi_y"] = "Báo cáo tài chính - học phí"

    return requirements


# ─── Report Suggestion Chain (LangChain Prompt) ──────────────────────────────

def suggest_report(
    doc_metadata: dict,
    chunks: list[dict],
) -> dict:
    """
    Sinh gợi ý khung báo cáo cho 1 văn bản (WF-04).

    Args:
        doc_metadata: dict từ documents.jsonl
        chunks: list[dict] các chunk thuộc văn bản này

    Returns:
        dict với template_id, loai_bao_cao, de_muc, can_cu_phap_ly, ghi_chu
    """
    doc_id = doc_metadata.get("doc_id", "")
    so_hieu = doc_metadata.get("so_hieu", "")
    ten_van_ban = doc_metadata.get("ten_van_ban", "")
    chu_de = doc_metadata.get("chu_de", "KHAC")
    loai_van_ban = doc_metadata.get("loai_van_ban", "Văn bản")
    can_cu_list = doc_metadata.get("can_cu_dan_chieu", [])

    # ── 1. Trích xuất yêu cầu báo cáo từ nội dung ─────────────────────────
    req = extract_report_requirements(chunks)
    loai_bao_cao = req.get("loai_bao_cao_goi_y", "Báo cáo định kỳ")

    # ── 2. Tìm template ───────────────────────────────────────────────────
    template = find_template(loai_bao_cao=loai_bao_cao, chu_de=chu_de)

    if template:
        de_muc = template["de_muc"].copy()
        source = "template_library"
        template_id = template["template_id"]
        ghi_chu = template.get("ghi_chu", "")
    else:
        # Fallback: dựng từ đề mục trích xuất trong văn bản gốc
        de_muc_raw = req.get("de_muc_tu_van_ban", [])

        if de_muc_raw:
            de_muc = ["I. Căn cứ pháp lý"] + de_muc_raw[:8]
            source = "extracted_from_document"
        else:
            # Default minimal
            de_muc = [
                "I. Căn cứ pháp lý",
                "II. Nội dung báo cáo",
                "  1. Tình hình thực hiện",
                "  2. Kết quả đạt được",
                "  3. Khó khăn, vướng mắc",
                "III. Kiến nghị, đề xuất",
            ]
            source = "default_minimal"

        template_id = None
        ghi_chu = (
            f"Khung báo cáo được tự động dựng từ nội dung {loai_van_ban} {so_hieu}. "
            "Vui lòng điều chỉnh đề mục cho phù hợp."
        )

    # ── 3. Điền căn cứ pháp lý (từ trích dẫn văn bản gốc) ────────────────
    can_cu_phap_ly = [f"Căn cứ {loai_van_ban} số {so_hieu} ({ten_van_ban})"]
    for cc in can_cu_list[:3]:
        if len(cc) > 10:
            can_cu_phap_ly.append(f"Căn cứ {cc}")

    # ── 4. Thông tin bổ sung ───────────────────────────────────────────────
    return {
        "doc_id": doc_id,
        "template_id": template_id,
        "loai_bao_cao": loai_bao_cao,
        "chu_de": chu_de,
        "de_muc": de_muc,
        "can_cu_phap_ly": can_cu_phap_ly,
        "ghi_chu": ghi_chu,
        "han_nop": req.get("han_nop"),
        "yeu_cau_tom_tat": req.get("yeu_cau_bao_cao", [])[:3],
        "source": source,
        "canh_bao": (
            "⚠️ Hệ thống CHỈ gợi ý CẤU TRÚC ĐỀ MỤC. "
            "Không tự sinh số liệu hay nội dung báo cáo thực tế."
        ),
    }


# ─── LangChain Prompt (dùng khi có LLM) ──────────────────────────────────────

def get_report_chain_with_llm(llm):
    """
    Tạo LangChain chain sinh khung báo cáo nâng cao khi có LLM.
    Dùng JsonOutputParser để đảm bảo output có cấu trúc.

    Args:
        llm: LangChain LLM instance

    Returns:
        chain có thể invoke với dict đầu vào
    """
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser

    prompt = ChatPromptTemplate.from_template("""
Bạn là chuyên gia hành chính giáo dục, hỗ trợ soạn thảo khung báo cáo cho Trường ĐH Kiến trúc Đà Nẵng.

NGUYÊN TẮC BẮT BUỘC:
1. Chỉ đề xuất CẤU TRÚC ĐỀ MỤC, TUYỆT ĐỐI không tự sinh số liệu hay nội dung thực tế.
2. Căn cứ pháp lý phải trích dẫn đúng từ văn bản gốc cung cấp.
3. Đề mục phải phù hợp với loại văn bản (không dùng template chung).

Thông tin văn bản:
- Loại văn bản: {loai_van_ban}
- Số hiệu: {so_hieu}
- Chủ đề: {chu_de}  
- Loại báo cáo yêu cầu: {loai_bao_cao}
- Yêu cầu cụ thể từ văn bản: {yeu_cau_bao_cao}
- Hạn nộp: {han_nop}

Trả về JSON (không có markdown):
{{
  "loai_bao_cao": "...",
  "de_muc": ["I. ...", "II. ...", "  1. ...", ...],
  "can_cu_phap_ly": ["Căn cứ {so_hieu}...", ...],
  "ghi_chu": "...",
  "canh_bao": "Hệ thống chỉ gợi ý cấu trúc, không tự sinh nội dung thực tế."
}}
""")

    parser = JsonOutputParser()
    return prompt | llm | parser


# ─── CLI Test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🧪 Test Report Suggestion Service...")

    sample_doc = {
        "doc_id": "BGD_TT_012024",
        "so_hieu": "01/2024/TT-BGDĐT",
        "ten_van_ban": "Thông tư 01/2024/TT-BGDĐT: Chuẩn cơ sở giáo dục đại học",
        "loai_van_ban": "Thông tư",
        "chu_de": "DAO_TAO",
        "can_cu_dan_chieu": [
            "Luật Giáo dục đại học số 08/2012/QH13",
            "Nghị định số 99/2019/NĐ-CP",
        ],
    }

    sample_chunks = [
        {
            "chunk_id": "BGD_TT_012024_D3",
            "content": (
                "Điều 3. Trách nhiệm của cơ sở giáo dục đại học. "
                "Báo cáo định kỳ hằng năm trước ngày 31 tháng 10 về tình hình "
                "thực hiện chuẩn cơ sở giáo dục đại học. "
                "Tổng kết, đánh giá việc thực hiện các tiêu chuẩn, tiêu chí."
            ),
        }
    ]

    result = suggest_report(doc_metadata=sample_doc, chunks=sample_chunks)

    print(f"\n📋 Loại báo cáo: {result['loai_bao_cao']}")
    print(f"📌 Template: {result.get('template_id', 'Tự dựng từ văn bản')}")
    print(f"🏗️ Đề mục khung báo cáo:")
    for dm in result["de_muc"]:
        print(f"   {dm}")
    print(f"\n⚖️ Căn cứ pháp lý:")
    for cc in result["can_cu_phap_ly"]:
        print(f"   - {cc}")
    print(f"\n⚠️ {result['canh_bao']}")
