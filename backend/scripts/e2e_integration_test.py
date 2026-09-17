import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Cấu hình path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from api.main import app

client = TestClient(app)

def run_e2e_test():
    print("🚀 Bắt đầu Integration Test End-to-End cho DAU Second Brain\n")
    
    # 1. Tạo 1 file PDF giả lập
    test_pdf_path = BACKEND_DIR / "test_dummy.pdf"
    print(f"👉 Bước 1: Tạo file PDF giả lập tại {test_pdf_path}")
    try:
        import fitz  # PyMuPDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Quyết định số 999/QĐ-ĐHKTĐN. \nĐiều 1. Sinh viên đi học đúng giờ. \nCăn cứ Luật số 123.", fontsize=12)
        doc.save(test_pdf_path)
    except ImportError:
        print("❌ Chưa cài đặt PyMuPDF (fitz). Bỏ qua việc tạo file thật.")
        with open(test_pdf_path, "wb") as f:
            f.write(b"%PDF-1.4 dummy file")
            
    # 2. Gọi API Upload (UC-01 & UC-02)
    print("\n👉 Bước 2: Gọi API Upload (/api/documents/upload) ...")
    try:
        with open(test_pdf_path, "rb") as f:
            response = client.post(
                "/api/documents/upload",
                files={"file": ("test_dummy.pdf", f, "application/pdf")},
                data={"chu_de": "DAO_TAO"}
            )
        if response.status_code == 200:
            res_data = response.json()
            doc_id = res_data.get("doc_id")
            print(f"✅ Upload thành công! Doc ID: {doc_id}")
            print(f"   - Số chunks tạo ra: {res_data.get('total_chunks')}")
            print(f"   - Trạng thái: {res_data.get('trang_thai_xuat_ban')}")
        else:
            print(f"❌ Upload lỗi: {response.text}")
            return
    except Exception as e:
        print(f"⚠️ Lỗi kết nối Upload: {e}")
        return

    # 3. Gọi API Review Queue (UC-04)
    print("\n👉 Bước 3: Kiểm tra hàng đợi duyệt (/api/review/queue) ...")
    try:
        res = client.get("/api/review/queue?status=pending")
        if res.status_code == 200:
            queue_data = res.json()
            items = queue_data.get("items", [])
            print(f"✅ Hàng đợi duyệt hiện có: {len(items)} câu cần rà soát.")
        else:
            print(f"❌ Lỗi lấy hàng đợi: {res.text}")
    except Exception as e:
        print(f"⚠️ Lỗi kết nối Review Queue: {e}")

    # 4. Kiểm tra Chi tiết văn bản
    print("\n👉 Bước 4: Kiểm tra chi tiết văn bản ...")
    try:
        res = client.get(f"/api/documents/{doc_id}")
        if res.status_code == 200:
            doc_data = res.json()
            print(f"✅ Lấy chi tiết văn bản thành công. Tổng số chunks trong hệ thống: {doc_data.get('total_chunks')}")
        else:
            print(f"❌ Lỗi lấy chi tiết: {res.text}")
    except Exception as e:
        print(f"⚠️ Lỗi lấy chi tiết: {e}")

    # Dọn dẹp
    if test_pdf_path.exists():
        os.remove(test_pdf_path)

    print("\n🎉 HOÀN TẤT E2E INTEGRATION TEST (CƠ BẢN)")
    print("Để kiểm tra chính xác, vui lòng chạy UI, tải 1 file PDF thực tế và xem kết quả trên màn hình.")

if __name__ == "__main__":
    run_e2e_test()
