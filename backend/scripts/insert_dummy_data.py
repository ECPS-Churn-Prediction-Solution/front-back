"""
ERD에 맞는 더미데이터 입력 스크립트
"""

import sqlite3
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insert_dummy_data():
    """더미 데이터를 SQLite에 입력"""
    conn = sqlite3.connect('shopping_mall.db')
    cursor = conn.cursor()
    
    try:
        logger.info("🚀 더미데이터 입력을 시작합니다...")
        
        # 1. 카테고리 데이터
        logger.info("📁 카테고리 데이터 입력...")
        categories = [
            # 상위 카테고리
            ('의류', None),
            ('신발', None),
            ('가방', None),
            ('액세서리', None),
            # 하위 카테고리
            ('상의', 1),
            ('하의', 1),
            ('아우터', 1),
            ('운동화', 2),
            ('구두', 2),
            ('백팩', 3),
            ('크로스백', 3),
            ('목걸이', 4),
            ('팔찌', 4)
        ]
        
        cursor.executemany(
            "INSERT INTO categories (category_name, parent_id) VALUES (?, ?)",
            categories
        )
        
        # 2. 상품 데이터
        logger.info("📦 상품 데이터 입력...")
        products = [
            # 상의 (카테고리 5)
            (5, '기본 티셔츠', '편안하고 깔끔한 기본 티셔츠', 29000.0),
            (5, '스트라이프 셔츠', '클래식한 스트라이프 패턴 셔츠', 45000.0),
            (5, '폴로 셔츠', '캐주얼한 폴로 셔츠', 35000.0),
            # 하의 (카테고리 6)
            (6, '슬림 청바지', '슬림핏 청바지', 59000.0),
            (6, '와이드 슬랙스', '편안한 와이드 슬랙스', 69000.0),
            (6, '조거 팬츠', '운동용 조거 팬츠', 39000.0),
            # 아우터 (카테고리 7)
            (7, '후드 집업', '따뜻한 후드 집업', 79000.0),
            (7, '데님 재킷', '빈티지 데님 재킷', 89000.0),
            # 운동화 (카테고리 8)
            (8, '캐주얼 스니커즈', '일상용 캐주얼 스니커즈', 89000.0),
            (8, '러닝화', '운동용 러닝화', 129000.0)
        ]
        
        cursor.executemany(
            "INSERT INTO products (category_id, product_name, description, price) VALUES (?, ?, ?, ?)",
            products
        )
        
        # 3. 상품 옵션 데이터 (ERD의 핵심)
        logger.info("🎨 상품 옵션 데이터 입력...")
        variants = [
            # 기본 티셔츠 (product_id: 1)
            (1, '화이트', 'S', 50), (1, '화이트', 'M', 80), (1, '화이트', 'L', 60),
            (1, '블랙', 'S', 45), (1, '블랙', 'M', 75), (1, '블랙', 'L', 55),
            (1, '그레이', 'M', 40), (1, '그레이', 'L', 35),
            
            # 스트라이프 셔츠 (product_id: 2)
            (2, '네이비', 'S', 30), (2, '네이비', 'M', 50), (2, '네이비', 'L', 40),
            (2, '화이트', 'M', 25), (2, '화이트', 'L', 30),
            
            # 폴로 셔츠 (product_id: 3)
            (3, '네이비', 'M', 35), (3, '네이비', 'L', 40), (3, '그레이', 'M', 30),
            
            # 슬림 청바지 (product_id: 4)
            (4, '블루', '28', 25), (4, '블루', '30', 35), (4, '블루', '32', 30), (4, '블루', '34', 20),
            (4, '블랙', '30', 25), (4, '블랙', '32', 20),
            
            # 와이드 슬랙스 (product_id: 5)
            (5, '블랙', '28', 20), (5, '블랙', '30', 30), (5, '블랙', '32', 25),
            (5, '베이지', '30', 15), (5, '베이지', '32', 20),
            
            # 조거 팬츠 (product_id: 6)
            (6, '그레이', 'M', 40), (6, '그레이', 'L', 45), (6, '블랙', 'M', 35), (6, '블랙', 'L', 40),
            
            # 후드 집업 (product_id: 7)
            (7, '그레이', 'M', 25), (7, '그레이', 'L', 30), (7, '블랙', 'M', 20), (7, '블랙', 'L', 25),
            
            # 데님 재킷 (product_id: 8)
            (8, '인디고', 'M', 15), (8, '인디고', 'L', 20), (8, '라이트블루', 'M', 10),
            
            # 캐주얼 스니커즈 (product_id: 9)
            (9, '화이트', '250', 30), (9, '화이트', '260', 40), (9, '화이트', '270', 35),
            (9, '블랙', '250', 25), (9, '블랙', '260', 30), (9, '블랙', '270', 25),
            
            # 러닝화 (product_id: 10)
            (10, '화이트', '250', 20), (10, '화이트', '260', 25), (10, '화이트', '270', 20),
            (10, '레드', '260', 15), (10, '레드', '270', 18)
        ]
        
        cursor.executemany(
            "INSERT INTO product_variants (product_id, color, size, stock_quantity) VALUES (?, ?, ?, ?)",
            variants
        )
        
        # 4. 테스트 사용자 데이터
        logger.info("👤 사용자 데이터 입력...")
        users = [
            ('test1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxqC3G', '김테스트', 'male', '1990-05-15', '010-1111-1111', '12345', '서울시 강남구 테헤란로 123', '101호'),
            ('test2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxqC3G', '이유저', 'female', '1995-08-22', '010-2222-2222', '54321', '서울시 서초구 서초대로 456', '202호'),
            ('test3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxqC3G', '박고객', 'other', '1988-12-03', '010-3333-3333', '67890', '서울시 마포구 홍대로 789', '303호')
        ]
        
        cursor.executemany(
            "INSERT INTO users (email, password_hash, user_name, gender, birthdate, phone_number, zip_code, address_main, address_detail) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            users
        )
        
        # 5. 사용자 관심사 데이터
        logger.info("❤️ 사용자 관심사 데이터 입력...")
        interests = [
            (1, 5), (1, 6), (1, 8),  # 김테스트: 상의, 하의, 운동화
            (2, 5), (2, 7), (2, 11), # 이유저: 상의, 아우터, 크로스백
            (3, 6), (3, 8), (3, 12)  # 박고객: 하의, 운동화, 목걸이
        ]
        
        cursor.executemany(
            "INSERT INTO user_interests (user_id, category_id) VALUES (?, ?)",
            interests
        )
        
        # 6. 테스트용 장바구니 데이터 (ERD variant_id 기준)
        logger.info("🛒 장바구니 데이터 입력...")
        cart_items = [
            (1, 1, 2),   # 김테스트: 화이트 티셔츠 S 2개
            (1, 17, 1),  # 김테스트: 블루 청바지 28 1개
            (2, 3, 1),   # 이유저: 화이트 티셔츠 L 1개
            (2, 33, 1),  # 이유저: 그레이 후드 M 1개
            (3, 20, 1)   # 박고객: 블루 청바지 32 1개
        ]
        
        cursor.executemany(
            "INSERT INTO cart_items (user_id, variant_id, quantity) VALUES (?, ?, ?)",
            cart_items
        )
        
        # 커밋
        conn.commit()
        
        # 결과 확인
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products")
        prod_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM product_variants")
        var_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM cart_items")
        cart_count = cursor.fetchone()[0]
        
        logger.info("✅ 더미데이터 입력 완료!")
        logger.info(f"📊 생성된 데이터:")
        logger.info(f"   - 카테고리: {cat_count}개")
        logger.info(f"   - 상품: {prod_count}개")
        logger.info(f"   - 상품옵션: {var_count}개")
        logger.info(f"   - 사용자: {user_count}개")
        logger.info(f"   - 장바구니: {cart_count}개")
        logger.info("🔐 테스트 계정 비밀번호: password123")
        
    except Exception as e:
        logger.error(f"❌ 더미데이터 입력 실패: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    insert_dummy_data()
