"""
초기 데이터 추가 스크립트
카테고리 등 기본 데이터를 데이터베이스에 추가
"""

from database import SessionLocal, engine
from models import Category
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_initial_categories():
    """
    기본 카테고리 데이터 생성
    """
    db = SessionLocal()
    
    try:
        # 기존 카테고리가 있는지 확인
        existing_categories = db.query(Category).count()
        if existing_categories > 0:
            logger.info(f"이미 {existing_categories}개의 카테고리가 존재합니다.")
            return
        
        # 기본 카테고리 데이터
        categories_data = [
            {"category_id": 1, "category_name": "상의", "parent_id": None},
            {"category_id": 2, "category_name": "하의", "parent_id": None},
            {"category_id": 3, "category_name": "아우터", "parent_id": None},
            {"category_id": 4, "category_name": "신발", "parent_id": None},
            {"category_id": 5, "category_name": "액세서리", "parent_id": None},
            {"category_id": 6, "category_name": "티셔츠", "parent_id": 1},
            {"category_id": 7, "category_name": "셔츠", "parent_id": 1},
            {"category_id": 8, "category_name": "청바지", "parent_id": 2},
            {"category_id": 9, "category_name": "슬랙스", "parent_id": 2},
            {"category_id": 10, "category_name": "재킷", "parent_id": 3},
        ]
        
        # 카테고리 생성
        for cat_data in categories_data:
            category = Category(
                category_name=cat_data["category_name"],
                parent_id=cat_data["parent_id"]
            )
            db.add(category)
        
        db.commit()
        logger.info(f"✅ {len(categories_data)}개의 기본 카테고리가 생성되었습니다.")
        
        # 생성된 카테고리 출력
        categories = db.query(Category).all()
        logger.info("생성된 카테고리:")
        for cat in categories:
            parent = f" (상위: {cat.parent_id})" if cat.parent_id else ""
            logger.info(f"  {cat.category_id}: {cat.category_name}{parent}")
            
    except Exception as e:
        logger.error(f"❌ 카테고리 생성 중 오류: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("🚀 초기 데이터 생성을 시작합니다...")
    create_initial_categories()
    logger.info("✅ 초기 데이터 생성이 완료되었습니다!")