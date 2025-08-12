"""
장바구니 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# === 요청 스키마 ===

class CartItemAdd(BaseModel):
    """
    장바구니 상품 추가 요청 스키마
    """
    variant_id: int = Field(..., description="상품 옵션 ID")
    quantity: int = Field(..., ge=1, description="수량 (1개 이상)")

    class Config:
        json_schema_extra = {
            "example": {
                "variant_id": 1,
                "quantity": 2
            }
        }

class CartItemUpdate(BaseModel):
    """
    장바구니 상품 수량 변경 요청 스키마
    """
    quantity: int = Field(..., ge=1, description="새로운 수량 (1개 이상)")

    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 3
            }
        }

# === 응답 스키마 ===

class CartItemResponse(BaseModel):
    """
    장바구니 아이템 응답 스키마
    """
    cart_item_id: int = Field(..., description="장바구니 아이템 ID")
    variant_id: int = Field(..., description="상품 옵션 ID")
    product_id: int = Field(..., description="상품 ID")
    product_name: str = Field(..., description="상품명")
    color: str = Field(..., description="색상")
    size: str = Field(..., description="사이즈")
    price: float = Field(..., description="개당 가격")
    quantity: int = Field(..., description="수량")
    total_price: float = Field(..., description="총 가격 (개당 가격 × 수량)")
    added_at: datetime = Field(..., description="장바구니 추가 일시")

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    """
    장바구니 전체 응답 스키마
    """
    items: List[CartItemResponse] = Field(..., description="장바구니 아이템 목록")
    total_items: int = Field(..., description="총 아이템 종류 수")
    total_quantity: int = Field(..., description="총 수량")
    total_amount: float = Field(..., description="총 금액")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "cart_item_id": 1,
                        "variant_id": 1,
                        "product_id": 1,
                        "product_name": "기본 면 티셔츠",
                        "color": "화이트",
                        "size": "M",
                        "price": 25000,
                        "quantity": 2,
                        "total_price": 50000,
                        "added_at": "2025-08-12T15:00:00"
                    }
                ],
                "total_items": 1,
                "total_quantity": 2,
                "total_amount": 50000
            }
        }
