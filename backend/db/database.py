"""
데이터베이스 연결 및 세션 관리
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv

# # 환경변수 로드
# 백엔드 디렉터리와 프로젝트 루트 양쪽의 .env를 모두 시도 로드
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BACKEND_DIR / ".env")

# 데이터베이스 URL 설정
# 우선순위: 환경변수 DATABASE_URL → 개별 DB_* 환경변수 조합 → 로컬 SQLite 파일
BASE_DIR = BACKEND_DIR

database_url_from_env = os.getenv("DATABASE_URL")

if database_url_from_env:
    DATABASE_URL = database_url_from_env
    DATABASE_SOURCE = "env:DATABASE_URL"
else:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        DATABASE_SOURCE = "env:DB_*"
    else:
        DATABASE_URL = f"sqlite:///{BASE_DIR / 'shopping_mall.db'}"
        DATABASE_SOURCE = "default:sqlite"

# 선택된 데이터베이스 정보 간단 출력(민감정보 노출 없음)
try:
    db_scheme = "sqlite" if "sqlite" in DATABASE_URL else "postgresql"
    print(f"[database] Using {db_scheme} via {DATABASE_SOURCE}")
except Exception:
    pass

# SQLAlchemy 엔진 생성 (한 번만 생성)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
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