"""
데이터베이스 모델 정의
ERD 기반으로 SQLAlchemy 모델 생성
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Enum, ForeignKey, DECIMAL, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

# 성별 Enum 정의
class GenderEnum(enum.Enum):
    """사용자 성별을 나타내는 Enum"""
    male = "male"
    female = "female"
    other = "other"

class User(Base):
    """
    사용자 테이블
    고객의 기본 정보와 로그인 정보를 저장
    """
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="고객 고유 번호")
    email = Column(String(255), unique=True, nullable=False, index=True, comment="로그인 이메일")
    password_hash = Column(String(255), nullable=False, comment="해시 처리된 비밀번호")
    user_name = Column(String(50), nullable=False, comment="고객 이름")
    gender = Column(Enum(GenderEnum), nullable=True, comment="성별")
    birthdate = Column(Date, nullable=False, comment="생년월일")
    phone_number = Column(String(20), nullable=True, comment="전화번호")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="가입일")
    
    # 관계 설정
    interests = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    """
    카테고리 테이블
    상품의 종류를 나누는 기준이자, 고객의 관심 분야 목록
    """
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="카테고리 고유 번호")
    category_name = Column(String(100), unique=True, nullable=False, comment="카테고리명")
    parent_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True, comment="상위 카테고리 ID")
    
    # 관계 설정
    interests = relationship("UserInterest", back_populates="category")
    products = relationship("Product", back_populates="category")
    # 자기 참조 관계
    children = relationship("Category", backref="parent", remote_side=[category_id])

class UserInterest(Base):
    """
    사용자-관심사 연결 테이블
    고객과 관심사를 연결하는 Many-to-Many 브릿지 테이블
    """
    __tablename__ = "user_interests"
    
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, comment="고객 ID")
    category_id = Column(Integer, ForeignKey("categories.category_id"), primary_key=True, comment="관심 카테고리 ID")
    
    # 관계 설정
    user = relationship("User", back_populates="interests")
    category = relationship("Category", back_populates="interests")

class Product(Base):
    """
    상품 정보 테이블
    판매하는 개별 의류 상품 정보를 저장
    """
    __tablename__ = "products"
    
    product_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="상품 고유 번호")
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False, comment="상품이 속한 카테고리")
    product_name = Column(String(255), nullable=False, comment="상품명")
    description = Column(Text, nullable=True, comment="상품 설명")
    price = Column(Integer, nullable=False, comment="상품 가격")
    stock_quantity = Column(Integer, nullable=False, default=0, comment="재고 수량")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="상품 등록일")
    
    # 관계 설정
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")

class Order(Base):
    """
    주문 마스터 테이블
    고객의 주문 마스터 정보를 저장
    """
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="주문 고유 번호")
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment="주문한 고객 ID")
    order_date = Column(TIMESTAMP, server_default=func.now(), comment="주문 일시")
    total_amount = Column(Integer, nullable=False, comment="주문 총액")
    status = Column(String(50), default="pending", comment="주문 상태")

    # 배송 정보
    recipient_name = Column(String(100), nullable=False, comment="수령인 이름")
    zip_code = Column(String(10), nullable=False, comment="우편번호")
    address_main = Column(String(255), nullable=False, comment="기본 주소")
    address_detail = Column(String(255), nullable=True, comment="상세 주소")
    phone_number = Column(String(20), nullable=False, comment="연락처")
    shopping_memo = Column(Text, nullable=True, comment="배송 메모")
    payment_method = Column(String(50), nullable=False, comment="결제 방법")
    used_coupon_code = Column(String(50), nullable=True, comment="사용한 쿠폰 코드")
    
    # 관계 설정
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    """
    주문 상세 항목 테이블
    한 주문에 어떤 상품이 몇 개 포함되었는지 저장
    """
    __tablename__ = "order_items"
    
    order_item_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="주문 항목 고유 번호")
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, comment="주문 번호")
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, comment="주문된 상품 번호")
    quantity = Column(Integer, nullable=False, default=1, comment="주문 수량")
    price_per_item = Column(Integer, nullable=False, comment="구매 당시 개당 가격")
    
    # 관계 설정
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

class CartItem(Base):
    """
    장바구니 항목 테이블
    사용자가 구매를 위해 임시로 담아둔 상품 목록
    """
    __tablename__ = "cart_items"

    cart_item_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="장바구니 항목 고유 번호")
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment="어떤 고객의 장바구니인지")
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, comment="장바구니에 담은 상품")
    quantity = Column(Integer, nullable=False, default=1, comment="담은 수량")
    added_at = Column(TIMESTAMP, server_default=func.now(), comment="장바구니에 추가한 시점")

    # 관계 설정
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")