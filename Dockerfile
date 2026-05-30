FROM node:20-slim AS frontend
WORKDIR /client
COPY client/package*.json ./
RUN npm ci
COPY client/ ./
# Nếu FE-BE chung một container/port, bạn có thể xóa 2 dòng ARG/ENV bên dưới

ARG VITE_API_URL="/api"
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Khai báo các biến môi trường cho Python/FastAPI
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV_MODE="production" \
    USE_FAKE_SENTIMENT_ANALYZER="false" \
    SENTIMENT_MODEL="custom" \
    ABSA_MODEL_PATH="/app/absa_model/absa_svm_model.pkl" \
    ACCESS_TOKEN_EXPIRE_MINUTES=30 \
    DATABASE_URL="sqlite:////app/vi_sense.db" \
    SECRET_KEY="your-production-secret-key" 

COPY core/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ /app/core/

# Copy Frontend vào thư mục tĩnh nằm trong core để FastAPI đọc được
COPY --from=frontend /client/dist /app/core/static

# Tạo sẵn thư mục data bên trong container để chứa file SQLite
RUN mkdir -p /app/data
# Di chuyển vào thư mục core
WORKDIR /app/core

# CHÚ Ý: Copy file script từ máy thật vào gốc của container
COPY entrypoint.sh /entrypoint.sh
# Cấp quyền thực thi cho file script bên trong Linux
RUN chmod +x /entrypoint.sh


EXPOSE 7860
ENTRYPOINT ["/entrypoint.sh"]
