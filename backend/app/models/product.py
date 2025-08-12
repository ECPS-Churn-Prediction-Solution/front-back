"""
상품 관련 모델
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

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
    price = Column(Float, nullable=False, comment="상품 가격")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="상품 등록일")
    
    # 관계 설정
    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base):
    """
    상품 옵션 테이블
    색상, 사이즈별 재고 관리
    """
    __tablename__ = "product_variants"

    variant_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="옵션 고유 번호")
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, comment="상품 ID")
    color = Column(String(50), nullable=True, comment="색상")
    size = Column(String(50), nullable=True, comment="사이즈")
    stock_quantity = Column(Integer, nullable=False, default=0, comment="재고 수량")

    # 관계 설정
    product = relationship("Product", back_populates="variants")
    order_items = relationship("OrderItem", back_populates="variant")
    cart_items = relationship("CartItem", back_populates="variant")
