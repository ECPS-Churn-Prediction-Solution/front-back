"""
장바구니 관련 모델
"""

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class CartItem(Base):
    """
    장바구니 항목 테이블
    사용자가 구매를 위해 임시로 담아둔 상품 목록
    """
    __tablename__ = "cart_items"

    cart_item_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="장바구니 항목 고유 번호")
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment="어떤 고객의 장바구니인지")
    variant_id = Column(Integer, ForeignKey("product_variants.variant_id"), nullable=False, comment="상품 옵션 ID (색상/사이즈)")
    quantity = Column(Integer, nullable=False, default=1, comment="담은 수량")
    added_at = Column(TIMESTAMP, server_default=func.now(), comment="장바구니에 추가한 시점")

    # 관계 설정
    user = relationship("User", back_populates="cart_items")
    variant = relationship("ProductVariant", back_populates="cart_items")
