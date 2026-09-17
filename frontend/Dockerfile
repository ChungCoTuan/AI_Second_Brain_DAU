# Stage 1: Build the React Application
FROM node:18-alpine AS builder

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy các file cấu hình package để cài đặt dependencies
COPY package.json package-lock.json* ./

# Cài đặt dependencies (dùng ci để đảm bảo tính nhất quán nếu có package-lock)
RUN npm ci || npm install

# Copy toàn bộ mã nguồn
COPY . .

# Build ứng dụng Vite
RUN npm run build

# Stage 2: Serve với Nginx
FROM nginx:alpine

# Copy cấu hình nginx tùy chỉnh cho SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Xóa các file tĩnh mặc định của Nginx và copy file build từ Stage 1
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/dist /usr/share/nginx/html

# Mở port 80
EXPOSE 80

# Chạy Nginx
CMD ["nginx", "-g", "daemon off;"]
