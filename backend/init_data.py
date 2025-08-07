"""
초기 데이터 추가 스크립트
카테고리 등 기본 데이터를 데이터베이스에 추가
"""

from database import SessionLocal, engine
from models import Category, Product
from decimal import Decimal
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

def create_initial_products():
    """
    기본 상품 데이터 생성
    """
    db = SessionLocal()

    try:
        # 기존 상품이 있는지 확인
        existing_products = db.query(Product).count()
        if existing_products > 0:
            logger.info(f"이미 {existing_products}개의 상품이 존재합니다.")
            return

        # 기본 상품 데이터
        products_data = [
            {
                "category_id": 6,  # 티셔츠
                "product_name": "기본 면 티셔츠",
                "description": "편안한 착용감의 기본 면 티셔츠입니다.",
                "price": Decimal("25000"),
                "stock_quantity": 100
            },
            {
                "category_id": 6,  # 티셔츠
                "product_name": "프리미엄 오가닉 티셔츠",
                "description": "친환경 오가닉 코튼으로 제작된 프리미엄 티셔츠입니다.",
                "price": Decimal("45000"),
                "stock_quantity": 50
            },
            {
                "category_id": 8,  # 청바지
                "product_name": "클래식 스트레이트 청바지",
                "description": "시대를 초월한 클래식한 스트레이트 핏 청바지입니다.",
                "price": Decimal("89000"),
                "stock_quantity": 75
            },
            {
                "category_id": 8,  # 청바지
                "product_name": "슬림핏 청바지",
                "description": "몸에 딱 맞는 슬림한 핏의 청바지입니다.",
                "price": Decimal("95000"),
                "stock_quantity": 60
            },
            {
                "category_id": 10,  # 재킷
                "product_name": "데님 재킷",
                "description": "캐주얼한 스타일의 데님 재킷입니다.",
                "price": Decimal("120000"),
                "stock_quantity": 30
            }
        ]

        # 상품 생성
        for prod_data in products_data:
            product = Product(
                category_id=prod_data["category_id"],
                product_name=prod_data["product_name"],
                description=prod_data["description"],
                price=prod_data["price"],
                stock_quantity=prod_data["stock_quantity"]
            )
            db.add(product)

        db.commit()
        logger.info(f"✅ {len(products_data)}개의 기본 상품이 생성되었습니다.")

        # 생성된 상품 출력
        products = db.query(Product).all()
        logger.info("생성된 상품:")
        for prod in products:
            logger.info(f"  {prod.product_id}: {prod.product_name} - {prod.price}원")

    except Exception as e:
        logger.error(f"❌ 상품 생성 중 오류: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("🚀 초기 데이터 생성을 시작합니다...")
    create_initial_categories()
    create_initial_products()
    logger.info("✅ 초기 데이터 생성이 완료되었습니다!")