# 📂 Sơ Đồ Cấu Trúc Thư Mục — DAU Second Brain

Hệ thống **DAU Second Brain** được tổ chức theo kiến trúc Full-Stack & Micro-services chuẩn mực:

```text
DAU_SECOND_BRAIN/
├── ⚙️ backend/                      # Toàn bộ Python Backend & Core AI Pipeline
│   ├── api/                        # REST API Layer (FastAPI Server)
│   │   ├── __init__.py
│   │   └── main.py                 # Server chính: /api/query, /api/documents, /api/stats, /api/health
│   │
│   ├── services/                   # Các dịch vụ xử lý lõi (Core AI Pipeline)
│   │   ├── __init__.py
│   │   ├── ingestion/              # Cào PDF (crawl_documents.py) & Preprocessing (preprocess.py)
│   │   ├── retrieval/              # FAISS Vector Search (build_index.py) & RAG (rag_chain.py)
│   │   ├── nli/                    # NLI Checker Faithfulness (nli_checker.py)
│   │   ├── summarization/          # Tóm tắt văn bản pháp quy
│   │   ├── report_suggestion/      # Gợi ý báo cáo & vi phạm
│   │   └── document_tree/          # Cây cấu trúc văn bản
│   │
│   ├── scripts/                    # Công cụ CLI & Scripts vận hành
│   │   ├── publish_documents.py    # CLI duyệt/xuất bản văn bản (PUBLISHED/PENDING_REVIEW)
│   │   ├── convert_data_ts_to_json.py # Script chuyển đổi TS -> JSON
│   │   ├── scan_pdf_urls.py        # Script quét URL văn bản PDF
│   │   └── test_quick.py           # Benchmark & quick test
│   │
│   ├── run_pipeline.py             # Script chạy toàn bộ pipeline
│   └── requirements_langchain.txt  # Danh sách thư viện Python
│
├── 💻 frontend/                     # Ứng dụng Frontend React + Vite
│   ├── public/
│   │   └── data.json               # Dữ liệu tĩnh được lazy load (Bundle size: 286KB)
│   ├── src/
│   │   ├── components/             # UI Components (Layout, Sidebar, Drawer...)
│   │   ├── pages/                  # Pages (Search/RAG AI Assistant, Priority, Deadlines...)
│   │   ├── services/
│   │   │   └── api.ts              # Client Layer kết nối FastAPI
│   │   ├── context/
│   │   └── data.ts                 # Dynamic loader tự động fetch /data.json
│   └── package.json
│
├── 📊 data/                         # Dữ liệu hệ thống
│   ├── raw/                        # PDF gốc (quy_che_noi_bo, thong_tu, quyet_dinh)
│   ├── processed/                  # JSONL đã xử lý (documents, chunks, relations)
│   └── vector_db/                  # FAISS Vector Index (628 vectors)
│
├── 📄 docs/                         # Tài liệu đặc tả & kiến trúc dự án
│   ├── DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md
│   └── DIRECTORY_STRUCTURE.md
│
└── 🛡️ .gitignore                    # Cấu hình bỏ qua các file đĩa / build / log
```

---

### 🚀 Hướng Dẫn Chạy Hệ Thống

1. **Khởi chạy Backend (FastAPI)** từ thư mục gốc:
   ```powershell
   cd E:\AISCBRAINDAU
   .venv\Scripts\python.exe -m uvicorn backend.api.main:app --reload --port 8000
   ```

2. **Khởi chạy Frontend (React)**:
   ```powershell
   cd E:\AISCBRAINDAU\frontend
   npm run dev
   ```
