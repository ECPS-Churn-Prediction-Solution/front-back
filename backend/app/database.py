"""
데이터베이스 연결 및 세션 관리
SQLite 사용 (환경변수 지원)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 데이터베이스 URL (환경변수에서 가져오거나 기본값 사용)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shopping_mall.db")

# 데이터베이스 엔진 생성
if DATABASE_URL.startswith("sqlite"):
    # SQLite 설정
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite 멀티스레드 지원
        echo=os.getenv("DEBUG", "True").lower() == "true"  # 환경변수로 SQL 로그 제어
    )
else:
    # PostgreSQL 설정
    engine = create_engine(
        DATABASE_URL,
        echo=os.getenv("DEBUG", "True").lower() == "true"
    )

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
