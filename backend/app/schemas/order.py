"""
주문 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class PaymentMethod(str, Enum):
    """결제 방식 선택"""
    CREDIT_CARD = "credit_card"
    CASH = "cash"

class DeliveryStatusEnum(str, Enum):
    """배송 상태"""
    preparing = "상품 준비중"
    shipping = "상품 배송중"
    delivered = "상품 배송완료"

# === 요청 스키마 ===

class ShippingAddress(BaseModel):
    """배송 주소 스키마"""
    zip_code: str = Field(..., description="우편번호")
    address_main: str = Field(..., description="기본 주소")
    address_detail: str = Field(..., description="상세 주소")

class OrderCreateRequest(BaseModel):
    """
    장바구니에서 주문 생성 요청 스키마
    """
    recipient_name: str = Field(..., description="수령인 이름")
    phone_number: str = Field(..., description="연락처")
    shipping_address: ShippingAddress = Field(..., description="배송 주소")
    shopping_memo: Optional[str] = Field(None, description="배송 메모")
    payment_method: PaymentMethod = Field(..., description="결제 방법")
    used_coupon_code: Optional[str] = Field(None, description="사용한 쿠폰 코드")

class DirectOrderRequest(BaseModel):
    """
    즉시 주문 생성 요청 스키마 (장바구니 거치지 않음)
    """
    variant_id: int = Field(..., description="상품 옵션 ID")
    quantity: int = Field(..., ge=1, description="주문 수량")
    recipient_name: str = Field(..., description="수령인 이름")
    phone_number: str = Field(..., description="연락처")
    shipping_address: ShippingAddress = Field(..., description="배송 주소")
    shopping_memo: Optional[str] = Field(None, description="배송 메모")
    payment_method: PaymentMethod = Field(..., description="결제 방법")
    used_coupon_code: Optional[str] = Field(None, description="사용한 쿠폰 코드")

# === 응답 스키마 ===

class OrderItemResponse(BaseModel):
    """
    주문 상품 응답 스키마
    """
    order_item_id: int = Field(..., description="주문 상품 ID")
    variant_id: int = Field(..., description="상품 옵션 ID")
    product_name: str = Field(..., description="상품명")
    color: str = Field(..., description="색상")
    size: str = Field(..., description="사이즈")
    quantity: int = Field(..., description="주문 수량")
    price_per_item: float = Field(..., description="개당 가격")
    total_price: float = Field(..., description="총 가격")

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    """
    주문 상세 응답 스키마
    """
    order_id: int = Field(..., description="주문 ID")
    order_date: datetime = Field(..., description="주문 일시")
    total_amount: float = Field(..., description="주문 총액")
    status: DeliveryStatusEnum = Field(..., description="배송 상태")
    recipient_name: str = Field(..., description="수령인 이름")
    phone_number: str = Field(..., description="연락처")
    shipping_address: str = Field(..., description="배송 주소")
    shopping_memo: Optional[str] = Field(None, description="배송 메모")
    payment_method: PaymentMethod = Field(..., description="결제 방법")
    items: List[OrderItemResponse] = Field(..., description="주문 상품 목록")

    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    """
    주문 목록 응답 스키마
    """
    orders: List[OrderResponse] = Field(..., description="주문 목록")
    total_count: int = Field(..., description="총 주문 수")

class OrderSuccessResponse(BaseModel):
    """
    주문 성공 응답 스키마
    """
    message: str = Field(..., description="성공 메시지")
    order_id: int = Field(..., description="생성된 주문 ID")
    total_amount: float = Field(..., description="주문 총액")
