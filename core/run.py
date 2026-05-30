#!/usr/bin/env python3

import os
import sys
import uvicorn
from dotenv import load_dotenv
load_dotenv() 



# Ensure parent directory is on sys.path so sibling packages like `crawler` can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import app

if __name__ == "__main__":
    env_mode = os.getenv("ENV_MODE", "development").lower()

    if env_mode in ["production", "prod", "staging"]:
        # Hugging Face Spaces bắt buộc chạy ở cổng 7860
        port = int(os.getenv("PORT", 7860)) 
        reload_mode = False
        print(f"🚀 Chạy ứng dụng ở chế độ PRODUCTION (Port: {port}, Reload: Off)")
    else:
        port = int(os.getenv("PORT", 8000))
        reload_mode = False
        print(f"🚀 Chạy ứng dụng ở chế độ DEVELOPMENT (Port: {port}, Reload: On)")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload_mode,
        log_level="info"
    )