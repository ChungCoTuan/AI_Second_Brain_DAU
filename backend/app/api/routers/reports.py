from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...db.models import Document
import os
from docx import Document as DocxDocument
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

router = APIRouter()

@router.get("/template/{document_id}")
async def download_report_template(document_id: str, db: Session = Depends(get_db)):
    # 1. Tìm văn bản trong DB
    doc = db.query(Document).filter(
        (Document.filename == document_id) | (Document.filename == f"{document_id}.pdf")
    ).first()
    
    # Nếu không tìm thấy bằng filename, thử tìm bằng ID (nếu truyền số)
    if not doc and document_id.isdigit():
        doc = db.query(Document).filter(Document.id == int(document_id)).first()
        
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy văn bản")
        
    # 2. Tạo file Word chuyên nghiệp với python-docx
    document = DocxDocument()
    
    # Header: Quốc hiệu, Tiêu ngữ
    header_table = document.add_table(rows=1, cols=2)
    header_table.allow_autofit = True
    
    cell_1 = header_table.cell(0, 0)
    p1 = cell_1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run1 = p1.add_run("TÊN CƠ QUAN CHỦ QUẢN\nĐƠN VỊ THỰC HIỆN")
    run1.bold = True
    run1.font.name = 'Times New Roman'
    run1.font.size = Pt(13)
    p1.add_run("\n-------\nSố: ..... /BC-..................").font.name = 'Times New Roman'
    
    cell_2 = header_table.cell(0, 1)
    p2 = cell_2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = p2.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc")
    run2.bold = True
    run2.font.name = 'Times New Roman'
    run2.font.size = Pt(13)
    p2.add_run("\n-----------------------\nĐà Nẵng, ngày .... tháng .... năm 20...").font.name = 'Times New Roman'
    
    document.add_paragraph("\n")
    
    # Nhận diện loại văn bản từ filename
    filename_upper = doc.filename.upper()
    doc_type = "DEFAULT"
    
    # Sử dụng split theo dấu gạch dưới "_" hoặc khoảng trắng để tránh nhận diện nhầm (VD: chuỗi "QĐ" trong chữ khác)
    # Tuy nhiên, để linh hoạt, ta vẫn check chuỗi nhưng ưu tiên những từ phổ biến.
    if "_QD" in filename_upper or "_QĐ" in filename_upper or "QĐ" in filename_upper or "QUYET DINH" in filename_upper or "QUYẾT ĐỊNH" in filename_upper:
        doc_type = "QD"
    elif "_TB" in filename_upper or "THONG BAO" in filename_upper or "THÔNG BÁO" in filename_upper:
        doc_type = "TB"
    elif "_TT" in filename_upper or "THONG TU" in filename_upper or "THÔNG TƯ" in filename_upper or "_ND" in filename_upper or "_NĐ" in filename_upper or "NGHI DINH" in filename_upper or "NGHỊ ĐỊNH" in filename_upper:
        doc_type = "TT_ND"
    elif "_KH" in filename_upper or "KE HOACH" in filename_upper or "KẾ HOẠCH" in filename_upper or "_HD" in filename_upper or "HUONG DAN" in filename_upper or "HƯỚNG DẪN" in filename_upper:
        doc_type = "KH_HD"
    elif "_CT" in filename_upper or "CHI THI" in filename_upper or "CHỈ THỊ" in filename_upper:
        doc_type = "CT"
    elif "_CV" in filename_upper or "CONG VAN" in filename_upper or "CÔNG VĂN" in filename_upper:
        doc_type = "CV"
    elif "_NQ" in filename_upper or "NGHI QUYET" in filename_upper or "NGHỊ QUYẾT" in filename_upper:
        doc_type = "NQ"
        
    # Title
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run("BÁO CÁO\nKết quả thực hiện nhiệm vụ/nghĩa vụ\n")
    title_run.bold = True
    title_run.font.name = 'Times New Roman'
    title_run.font.size = Pt(14)
    
    # Custom font styles for normal paragraphs
    style = document.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(13)
    
    # Content sections
    h1 = document.add_paragraph()
    h1_run = h1.add_run('I. CĂN CỨ PHÁP LÝ')
    h1_run.bold = True
    document.add_paragraph(f"- Căn cứ theo văn bản: {doc.filename}.")
    
    if doc_type == "QD":
        h2 = document.add_paragraph()
        h2_run = h2.add_run('II. ĐÁNH GIÁ MỨC ĐỘ ẢNH HƯỞNG VÀ NHỮNG THAY ĐỔI QUAN TRỌNG')
        h2_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h3 = document.add_paragraph()
        h3_run = h3.add_run('III. TÌNH HÌNH TRIỂN KHAI VÀ THỰC HIỆN NGHĨA VỤ')
        h3_run.bold = True
        document.add_paragraph("1. Tên nhiệm vụ/nghĩa vụ: ....................................................................................")
        document.add_paragraph("   - Kết quả đạt được: .........................................................................................")
        
        h4 = document.add_paragraph()
        h4_run = h4.add_run('IV. KHÓ KHĂN, VƯỚNG MẮC')
        h4_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h5 = document.add_paragraph()
        h5_run = h5.add_run('V. ĐỀ XUẤT VÀ KẾ HOẠCH TIẾP THEO')
        h5_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
    elif doc_type == "TB":
        h2 = document.add_paragraph()
        h2_run = h2.add_run('II. CÁC NỘI DUNG TRỌNG TÂM CẦN QUÁN TRIỆT')
        h2_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h3 = document.add_paragraph()
        h3_run = h3.add_run('III. KẾT QUẢ TIẾP THU VÀ THỰC HIỆN')
        h3_run.bold = True
        document.add_paragraph("1. Tên nhiệm vụ/yêu cầu: ....................................................................................")
        document.add_paragraph("   - Kết quả đạt được: .........................................................................................")
        document.add_paragraph("   - Khó khăn, vướng mắc: ..................................................................................")
        
        h4 = document.add_paragraph()
        h4_run = h4.add_run('IV. KẾ HOẠCH TIẾP THEO')
        h4_run.bold = True
        document.add_paragraph("........................................................................................................................")

    elif doc_type == "TT_ND":
        h2 = document.add_paragraph()
        h2_run = h2.add_run('II. ĐÁNH GIÁ SỰ TUÂN THỦ PHÁP LUẬT VÀ MỨC ĐỘ ẢNH HƯỞNG')
        h2_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h3 = document.add_paragraph()
        h3_run = h3.add_run('III. NỘI DUNG VÀ KẾT QUẢ THỰC HIỆN')
        h3_run.bold = True
        document.add_paragraph("1. Tên nhiệm vụ/nghĩa vụ: ....................................................................................")
        document.add_paragraph("   - Kết quả đạt được: .........................................................................................")
        
        h4 = document.add_paragraph()
        h4_run = h4.add_run('IV. VƯỚNG MẮC KHI ÁP DỤNG')
        h4_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h5 = document.add_paragraph()
        h5_run = h5.add_run('V. ĐỀ XUẤT, KIẾN NGHỊ')
        h5_run.bold = True
        document.add_paragraph("........................................................................................................................")

    elif doc_type == "KH_HD":
        h2 = document.add_paragraph()
        h2_run = h2.add_run('II. TÌNH HÌNH TRIỂN KHAI VÀ TIẾN ĐỘ THỰC HIỆN')
        h2_run.bold = True
        document.add_paragraph("1. Tên công việc/nhiệm vụ: ....................................................................................")
        document.add_paragraph("   - Kết quả đạt được: .........................................................................................")
        
        h3 = document.add_paragraph()
        h3_run = h3.add_run('III. MỨC ĐỘ HOÀN THÀNH CÁC GIAI ĐOẠN')
        h3_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h4 = document.add_paragraph()
        h4_run = h4.add_run('IV. KHÓ KHĂN, VƯỚNG MẮC')
        h4_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h5 = document.add_paragraph()
        h5_run = h5.add_run('V. KẾ HOẠCH TIẾP THEO')
        h5_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
    elif doc_type in ["CT", "CV", "NQ"]:
        # Chỉ thị, Công văn, Nghị quyết dùng chung một mẫu tập trung vào Quán triệt & Triển khai
        h2 = document.add_paragraph()
        h2_run = h2.add_run('II. KẾT QUẢ QUÁN TRIỆT VÀ TỔ CHỨC TRIỂN KHAI')
        h2_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h3 = document.add_paragraph()
        h3_run = h3.add_run('III. KẾT QUẢ THỰC HIỆN CỤ THỂ')
        h3_run.bold = True
        document.add_paragraph("1. Tên nhiệm vụ/yêu cầu: ....................................................................................")
        document.add_paragraph("   - Kết quả đạt được: .........................................................................................")
        
        h4 = document.add_paragraph()
        h4_run = h4.add_run('IV. KHÓ KHĂN, VƯỚNG MẮC')
        h4_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h5 = document.add_paragraph()
        h5_run = h5.add_run('V. ĐỀ XUẤT, KIẾN NGHỊ')
        h5_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
    else:
        # Default (Văn bản khác)
        h2 = document.add_paragraph()
        h2_run = h2.add_run('II. NỘI DUNG VÀ KẾT QUẢ THỰC HIỆN')
        h2_run.bold = True
        document.add_paragraph("1. Tên nhiệm vụ/nghĩa vụ: ....................................................................................")
        document.add_paragraph("   - Kết quả đạt được: .........................................................................................")
        
        h3 = document.add_paragraph()
        h3_run = h3.add_run('III. ĐÁNH GIÁ SỰ TUÂN THỦ VÀ MỨC ĐỘ ẢNH HƯỞNG')
        h3_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h4 = document.add_paragraph()
        h4_run = h4.add_run('IV. KHÓ KHĂN, VƯỚNG MẮC')
        h4_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
        h5 = document.add_paragraph()
        h5_run = h5.add_run('V. ĐỀ XUẤT, KIẾN NGHỊ')
        h5_run.bold = True
        document.add_paragraph("........................................................................................................................")
        
    document.add_paragraph("\n")
    
    # Footer Signatures
    sig_table = document.add_table(rows=1, cols=2)
    p_sig_left = sig_table.cell(0, 0).paragraphs[0]
    p_sig_left.add_run("Nơi nhận:\n").bold = True
    p_sig_left.add_run("- Như trên;\n- Lưu: VT.").italic = True
    
    p_sig_right = sig_table.cell(0, 1).paragraphs[0]
    p_sig_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sig_right.add_run("THỦ TRƯỞNG ĐƠN VỊ\n").bold = True
    p_sig_right.add_run("(Ký, ghi rõ họ tên và đóng dấu)").italic = True
    
    # Save to temp file
    os.makedirs("data/temp", exist_ok=True)
    filepath = f"data/temp/Khung_Bao_Cao_{doc.id}.docx"
    document.save(filepath)
    
    return FileResponse(filepath, filename=f"Khung_Bao_Cao_{doc.id}.docx")
