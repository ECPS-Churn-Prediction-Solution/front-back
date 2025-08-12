"""
초기 데이터 추가 스크립트
카테고리 등 기본 데이터를 데이터베이스에 추가
"""

from database import SessionLocal, engine
from models import Category, Product, ProductVariant
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
                "price": 25000
            },
            {
                "category_id": 6,  # 티셔츠
                "product_name": "프리미엄 오가닉 티셔츠",
                "description": "친환경 오가닉 코튼으로 제작된 프리미엄 티셔츠입니다.",
                "price": 45000
            },
            {
                "category_id": 8,  # 청바지
                "product_name": "클래식 스트레이트 청바지",
                "description": "시대를 초월한 클래식한 스트레이트 핏 청바지입니다.",
                "price": 89000
            },
            {
                "category_id": 8,  # 청바지
                "product_name": "슬림핏 청바지",
                "description": "몸에 딱 맞는 슬림한 핏의 청바지입니다.",
                "price": 95000
            },
            {
                "category_id": 10,  # 재킷
                "product_name": "데님 재킷",
                "description": "캐주얼한 스타일의 데님 재킷입니다.",
                "price": 120000
            }
        ]

        # 상품 생성
        for prod_data in products_data:
            product = Product(
                category_id=prod_data["category_id"],
                product_name=prod_data["product_name"],
                description=prod_data["description"],
                price=prod_data["price"]
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


def create_initial_variants():
    """기본 상품 옵션 데이터 생성"""
    db = SessionLocal()

    try:
        # 기존 상품 옵션이 있는지 확인
        existing_variants = db.query(ProductVariant).count()
        if existing_variants > 0:
            logger.info("상품 옵션 데이터가 이미 존재합니다.")
            return

        # 각 상품에 대한 기본 옵션 생성
        variants_data = [
            # 기본 면 티셔츠 (product_id: 1)
            {"product_id": 1, "color": "화이트", "size": "M", "stock_quantity": 50},
            {"product_id": 1, "color": "블랙", "size": "M", "stock_quantity": 30},
            {"product_id": 1, "color": "화이트", "size": "L", "stock_quantity": 40},

            # 프리미엄 오가닉 티셔츠 (product_id: 2)
            {"product_id": 2, "color": "베이지", "size": "M", "stock_quantity": 25},
            {"product_id": 2, "color": "네이비", "size": "L", "stock_quantity": 20},

            # 클래식 스트레이트 청바지 (product_id: 3)
            {"product_id": 3, "color": "인디고", "size": "30", "stock_quantity": 35},
            {"product_id": 3, "color": "인디고", "size": "32", "stock_quantity": 40},

            # 슬림핏 청바지 (product_id: 4)
            {"product_id": 4, "color": "다크블루", "size": "30", "stock_quantity": 30},
            {"product_id": 4, "color": "다크블루", "size": "32", "stock_quantity": 30},

            # 데님 재킷 (product_id: 5)
            {"product_id": 5, "color": "라이트블루", "size": "M", "stock_quantity": 15},
            {"product_id": 5, "color": "라이트블루", "size": "L", "stock_quantity": 15},
        ]


def create_initial_product_variants():
    """
    기본 상품 옵션 데이터 생성
    """
    db = SessionLocal()

    try:
        from models import ProductVariant
        
        # 기존 옵션이 있는지 확인
        existing_variants = db.query(ProductVariant).count()
        if existing_variants > 0:
            logger.info(f"이미 {existing_variants}개의 상품 옵션이 존재합니다.")
            return

        # 기본 상품 옵션 데이터
        variants_data = [
            # 기본 면 티셔츠 (상품 ID: 1)
            {"product_id": 1, "color": "화이트", "size": "S", "stock_quantity": 20, "price_adjustment": Decimal("0")},
            {"product_id": 1, "color": "화이트", "size": "M", "stock_quantity": 25, "price_adjustment": Decimal("0")},
            {"product_id": 1, "color": "화이트", "size": "L", "stock_quantity": 20, "price_adjustment": Decimal("0")},
            {"product_id": 1, "color": "블랙", "size": "S", "stock_quantity": 15, "price_adjustment": Decimal("0")},
            {"product_id": 1, "color": "블랙", "size": "M", "stock_quantity": 20, "price_adjustment": Decimal("0")},
            
            # 프리미엄 오가닉 티셔츠 (상품 ID: 2)
            {"product_id": 2, "color": "네이비", "size": "S", "stock_quantity": 10, "price_adjustment": Decimal("0")},
            {"product_id": 2, "color": "네이비", "size": "M", "stock_quantity": 15, "price_adjustment": Decimal("0")},
            {"product_id": 2, "color": "네이비", "size": "L", "stock_quantity": 10, "price_adjustment": Decimal("0")},
            {"product_id": 2, "color": "그레이", "size": "M", "stock_quantity": 15, "price_adjustment": Decimal("0")},
            
            # 클래식 스트레이트 청바지 (상품 ID: 3)
            {"product_id": 3, "color": "블루", "size": "28", "stock_quantity": 15, "price_adjustment": Decimal("0")},
            {"product_id": 3, "color": "블루", "size": "30", "stock_quantity": 20, "price_adjustment": Decimal("0")},
            {"product_id": 3, "color": "블루", "size": "32", "stock_quantity": 20, "price_adjustment": Decimal("0")},
            {"product_id": 3, "color": "블루", "size": "34", "stock_quantity": 20, "price_adjustment": Decimal("0")},
            
            # 슬림핏 청바지 (상품 ID: 4)
            {"product_id": 4, "color": "다크블루", "size": "28", "stock_quantity": 12, "price_adjustment": Decimal("0")},
            {"product_id": 4, "color": "다크블루", "size": "30", "stock_quantity": 18, "price_adjustment": Decimal("0")},
            {"product_id": 4, "color": "다크블루", "size": "32", "stock_quantity": 18, "price_adjustment": Decimal("0")},
            {"product_id": 4, "color": "블랙", "size": "30", "stock_quantity": 12, "price_adjustment": Decimal("5000")},
            
            # 데님 재킷 (상품 ID: 5)
            {"product_id": 5, "color": "라이트블루", "size": "S", "stock_quantity": 8, "price_adjustment": Decimal("0")},
            {"product_id": 5, "color": "라이트블루", "size": "M", "stock_quantity": 12, "price_adjustment": Decimal("0")},
            {"product_id": 5, "color": "라이트블루", "size": "L", "stock_quantity": 10, "price_adjustment": Decimal("0")},
        ]

        # 상품 옵션 생성

        for variant_data in variants_data:
            variant = ProductVariant(
                product_id=variant_data["product_id"],
                color=variant_data["color"],
                size=variant_data["size"],

                stock_quantity=variant_data["stock_quantity"]

                stock_quantity=variant_data["stock_quantity"],
                price_adjustment=variant_data["price_adjustment"]

            )
            db.add(variant)

        db.commit()


        # 생성된 옵션 확인
        created_variants = db.query(ProductVariant).all()
        logger.info(f"✅ {len(created_variants)}개의 기본 상품 옵션이 생성되었습니다.")
        logger.info("생성된 상품 옵션:")
        for variant in created_variants:
            logger.info(f"  {variant.variant_id}: {variant.product.product_name} - {variant.color}/{variant.size} (재고: {variant.stock_quantity}개)")

        logger.info(f"✅ {len(variants_data)}개의 상품 옵션이 생성되었습니다.")

        # 생성된 옵션 출력
        variants = db.query(ProductVariant).all()
        logger.info("생성된 상품 옵션:")
        for var in variants:
            price_info = f" (+{var.price_adjustment}원)" if var.price_adjustment > 0 else ""
            logger.info(f"  상품 {var.product_id}: {var.color} {var.size} - 재고 {var.stock_quantity}개{price_info}")


    except Exception as e:
        logger.error(f"❌ 상품 옵션 생성 중 오류: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("🚀 초기 데이터 생성을 시작합니다...")
    create_initial_categories()
    create_initial_products()

    create_initial_variants()

    create_initial_product_variants()

    logger.info("✅ 초기 데이터 생성이 완료되었습니다!")