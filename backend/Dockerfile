# Sử dụng Python 3.11 làm base image
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết (build-essential, vv.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements
COPY requirements_langchain.txt .

# Cài đặt dependencies từ requirements_langchain.txt và các thư viện web server
# Lưu ý: Cài thêm fastapi, uvicorn, python-multipart vì có thể requirements_langchain.txt thiếu
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_langchain.txt && \
    pip install --no-cache-dir fastapi uvicorn python-multipart

# Đặt biến môi trường
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Copy toàn bộ mã nguồn của backend vào /app
# Lưu ý: Thư mục backend của repo chính là root context khi build docker-compose.
# Khi copy '.', nó sẽ copy các file từ backend/ vào /app.
COPY . .

# Mở port 8000
EXPOSE 8000

# Lệnh khởi chạy server bằng uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
