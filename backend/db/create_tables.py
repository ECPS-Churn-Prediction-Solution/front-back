"""
데이터베이스 테이블 생성 스크립트
ERD에 정의된 모든 테이블을 데이터베이스에 생성

실행 방법:
    python create_tables.py
"""

from db.database import engine
from db.models import Base
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """
    모든 데이터베이스 테이블 생성
    ERD 기반으로 정의된 모든 테이블을 생성합니다.
    """
    try:
        # SQLAlchemy 모델을 기반으로 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 데이터베이스 테이블이 성공적으로 생성되었습니다.")
        
        # 생성된 테이블 목록 출력
        logger.info("생성된 테이블:")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  - {table_name}")
            
    except Exception as e:
        logger.error(f"❌ 테이블 생성 중 오류 발생: {str(e)}")
        raise

def drop_tables():
    """
    모든 데이터베이스 테이블 삭제
    주의: 모든 데이터가 삭제됩니다!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("⚠️ 모든 데이터베이스 테이블이 삭제되었습니다.")
    except Exception as e:
        logger.error(f"❌ 테이블 삭제 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        # 테이블 삭제 후 재생성
        logger.warning("⚠️ 기존 테이블을 삭제하고 새로 생성합니다...")
        drop_tables()
        create_tables()
    else:
        # 테이블 생성
        create_tables()