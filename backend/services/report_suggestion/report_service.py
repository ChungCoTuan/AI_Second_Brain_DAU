import io
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from docx import Document as DocxDocument
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from backend.db.models import Document, DocumentChunk, ReportTemplate

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATES = {
    "TUYEN_SINH": [
        "I. Căn cứ pháp lý áp dụng",
        "II. Tình hình triển khai công tác tuyển sinh",
        "III. Quy trình tiếp nhận & Xét tuyển hồ sơ",
        "IV. Số liệu thống kê nguyện vọng & Nhập học (Để trống)",
        "V. Kết luận & Đề xuất phương án"
    ],
    "DAO_TAO": [
        "I. Căn cứ pháp lý áp dụng",
        "II. Tiến độ thực hiện chương trình đào tạo & Học vụ",
        "III. Đánh giá việc tuân thủ quy chế học phần",
        "IV. Thống kê kết quả học tập & Tín chỉ (Để trống)",
        "V. Kiến nghị & Đề xuất giải pháp"
    ],
    "DEFAULT": [
        "I. Căn cứ pháp lý áp dụng",
        "II. Nội dung thực hiện theo văn bản quy định",
        "III. Kết quả & Số liệu thực tế (Để trống)",
        "IV. Kết luận & Phương hướng tiếp theo"
    ]
}

def generate_report_outline(db: Session, doc_id: str) -> Dict[str, Any]:
    """Tạo cấu trúc khung báo cáo gợi ý (UC-05) chuẩn văn bản hành chính Việt Nam (Nghị định 30/2020):
    - Có Quốc hiệu, Tiêu ngữ, Tên Đơn vị/Trường DAU.
    - Tiêu đề Báo cáo / Tờ trình kèm V/v trích yếu.
    - Kính gửi Ban Giám hiệu / Thủ trưởng đơn vị.
    - Khớp template theo loai_van_ban + chu_de trong DB.
    - Căn cứ pháp lý: Tự động điền trích dẫn.
    - Số liệu & Kết luận: ĐỂ TRỐNG (ràng buộc an toàn tuyệt đối chống bịa số liệu).
    - Khối Nơi nhận & Chữ ký người báo cáo ở cuối đơn.
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise ValueError(f"Không tìm thấy văn bản với ID={doc_id}")

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == doc_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    # 1. Look up ReportTemplate in DB
    template = (
        db.query(ReportTemplate)
        .filter(ReportTemplate.chu_de_ap_dung == doc.chu_de)
        .first()
    )

    template_used_name = "Thư viện Template Mặc định"
    section_titles: List[str] = []

    if template and template.danh_sach_de_muc and "sections" in template.danh_sach_de_muc:
        section_titles = template.danh_sach_de_muc["sections"]
        template_used_name = f"Template {doc.chu_de} (DB)"
    elif doc.chu_de in DEFAULT_TEMPLATES:
        section_titles = DEFAULT_TEMPLATES[doc.chu_de]
        template_used_name = f"Template {doc.chu_de} (Cố định)"
    else:
        # Fallback: Extract headings directly from DocumentChunks
        template_used_name = "Tự dựng khung từ Đề mục Văn bản gốc"
        section_titles = ["I. Căn cứ pháp lý áp dụng"]
        seen_headings = set()
        for c in chunks[:5]:
            heading = c.dieu_khoan or "Nội dung quy định"
            if heading not in seen_headings:
                seen_headings.add(heading)
                section_titles.append(f"II.{len(seen_headings)}. Triển khai {heading}")
        section_titles.extend([
            "III. Số liệu & Thống kê thực tế (Để trống)",
            "IV. Kết luận & Đề xuất phương án"
        ])

    # 2. Build structured outline sections
    legal_date_str = doc.ngay_ban_hanh.strftime("%d/%m/%Y") if doc.ngay_ban_hanh else "hiện hành"
    legal_content = (
        f"- Căn cứ văn bản {doc.ten_van_ban} (Số hiệu: {doc.so_hieu or 'N/A'}), "
        f"ban hành ngày {legal_date_str} bởi {doc.co_quan_ban_hanh or 'Trường ĐH Kiến trúc Đà Nẵng'}.\n"
        f"- Căn cứ các quy chế và văn bản chỉ đạo hiện hành của Trường Đại học Kiến trúc Đà Nẵng.\n"
        f"- Nguồn lưu trữ trích dẫn: {doc.file_goc_url or 'Cơ sở dữ liệu DAU Second Brain'}."
    )

    sections = []
    for idx, title in enumerate(section_titles, 1):
        if "Căn cứ" in title:
            sections.append({
                "heading": title,
                "content": legal_content,
                "is_blank": False,
                "type": "legal_base"
            })
        elif "Số liệu" in title or "Thống kê" in title:
            sections.append({
                "heading": title,
                "content": "[Để trống cho giảng viên / cán bộ tự điền số liệu thực tế - TUYỆT ĐỐI không tự bịa số liệu]\n...........................................................................................................................................\n...........................................................................................................................................",
                "is_blank": True,
                "type": "metrics_blank"
            })
        elif "Kết luận" in title or "Kiến nghị" in title or "Phương hướng" in title:
            sections.append({
                "heading": title,
                "content": "[Để trống cho giảng viên / cán bộ tự nhập kết luận & đề xuất giải pháp]\n...........................................................................................................................................\n...........................................................................................................................................",
                "is_blank": True,
                "type": "conclusion_blank"
            })
        else:
            sample_chunks_text = "\n".join([f"• Theo {c.dieu_khoan}: {c.noi_dung[:120]}..." for c in chunks[:2]])
            sections.append({
                "heading": title,
                "content": f"Gợi ý nội dung triển khai theo các điều khoản gốc:\n{sample_chunks_text}",
                "is_blank": False,
                "type": "content_body"
            })

    return {
        "doc_id": doc.id,
        "quoc_hieu": "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
        "tieu_ngu": "Độc lập - Tự do - Hạnh phúc",
        "co_quan_ban_hanh_tren": "TRƯỜNG ĐẠI HỌC KIẾN TRÚC ĐÀ NẴNG (DAU)",
        "don_vi_bao_cao": "ĐƠN VỊ / KHOA / PHÒNG: [........................................]",
        "so_ky_hieu": f"Số: ...../BC-DAU",
        "dia_danh_ngay_thang": "Đà Nẵng, ngày ... tháng ... năm 20...",
        "ten_van_ban": doc.ten_van_ban,
        "so_hieu": doc.so_hieu or "",
        "loai_van_ban": doc.loai_van_ban or "Quy định",
        "chu_de": doc.chu_de or "KHAC",
        "ten_don_bao_cao": f"BÁO CÁO THỰC HIỆN",
        "trich_yeu": f"V/v Triển khai & Thực hiện {doc.ten_van_ban}",
        "kinh_gui": "Kính gửi: Ban Giám hiệu Trường Đại học Kiến trúc Đà Nẵng / Trưởng đơn vị",
        "template_used": template_used_name,
        "sections": sections,
        "noi_nhan": ["- Như trên;", "- Lưu: VT, Đơn vị."],
        "nguoi_ky_chuc_danh": "NGƯỜI LÀM BÁO CÁO / THỦ TRƯỞNG ĐƠN VỊ",
        "nguoi_ky_chu_ky": "(Ký và ghi rõ họ tên)"
    }


def build_report_docx_stream(db: Session, doc_id: str) -> bytes:
    """Sinh file Word (.docx) chuẩn định dạng văn bản hành chính Việt Nam (Nghị định 30/2020/NĐ-CP)."""
    outline = generate_report_outline(db, doc_id)

    doc = DocxDocument()

    # Document Page Margins (Standard A4 Margins: Top 2cm, Bottom 2cm, Left 3cm, Right 2cm)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.79)

    # 1. HEADER TABLE (2 Columns: Left = Organ, Right = National Motto)
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False

    # Left Cell
    cell_left = header_table.cell(0, 0)
    cell_left.width = Inches(3.2)
    p_left1 = cell_left.paragraphs[0]
    p_left1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_left1.add_run(outline["co_quan_ban_hanh_tren"] + "\n")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(10)
    r1.font.bold = True
    
    r2 = p_left1.add_run(outline["don_vi_bao_cao"] + "\n")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(10)

    r3 = p_left1.add_run(outline["so_ky_hieu"])
    r3.font.name = "Times New Roman"
    r3.font.size = Pt(10)

    # Right Cell
    cell_right = header_table.cell(0, 1)
    cell_right.width = Inches(3.5)
    p_right1 = cell_right.paragraphs[0]
    p_right1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    r_qh = p_right1.add_run(outline["quoc_hieu"] + "\n")
    r_qh.font.name = "Times New Roman"
    r_qh.font.size = Pt(10.5)
    r_qh.font.bold = True

    r_tn = p_right1.add_run(outline["tieu_ngu"] + "\n")
    r_tn.font.name = "Times New Roman"
    r_tn.font.size = Pt(11)
    r_tn.font.bold = True

    r_line = p_right1.add_run("-----------------------\n")
    r_line.font.name = "Times New Roman"
    r_line.font.size = Pt(9)
    r_line.font.bold = True

    r_dt = p_right1.add_run(outline["dia_danh_ngay_thang"])
    r_dt.font.name = "Times New Roman"
    r_dt.font.size = Pt(10)
    r_dt.font.italic = True

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 2. DOCUMENT TITLE
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = p_title.add_run(outline["ten_don_bao_cao"] + "\n")
    run_t.font.name = "Times New Roman"
    run_t.font.size = Pt(15)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(15, 23, 42)

    run_sub = p_title.add_run(outline["trich_yeu"])
    run_sub.font.name = "Times New Roman"
    run_sub.font.size = Pt(12)
    run_sub.font.bold = True
    run_sub.font.italic = True

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 3. KÍNH GỬI
    p_kg = doc.add_paragraph()
    p_kg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_kg = p_kg.add_run(outline["kinh_gui"])
    run_kg.font.name = "Times New Roman"
    run_kg.font.size = Pt(12)
    run_kg.font.bold = True
    run_kg.font.italic = True

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 4. REPORT SECTIONS
    for sec in outline["sections"]:
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(4)
        h_run = h.add_run(sec["heading"])
        h_run.font.name = "Times New Roman"
        h_run.font.size = Pt(12.5)
        h_run.font.bold = True
        h_run.font.color.rgb = RGBColor(15, 23, 42)

        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.2
        p_run = p.add_run(sec["content"])
        p_run.font.name = "Times New Roman"
        p_run.font.size = Pt(12)

        if sec["is_blank"]:
            p_run.font.italic = True
            p_run.font.color.rgb = RGBColor(180, 83, 9)  # Warning amber font for blank placeholder
        else:
            p_run.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(18)

    # 5. FOOTER TABLE (Nơi nhận & Chữ ký)
    footer_table = doc.add_table(rows=1, cols=2)
    footer_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    footer_table.autofit = False

    # Left: Nơi nhận
    cell_nn = footer_table.cell(0, 0)
    cell_nn.width = Inches(3.2)
    p_nn = cell_nn.paragraphs[0]
    r_nn1 = p_nn.add_run("Nơi nhận:\n")
    r_nn1.font.name = "Times New Roman"
    r_nn1.font.size = Pt(10)
    r_nn1.font.bold = True
    r_nn1.font.italic = True

    for item in outline["noi_nhan"]:
        r_item = p_nn.add_run(f"{item}\n")
        r_item.font.name = "Times New Roman"
        r_item.font.size = Pt(9.5)
        r_item.font.italic = True

    # Right: Chữ ký
    cell_sig = footer_table.cell(0, 1)
    cell_sig.width = Inches(3.5)
    p_sig = cell_sig.paragraphs[0]
    p_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    r_sig1 = p_sig.add_run(outline["nguoi_ky_chuc_danh"] + "\n")
    r_sig1.font.name = "Times New Roman"
    r_sig1.font.size = Pt(11)
    r_sig1.font.bold = True

    r_sig2 = p_sig.add_run(outline["nguoi_ky_chu_ky"] + "\n\n\n\n")
    r_sig2.font.name = "Times New Roman"
    r_sig2.font.size = Pt(10)
    r_sig2.font.italic = True

    r_sig3 = p_sig.add_run("........................................................")
    r_sig3.font.name = "Times New Roman"
    r_sig3.font.size = Pt(10)

    # Save to memory bytes stream
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream.getvalue()
