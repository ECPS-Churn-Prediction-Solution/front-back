"""
ERD에 맞는 더미데이터 입력 스크립트 (DB-agnostic: SQLite/Postgres 모두 지원)
"""

import logging
from typing import List, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# 로컬 패키지(import 충돌 방지)를 위해 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.database import engine

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def insert_dummy_data():
    """더미 데이터를 현재 DATABASE_URL이 가리키는 DB에 입력"""
    with Session(bind=engine) as session:
        try:
            logger.info("🚀 더미데이터 입력을 시작합니다...")

            # 1. 카테고리 데이터
            logger.info("📁 카테고리 데이터 입력...")
            parent_names = ['의류', '신발', '가방', '액세서리']
            name_to_category_id: dict = {}

            # 상위 카테고리 upsert
            for pname in parent_names:
                cid = session.execute(
                    text("SELECT category_id FROM categories WHERE category_name = :name"),
                    {"name": pname}
                ).scalar()
                if not cid:
                    session.execute(
                        text("INSERT INTO categories (category_name, parent_id) VALUES (:name, :parent_id)"),
                        {"name": pname, "parent_id": None}
                    )
                    cid = session.execute(
                        text("SELECT category_id FROM categories WHERE category_name = :name"),
                        {"name": pname}
                    ).scalar()
                name_to_category_id[pname] = cid

            # 하위 카테고리 (부모 이름 기반으로 parent_id 매핑)
            child_specs: List[Tuple[str, str]] = [
                ('상의', '의류'), ('하의', '의류'), ('아우터', '의류'),
                ('운동화', '신발'), ('구두', '신발'),
                ('백팩', '가방'), ('크로스백', '가방'),
                ('목걸이', '액세서리'), ('팔찌', '액세서리'),
            ]
            for cname, pname in child_specs:
                parent_id = name_to_category_id.get(pname)
                if not parent_id:
                    continue
                existing = session.execute(
                    text("SELECT category_id FROM categories WHERE category_name = :name"),
                    {"name": cname}
                ).scalar()
                if not existing:
                    session.execute(
                        text("INSERT INTO categories (category_name, parent_id) VALUES (:name, :parent_id)"),
                        {"name": cname, "parent_id": parent_id}
                    )
                # 갱신된 child id 저장
                child_id = session.execute(
                    text("SELECT category_id FROM categories WHERE category_name = :name"),
                    {"name": cname}
                ).scalar()
                name_to_category_id[cname] = child_id

            # 2. 상품 데이터
            logger.info("📦 상품 데이터 입력...")
            products_by_category_name: List[Tuple[str, str, str, float, str]] = [
                ('상의', '기본 티셔츠', '편안하고 깔끔한 기본 티셔츠', 29000.0, 'https://picsum.photos/seed/1/400/600'),
                ('상의', '스트라이프 셔츠', '클래식한 스트라이프 패턴 셔츠', 45000.0, 'https://picsum.photos/seed/2/400/600'),
                ('상의', '폴로 셔츠', '캐주얼한 폴로 셔츠', 35000.0, 'https://picsum.photos/seed/3/400/600'),
                ('하의', '슬림 청바지', '슬림핏 청바지', 59000.0, 'https://picsum.photos/seed/4/400/600'),
                ('하의', '와이드 슬랙스', '편안한 와이드 슬랙스', 69000.0, 'https://picsum.photos/seed/5/400/600'),
                ('하의', '조거 팬츠', '운동용 조거 팬츠', 39000.0, 'https://picsum.photos/seed/6/400/600'),
                ('아우터', '후드 집업', '따뜻한 후드 집업', 79000.0, 'https://picsum.photos/seed/7/400/600'),
                ('아우터', '데님 재킷', '빈티지 데님 재킷', 89000.0, 'https://picsum.photos/seed/8/400/600'),
                ('운동화', '캐주얼 스니커즈', '일상용 캐주얼 스니커즈', 89000.0, 'https://picsum.photos/seed/9/400/600'),
                ('운동화', '러닝화', '운동용 러닝화', 129000.0, 'https://picsum.photos/seed/10/400/600'),
            ]
            product_name_to_id: dict = {}
            for cname, pname, desc, price, image_url in products_by_category_name:
                cid = name_to_category_id.get(cname)
                if not cid:
                    continue
                exists_pid = session.execute(
                    text("SELECT product_id FROM products WHERE product_name = :name"),
                    {"name": pname}
                ).scalar()
                if not exists_pid:
                    session.execute(
                        text("""
                            INSERT INTO products (category_id, product_name, description, price, image_url)
                            VALUES (:category_id, :product_name, :description, :price, :image_url)
                        """),
                        {
                            "category_id": cid,
                            "product_name": pname,
                            "description": desc,
                            "price": price,
                            "image_url": image_url,
                        }
                    )
                pid = session.execute(
                    text("SELECT product_id FROM products WHERE product_name = :name"),
                    {"name": pname}
                ).scalar()
                product_name_to_id[pname] = pid

            # 3. 상품 옵션 데이터
            logger.info("🎨 상품 옵션 데이터 입력...")
            variants_by_product_name: List[Tuple[str, str, str, int]] = [
                ('기본 티셔츠', 'white', 'S', 50), ('기본 티셔츠', 'white', 'M', 80), ('기본 티셔츠', 'white', 'L', 60),
                ('기본 티셔츠', 'black', 'S', 45), ('기본 티셔츠', 'black', 'M', 75), ('기본 티셔츠', 'black', 'L', 55),
                ('기본 티셔츠', 'gray', 'M', 40), ('기본 티셔츠', 'gray', 'L', 35),
                ('기본 티셔츠', 'blue', 'M', 20),
                ('기본 티셔츠', 'mint', 'S', 30),
                ('스트라이프 셔츠', 'navy', 'S', 30), ('스트라이프 셔츠', 'navy', 'M', 50), ('스트라이프 셔츠', 'navy', 'L', 40),
                ('스트라이프 셔츠', 'white', 'M', 25), ('스트라이프 셔츠', 'white', 'L', 30),
                ('폴로 셔츠', 'navy', 'M', 35), ('폴로 셔츠', 'navy', 'L', 40), ('폴로 셔츠', 'gray', 'M', 30),
                ('슬림 청바지', 'blue', '28', 25), ('슬림 청바지', 'blue', '30', 35), ('슬림 청바지', 'blue', '32', 30), ('슬림 청바지', 'blue', '34', 20),
                ('슬림 청바지', 'black', '30', 25), ('슬림 청바지', 'black', '32', 20),
                ('와이드 슬랙스', 'black', '28', 20), ('와이드 슬랙스', 'black', '30', 30), ('와이드 슬랙스', 'black', '32', 25),
                ('와이드 슬랙스', 'beige', '30', 15), ('와이드 슬랙스', 'beige', '32', 20),
                ('조거 팬츠', 'gray', 'M', 40), ('조거 팬츠', 'gray', 'L', 45), ('조거 팬츠', 'black', 'M', 35), ('조거 팬츠', 'black', 'L', 40),
                ('후드 집업', 'gray', 'M', 25), ('후드 집업', 'gray', 'L', 30), ('후드 집업', 'black', 'M', 20), ('후드 집업', 'black', 'L', 25),
                ('데님 재킷', 'indigo', 'M', 15), ('데님 재킷', 'indigo', 'L', 20), ('데님 재킷', 'lightblue', 'M', 10),
                ('캐주얼 스니커즈', 'white', '250', 30), ('캐주얼 스니커즈', 'white', '260', 40), ('캐주얼 스니커즈', 'white', '270', 35),
                ('캐주얼 스니커즈', 'black', '250', 25), ('캐주얼 스니커즈', 'black', '260', 30), ('캐주얼 스니커즈', 'black', '270', 25),
                ('러닝화', 'white', '250', 20), ('러닝화', 'white', '260', 25), ('러닝화', 'white', '270', 20),
                ('러닝화', 'red', '260', 15), ('러닝화', 'red', '270', 18),
            ]
            for pname, color, size, stock_quantity in variants_by_product_name:
                pid = product_name_to_id.get(pname)
                if not pid:
                    continue
                exists_vid = session.execute(
                    text("""
                        SELECT variant_id FROM product_variants
                        WHERE product_id = :pid AND color = :color AND size = :size
                    """),
                    {"pid": pid, "color": color, "size": size}
                ).scalar()
                if not exists_vid:
                    session.execute(
                        text("""
                            INSERT INTO product_variants (product_id, color, size, stock_quantity)
                            VALUES (:product_id, :color, :size, :stock_quantity)
                        """),
                        {
                            "product_id": pid,
                            "color": color,
                            "size": size,
                            "stock_quantity": stock_quantity,
                        }
                    )

            # 4. 테스트 사용자 데이터
            logger.info("👤 사용자 데이터 입력...")
            users: List[Tuple[str, str, str, str, str, str, str, str, str]] = [
                ('test1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxqC3G', '김테스트', 'male', '1990-05-15', '010-1111-1111', '12345', '서울시 강남구 테헤란로 123', '101호'),
                ('test2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxqC3G', '이유저', 'female', '1995-08-22', '010-2222-2222', '54321', '서울시 서초구 서초대로 456', '202호'),
                ('test3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxqC3G', '박고객', 'other', '1988-12-03', '010-3333-3333', '67890', '서울시 마포구 홍대로 789', '303호'),
            ]
            session.execute(
                text("""
                    INSERT INTO users (email, password_hash, user_name, gender, birthdate, phone_number, zip_code, address_main, address_detail)
                    VALUES (:email, :password_hash, :user_name, :gender, :birthdate, :phone_number, :zip_code, :address_main, :address_detail)
                """),
                [
                    {
                        "email": email,
                        "password_hash": password_hash,
                        "user_name": user_name,
                        "gender": gender,
                        "birthdate": birthdate,
                        "phone_number": phone_number,
                        "zip_code": zip_code,
                        "address_main": address_main,
                        "address_detail": address_detail,
                    }
                    for (email, password_hash, user_name, gender, birthdate, phone_number, zip_code, address_main, address_detail) in users
                ],
            )

            # 5. 사용자 관심사 데이터 (동적 매핑: 실제 user_id / category_id 조회)
            logger.info("❤️ 사용자 관심사 데이터 입력...")
            # 5-1) 사용자 ID 매핑 (email -> user_id)
            seed_user_emails = [u[0] for u in users]
            email_to_user_id = {}
            for email in seed_user_emails:
                user_id_val = session.execute(
                    text("SELECT user_id FROM users WHERE email = :email"),
                    {"email": email}
                ).scalar()
                if user_id_val:
                    email_to_user_id[email] = user_id_val

            # 5-2) 카테고리 ID 매핑 (category_name -> category_id)
            interest_category_names = ["상의", "하의", "운동화", "아우터", "크로스백", "목걸이"]
            name_to_category_id = {}
            for cname in interest_category_names:
                cid = session.execute(
                    text("SELECT category_id FROM categories WHERE category_name = :name"),
                    {"name": cname}
                ).scalar()
                if cid:
                    name_to_category_id[cname] = cid

            # 5-3) 관심사 관계 구성 (이메일/이름 기반)
            interest_plan = [
                ("test1@example.com", ["상의", "하의", "운동화"]),
                ("test2@example.com", ["상의", "아우터", "크로스백"]),
                ("test3@example.com", ["하의", "운동화", "목걸이"]),
            ]

            interest_rows = []
            for email, category_names in interest_plan:
                uid = email_to_user_id.get(email)
                if not uid:
                    continue
                for cname in category_names:
                    cid = name_to_category_id.get(cname)
                    if cid:
                        interest_rows.append({"user_id": uid, "category_id": cid})

            if interest_rows:
                session.execute(
                    text("INSERT INTO user_interests (user_id, category_id) VALUES (:user_id, :category_id)"),
                    interest_rows,
                )

            # 6. 장바구니 데이터
            logger.info("🛒 장바구니 데이터 입력...")
            # 사용자 이메일 → user_id
            email_to_user_id = {}
            for email in [u[0] for u in users]:
                uid = session.execute(text("SELECT user_id FROM users WHERE email = :email"), {"email": email}).scalar()
                if uid:
                    email_to_user_id[email] = uid

            # 장바구니 항목: (email, product_name, color, size, qty)
            cart_specs: List[Tuple[str, str, str, str, int]] = [
                ('test1@example.com', '기본 티셔츠', 'white', 'S', 2),
                ('test1@example.com', '슬림 청바지', 'blue', '28', 1),
                ('test2@example.com', '기본 티셔츠', 'white', 'L', 1),
                ('test2@example.com', '후드 집업', 'gray', 'M', 1),
                ('test3@example.com', '슬림 청바지', 'blue', '32', 1),
            ]
            for email, pname, color, size, qty in cart_specs:
                uid = email_to_user_id.get(email)
                pid = product_name_to_id.get(pname)
                if not uid or not pid:
                    continue
                vid = session.execute(
                    text("""
                        SELECT variant_id FROM product_variants
                        WHERE product_id = :pid AND color = :color AND size = :size
                    """),
                    {"pid": pid, "color": color, "size": size}
                ).scalar()
                if vid:
                    session.execute(
                        text("INSERT INTO cart_items (user_id, variant_id, quantity) VALUES (:user_id, :variant_id, :quantity)"),
                        {"user_id": uid, "variant_id": vid, "quantity": qty}
                    )

            # 커밋 및 집계 출력
            session.commit()

            counts = {}
            for table in ["categories", "products", "product_variants", "users", "cart_items", "user_interests"]:
                counts[table] = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()

            logger.info("✅ 더미데이터 입력 완료!")
            logger.info("📊 생성된 데이터:")
            logger.info(f"   - 카테고리: {counts['categories']}개")
            logger.info(f"   - 상품: {counts['products']}개")
            logger.info(f"   - 상품옵션: {counts['product_variants']}개")
            logger.info(f"   - 사용자: {counts['users']}개")
            logger.info(f"   - 장바구니: {counts['cart_items']}개")
            logger.info(f"   - 관심사: {counts['user_interests']}개")
            logger.info("🔐 테스트 계정 비밀번호: password123")

        except Exception as e:
            logger.error(f"❌ 더미데이터 입력 실패: {e}")
            session.rollback()
            raise


if __name__ == "__main__":
    insert_dummy_data()