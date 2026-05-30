#!/bin/sh

# Thoát ngay lập tức nếu có lệnh nào bị lỗi
set -e

# Khởi tạo Database SQLite
echo "Starting database initialization..."
python init_db.py

# Khởi động FastAPI server
echo "Starting FastAPI server..."
python run.py
