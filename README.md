# DAU Second Brain 🧠
> **Hệ thống tóm tắt & tra cứu văn bản tiếng Việt có trích dẫn — Chống bịa đặt thông tin — Dành cho Trường Đại học Kiến trúc Đà Nẵng.**  
> *Đồ án môn Trí tuệ Nhân tạo | Nhóm 2 sinh viên | Thời gian thực hiện: 12 tuần*

---

## 📌 1. Giới thiệu tổng quan

**DAU Second Brain** là giải pháp phần mềm thông minh hỗ trợ Ban Giám hiệu, Phòng Đào tạo và đội ngũ giảng viên Trường Đại học Kiến trúc Đà Nẵng giải quyết bài toán xử lý lượng lớn văn bản pháp quy (thông tư, quyết định, quy chế của Bộ GD&ĐT) và tài liệu điều hành nội bộ.

Điểm khác biệt cốt lõi:
- **Tuyệt đối chống bịa đặt (Zero-Hallucination Gate):** Mọi câu tóm tắt hoặc nội dung AI sinh ra đều trải qua kiểm chứng suy luận tự nhiên (NLI - Natural Language Inference) với 3 nhãn (*entailment*, *contradiction*, *neutral*) trước khi được hiển thị.
- **Minh bạch trích dẫn (Verifiable Citations):** Mọi dữ liệu trích xuất đều được gắn ID đoạn nguồn nguyên bản trong văn bản gốc.
- **Publish Gate (Human-in-the-loop):** Các văn bản có phát hiện mâu thuẫn (`contradiction`) sẽ bị khóa tự động và đưa vào quy trình rà soát, kiểm duyệt có lưu vết kiểm toán (Audit Trail) trước khi công bố.

---

## 🎯 2. Nguyên tắc học thuật cốt lõi của Đồ án AI

> [!IMPORTANT]
> **Đồ án tuân thủ nghiêm ngặt chuẩn mực đồ án Trí tuệ Nhân tạo:**
> - **100% Pipeline cốt lõi sử dụng mô hình AI và thuật toán cục bộ (Local AI/NLP):**
>   - Bóc tách văn bản, OCR: `Tesseract OCR` kết hợp `PyPDF2` / `pdf2image`.
>   - Trích xuất thông tin cấu trúc (Metadata, ngày ban hành, chủ thể, căn cứ pháp lý, hiệu lực): Thuật toán xử lý ngôn ngữ tự nhiên (NLP) dựa trên Rule-based Pattern Matching & Regex quy chuẩn văn bản hành chính Việt Nam.
>   - Tóm tắt trích dẫn: Mô hình ngôn ngữ chuyên sâu tiếng Việt (`ViT5` / `BARTpho`).
>   - Kiểm chứng mâu thuẫn (Faithfulness / NLI 3 nhãn): Mô hình phân loại ngữ nghĩa đa ngôn ngữ (`XLM-RoBERTa-large-xnli` / PhoBERT NLI).
>   - Vector Embedding & Cây văn bản: `SentenceTransformers` (`paraphrase-multilingual-MiniLM-L12-v2`).
> - **Duy nhất chức năng "Tra cứu AI (Chatbot)"** được tích hợp Google Gemini API nhằm đóng vai trò trợ lý hỏi đáp thông minh và tổng hợp câu trả lời tự nhiên dựa trên ngữ cảnh văn bản đã được kiểm duyệt.

---

## 📂 3. Cấu trúc thư mục dự án

```
AI_Second_Brain_DAU/
├── backend/                         # Backend FastAPI & AI Pipeline
│   ├── app/
│   │   ├── api/                     # Router API endpoints (auth, documents, chatbot, review...)
│   │   ├── core/                    # Cấu hình hệ thống, bảo mật JWT, database engine
│   │   ├── models/                  # SQLAlchemy ORM Models (User, Document, Section, ReviewLog...)
│   │   ├── schemas/                 # Pydantic Schemas validate dữ liệu
│   │   └── services/                # Các dịch vụ xử lý nghiệp vụ & AI Models:
│   │       ├── ingestion_service.py     # Đọc PDF, OCR, chia đoạn (chunking)
│   │       ├── extraction_service.py    # Bóc tách metadata, thực thể, căn cứ
│   │       ├── summarization_service.py # Tóm tắt tiếng Việt (ViT5/BARTpho)
│   │       ├── nli_service.py           # NLI 3 nhãn kiểm tra mâu thuẫn
│   │       ├── vector_service.py        # Embedding & Tìm kiếm vector tương đồng
│   │       └── gemini_service.py        # Gemini AI Assistant (chỉ dùng cho Tab Tra cứu AI)
│   ├── bin/                         # Các công cụ nhị phân đóng gói sẵn (Tesseract, Poppler)
│   │   ├── Tesseract-OCR/           # Binary Tesseract OCR chạy độc lập (portable)
│   │   ├── tessdata/                # Language pack tiếng Việt (vie.traineddata)
│   │   └── poppler/                 # Poppler binaries (pdftoppm, pdfinfo)
│   ├── .env.example                 # Mẫu cấu hình môi trường backend
│   └── requirements.txt             # Danh mục thư viện Python backend
│
├── frontend/                        # Frontend Single Page Application (React + Vite)
│   ├── src/
│   │   ├── components/              # Các UI components (Header, Sidebar, ConfirmModal...)
│   │   ├── pages/                   # Các trang giao diện (Login, Ingestion, Review, QA, Graph...)
│   │   ├── services/                # Axios API clients kết nối backend
│   │   └── types/                   # TypeScript interfaces định nghĩa cấu trúc dữ liệu
│   ├── package.json                 # Cấu hình gói và script npm
│   └── vite.config.ts
│
├── docs/                            # Toàn bộ tài liệu đặc tả kiến trúc đồ án (8 tài liệu)
├── requirements.py                  # 🩺 BỘ CÔNG CỤ TỰ ĐỘNG CHẨN ĐOÁN & CÀI ĐẶT MÔI TRƯỜNG
├── requirements.txt                 # Danh mục thư viện Python chuẩn ở thư mục gốc
└── README.md                        # Hướng dẫn cài đặt và lưu ý vận hành
```

---

## 🚀 4. Hướng dẫn Khởi chạy Dự án (Quick Start)

### ⚙️ Yêu cầu môi trường tối thiểu
- **Hệ điều hành:** Windows 10/11 (64-bit), macOS hoặc Linux.
- **Python:** `Python 3.10` đến `Python 3.12` (Khuyến nghị **Python 3.11**; *tránh Python 3.13*).
- **Node.js:** `Node.js v18` hoặc cao hơn.
- **Cơ sở dữ liệu:** `PostgreSQL 14+`.
- **Phần cứng:** RAM tối thiểu 8GB (Khuyến nghị 16GB hoặc kích hoạt Virtual Memory theo mục 5).

---

### 👉 Cách 1: Khởi động tự động bằng Bộ Chẩn Đoán (Khuyên dùng)

Dự án cung cấp script `requirements.py` giúp tự động kiểm tra phiên bản Python, cài đặt toàn bộ thư viện pip, kiểm tra Tesseract OCR, Poppler, PostgreSQL, cấu hình `.env` và cảnh báo bộ nhớ ảo.

Mở terminal tại thư mục gốc của dự án và chạy:
```bash
python requirements.py
```
*Script sẽ kiểm tra và thông báo chính xác máy tính của bạn đã đủ điều kiện chạy hay còn thiếu bước nào.*

---

### 👉 Cách 2: Cài đặt & Khởi động thủ công từng bước

#### Bước 1: Thiết lập Cơ sở dữ liệu PostgreSQL
1. Mở **pgAdmin** hoặc giao diện dòng lệnh `psql`.
2. Tạo một database mới tên là `dau_second_brain`:
   ```sql
   CREATE DATABASE dau_second_brain;
   ```

#### Bước 2: Cấu hình biến môi trường Backend
1. Đi tới thư mục `backend/`:
   ```bash
   cd backend
   ```
2. Tạo file `.env` từ file `.env.example`:
   ```bash
   copy .env.example .env
   ```
3. Mở file `.env` và điền mật khẩu PostgreSQL của máy bạn:
   ```env
   DATABASE_URL=postgresql://postgres:<MAT_KHAU_CUA_BAN>@localhost:5432/dau_second_brain
   SECRET_KEY=dau_second_brain_secret_key_change_in_production
   GEMINI_API_KEY=<API_KEY_GEMINI_CUA_BAN>
   ```

#### Bước 3: Cài đặt và Chạy Backend (FastAPI)
1. Tạo môi trường ảo Python (Virtual Environment):
   ```bash
   cd backend
   python -m venv venv
   ```
2. Kích hoạt môi trường ảo:
   - **Windows PowerShell:**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows Command Prompt:**
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **Linux / macOS:**
     ```bash
     source venv/bin/activate
     ```
3. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
4. Khởi chạy máy chủ Backend:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   > Backend sẽ hoạt động tại: **http://localhost:8000**  
   > Tài liệu API Swagger UI: **http://localhost:8000/docs**

#### Bước 4: Cài đặt và Chạy Frontend (React + Vite)
Mở một cửa sổ Terminal **mới**:
```bash
cd frontend
npm install
npm run dev
```
> Giao diện Web hoạt động tại: **http://localhost:5173**  
> *Đăng nhập nhanh:* Trên màn hình đăng nhập có sẵn nút **"Điền nhanh (Admin)"** để đăng nhập bằng tài khoản quản trị mặc định.

---

## ⚠️ 5. NHỮNG ĐIỀU CẦN LƯU Ý: VÌ SAO MÁY KHÁC KHÔNG CHẠY ĐƯỢC? (TOP 7 LỖI PHỔ BIẾN & CÁCH SỬA)

Khi mang mã nguồn dự án sang một máy tính khác (máy của giáo viên, máy sinh viên khác, hoặc máy tính phòng lab), rất dễ gặp lỗi không khởi động được hoặc crash chương trình. Dưới đây là **7 nguyên nhân chính** đã được đúc kết từ thực tế cùng giải pháp xử lý triệt để:

---

### 🚨 Lỗi 1: Thiếu Tesseract OCR Binary (`tesseract is not installed or it's not in your PATH`)
- **Nguyên nhân:** Gói Python `pytesseract` chỉ là một thư viện wrapper (cầu nối). Nó **không chứa** bộ máy nhận dạng OCR thực sự. Nếu máy tính chưa cài Tesseract OCR dạng thực thi (`tesseract.exe`), hệ thống sẽ văng lỗi ngay khi người dùng tải lên tài liệu scan.
- **Cách khắc phục:**
  - **Cách tốt nhất:** Dự án đã tích hợp sẵn thư mục binary Tesseract tại `backend/bin/Tesseract-OCR/`. Hệ thống backend tự động dò tìm thư mục này nếu trong `PATH` hệ thống chưa có.
  - **Cách thủ công (nếu muốn cài độc lập):** Tải và cài đặt Tesseract OCR cho Windows từ [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki), cài vào `C:\Program Files\Tesseract-OCR`, sau đó thêm đường dẫn này vào biến môi trường `PATH`.

---

### 🚨 Lỗi 2: Thiếu Language Pack Tiếng Việt (`Error: tessdata/vie.traineddata not found`)
- **Nguyên nhân:** Mặc định Tesseract cài trên máy chỉ có bộ dữ liệu tiếng Anh (`eng`). Khi hệ thống gọi OCR cho công văn tiếng Việt với tham số `lang='vie'`, Tesseract sẽ báo lỗi crash do thiếu file từ điển `vie.traineddata`.
- **Cách khắc phục:**
  - Dự án đã lưu sẵn file này trong thư mục `backend/bin/tessdata/vie.traineddata`.
  - Nếu bạn cài Tesseract ở `C:\Program Files\Tesseract-OCR`, hãy copy file `vie.traineddata` vào thư mục `C:\Program Files\Tesseract-OCR\tessdata\`.

---

### 🚨 Lỗi 3: Thiếu Poppler Engine (`pdf2image.exceptions.PDFInfoNotInstalledError`)
- **Nguyên nhân:** Để bóc tách và OCR các file văn bản PDF dạng scan hoặc chứa hình ảnh, thư viện `pdf2image` bắt buộc phải sử dụng công cụ nhị phân Poppler (`pdftoppm.exe` và `pdfinfo.exe`) để render trang PDF thành định dạng ảnh RGB trước khi đưa vào Tesseract.
- **Cách khắc phục:**
  - Dự án đã tích hợp sẵn Poppler trong `backend/bin/poppler/Library/bin/`.
  - Hoặc bạn có thể cài nhanh trên Windows qua lệnh PowerShell:
    ```powershell
    winget install osdn.poppler
    ```

---

### 🚨 Lỗi 4: Lỗi Tràn RAM & Thiếu Bộ Nhớ Ảo Windows (`WinError 1455 - The paging file is too small`)
- **Triệu chứng:** Khi khởi động backend hoặc khi nạp mô hình NLI (`XLM-RoBERTa`), tiến trình Python bất ngờ bị dừng đột ngột hoặc xuất hiện lỗi:
  ```text
  OSError: [WinError 1455] The paging file is too small for this operation to complete.
  Error loading "torch\lib\fbgemm.dll" or one of its dependencies.
  ```
- **Nguyên nhân:** Các mô hình học sâu (Deep Learning) của PyTorch chiếm dung lượng bộ nhớ lớn khi khởi tạo tensor. Trên các máy có RAM 8GB hoặc 16GB nhưng Windows đang tắt bộ nhớ ảo (Paging File) hoặc ổ C: bị đầy dung lượng, Windows sẽ từ chối cấp phát bộ nhớ ảo dẫn đến crash.
- **Cách khắc phục chi tiết:**
  1. Nhấn tổ hợp phím `Win + R`, gõ `sysdm.cpl` rồi nhấn **Enter**.
  2. Chọn tab **Advanced** (Nâng cao) ➔ Tại mục *Performance* (Hiệu năng), bấm nút **Settings...**.
  3. Chọn tab **Advanced** trong cửa sổ mới ➔ Tại mục *Virtual memory*, bấm **Change...**.
  4. Bỏ dấu tích ở ô *"Automatically manage paging file size for all drives"*.
  5. Chọn ổ đĩa có dung lượng trống lớn (ổ C: hoặc D:) ➔ Chọn **Custom size**:
     - **Initial size (MB):** `8192` (8 GB)
     - **Maximum size (MB):** `16384` (16 GB)
  6. Bấm nút **Set** ➔ Bấm **OK** và khởi động lại máy tính (Restart PC).

---

### 🚨 Lỗi 5: Chưa khởi tạo Database PostgreSQL hoặc sai mật khẩu kết nối
- **Triệu chứng:** Backend khởi động báo lỗi đỏ:
  ```text
  sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "localhost" (127.0.0.1), port 5432 failed
  FATAL: password authentication failed for user "postgres"
  hoặc FATAL: database "dau_second_brain" does not exist
  ```
- **Cách khắc phục:**
  1. Đảm bảo dịch vụ PostgreSQL Server đang chạy (mở `services.msc` kiểm tra dịch vụ `postgresql-x64-xx` đang ở trạng thái *Running*).
  2. Mở pgAdmin hoặc dòng lệnh tạo database tên `dau_second_brain`.
  3. Mở file `backend/.env`, kiểm tra kỹ tên tài khoản (`postgres`) và mật khẩu của bạn.

---

### 🚨 Lỗi 6: Dùng phiên bản Python quá mới (Python 3.13+) hoặc quá cũ (dưới 3.10)
- **Triệu chứng:** Chạy `pip install -r requirements.txt` bị văng lỗi biên dịch C/C++ dài dòng (`error: command 'cl.exe' failed`, `wheel build failed for tokenizers / sentencepiece`).
- **Nguyên nhân:** Python 3.13 mới phát hành nên các gói deep learning (PyTorch, Tokenizers, SciPy) chưa kịp phân phối bản binary wheels dựng sẵn (.whl), khiến pip cố gắng compile mã nguồn C++ nhưng máy tính thiếu Visual Studio C++ Build Tools.
- **Cách khắc phục:** Sử dụng **Python 3.10** hoặc **Python 3.11** (64-bit). Khuyến nghị tải bản cài đặt chính thức từ [python.org](https://www.python.org/downloads/).

---

### 🚨 Lỗi 7: Máy tính không có Internet trong lần đầu tiên chạy mô hình (HuggingFace Cache)
- **Triệu chứng:** Khi chạy tóm tắt hoặc kiểm tra NLI lần đầu, chương trình bị treo lâu hoặc báo lỗi `requests.exceptions.ConnectionError` từ `huggingface.co`.
- **Nguyên nhân:** Lần đầu tiên chạy, thư viện Transformers cần kết nối internet để tải file trọng số (weights) của mô hình về thư mục cache trên máy (`~/.cache/huggingface/hub/`).
- **Cách khắc phục:**
  - Máy tính cần kết nối internet ổn định trong lần chạy thử nghiệm văn bản đầu tiên.
  - Sau khi weights đã tải về máy thành công một lần, hệ thống sẽ tự động chuyển sang chế độ nạp offline hoàn toàn từ cache cục bộ cho các lần chạy sau.

---

## 📚 6. Danh mục Tài liệu Kỹ thuật Đồ án

Toàn bộ tài liệu phân tích, thiết kế và kế hoạch chi tiết của đồ án được lưu trữ trong thư mục `docs/`:

| # | Tài liệu | Nội dung tóm lược |
|---|---|---|
| 1 | [Đề cương chi tiết đồ án](docs/DAU_Second_Brain_De_Cuong_Chi_Tiet.md) | Mục tiêu, đặt vấn đề, phạm vi, tổng quan giải pháp |
| 2 | [Đặc tả Nghiệp vụ & Kiến trúc](docs/DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md) | Phân tầng kiến trúc, luồng dữ liệu, Scrum, rủi ro kỹ thuật |
| 3 | [Đặc tả Yêu cầu Chức năng (SRS)](docs/DAU_Second_Brain_Dac_Ta_Yeu_Cau_Chuc_Nang.md) | Danh sách Use Cases chi tiết, yêu cầu chức năng & phi chức năng |
| 4 | [Thiết kế Giao diện (UI/UX Spec)](docs/DAU_Second_Brain_UIUX_Spec.md) | Wireframe, màn hình chức năng, design tokens & hệ màu |
| 5 | [Kế hoạch Thu thập & Xử lý Dữ liệu](docs/DAU_Second_Brain_Ke_Hoach_Du_Lieu.md) | Nguồn thu thập văn bản, quy chuẩn tiền xử lý, gán nhãn dữ liệu |
| 6 | [Kế hoạch Đánh giá & Tiêu chí Nghiệm thu](docs/DAU_Second_Brain_Ke_Hoach_Danh_Gia.md) | Bộ chỉ số đánh giá (ROUGE, BERTScore, NLI accuracy), ma trận test |
| 7 | [Bảng Phân công Công việc (RACI)](docs/DAU_Second_Brain_Phan_Cong_RACI.md) | Ma trận trách nhiệm phân công 2 thành viên theo từng Sprint |
| 8 | [Các Thuật toán Sử dụng](docs/CÁC%20THUẬT%20TOÁN%20SỬ%20DỤNG.md) | Phân tích toán học, cơ chế hoạt động và vai trò của từng thuật toán |

---

## 👥 7. Đội ngũ Thực hiện

- **Đơn vị đào tạo:** Trường Đại học Kiến trúc Đà Nẵng (DAU).
- **Học phần:** Đồ án Môn học Trí tuệ Nhân tạo.
- **Thành viên nhóm:** Nhóm gồm 2 sinh viên chuyên ngành Công nghệ Thông tin.
- **Quy chuẩn phát triển mã nguồn:** Tuân thủ Git Flow chuẩn (`main` ← `dev` ← `feature/*`), commit theo chuẩn Conventional Commits.

---

## 📄 8. Bản quyền & Giấy phép

Đồ án được thực hiện phục vụ mục đích nghiên cứu học thuật và chuyển đổi số quản trị đại học tại **Trường Đại học Kiến trúc Đà Nẵng**. Mọi quyền được bảo lưu.
