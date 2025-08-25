"""
데이터베이스 연결 및 세션 관리
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 데이터베이스 URL 설정 (절대 경로 사용)
# 이 파일(database.py)의 위치를 기준으로 backend 폴더의 절대 경로를 계산
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'shopping_mall.db'}"

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# 세션 로컬 클래스 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스 생성
Base = declarative_base()

def get_db():
    """
    데이터베이스 세션 의존성 함수
    FastAPI에서 Depends로 사용
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()