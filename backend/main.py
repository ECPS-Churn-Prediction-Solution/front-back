"""
FastAPI 애플리케이션 실행 파일
"""

import uvicorn
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "True").lower() == "true",  # 개발용 리로드
        log_level=os.getenv("LOG_LEVEL", "info")
    )