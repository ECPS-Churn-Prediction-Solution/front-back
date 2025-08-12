"""
주문 관련 모델
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

# 배송 상태 Enum 정의
class DeliveryStatusEnum(enum.Enum):
    """배송 상태를 나타내는 Enum"""
    preparing = "상품 준비중"
    shipping = "상품 배송중"
    delivered = "상품 배송완료"

class Order(Base):
    """
    주문 마스터 테이블
    고객의 주문 마스터 정보를 저장
    """
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="주문 고유 번호")
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment="주문한 고객 ID")
    order_date = Column(TIMESTAMP, server_default=func.now(), comment="주문 일시")
    total_amount = Column(Float, nullable=False, comment="주문 총액")
    status = Column(Enum(DeliveryStatusEnum), default=DeliveryStatusEnum.preparing, comment="주문 상태")
    shipping_address = Column(String(255), nullable=True, comment="배송 주소")
    shipping_memo = Column(Text(300), nullable=True, comment="배송 메모")
    used_coupon_code = Column(String(50), nullable=True, comment="사용한 쿠폰 코드")
    payment_method = Column(String(50), nullable=True, comment="결제 방법")
    
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
    variant_id = Column(Integer, ForeignKey("product_variants.variant_id"), nullable=False, comment="주문된 상품 옵션 번호")
    quantity = Column(Integer, nullable=False, default=1, comment="주문 수량")
    price_per_item = Column(Float, nullable=False, comment="구매 당시 개당 가격")

    # 관계 설정
    order = relationship("Order", back_populates="order_items")
    variant = relationship("ProductVariant", back_populates="order_items")
