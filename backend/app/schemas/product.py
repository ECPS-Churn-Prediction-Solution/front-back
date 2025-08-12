"""
상품 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# === 응답 스키마 ===

class ProductVariantResponse(BaseModel):
    """
    상품 옵션 응답 스키마
    """
    variant_id: int = Field(..., description="상품 옵션 ID")
    color: str = Field(..., description="색상")
    size: str = Field(..., description="사이즈")
    stock_quantity: int = Field(..., description="재고 수량")
    price_adjustment: float = Field(..., description="가격 조정")
    final_price: float = Field(..., description="최종 가격")

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    """
    상품 목록 응답 스키마 (간단한 정보)
    """
    product_id: int = Field(..., description="상품 ID")
    product_name: str = Field(..., description="상품명")
    description: str = Field(..., description="상품 설명")
    price: float = Field(..., description="기본 가격")
    category_name: str = Field(..., description="카테고리명")
    created_at: datetime = Field(..., description="등록일시")
    available_variants: int = Field(..., description="사용 가능한 옵션 수")

    class Config:
        from_attributes = True

class ProductDetailResponse(BaseModel):
    """
    상품 상세 응답 스키마 (옵션 포함)
    """
    product_id: int = Field(..., description="상품 ID")
    product_name: str = Field(..., description="상품명")
    description: str = Field(..., description="상품 설명")
    price: float = Field(..., description="기본 가격")
    category_name: str = Field(..., description="카테고리명")
    created_at: datetime = Field(..., description="등록일시")
    variants: List[ProductVariantResponse] = Field(..., description="상품 옵션 목록")

    class Config:
        from_attributes = True

class ProductListPaginatedResponse(BaseModel):
    """
    상품 목록 페이지네이션 응답 스키마
    """
    products: List[ProductListResponse] = Field(..., description="상품 목록")
    total_count: int = Field(..., description="전체 상품 수")
    total_pages: int = Field(..., description="전체 페이지 수")
    current_page: int = Field(..., description="현재 페이지")
    page_size: int = Field(..., description="페이지 크기")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_prev: bool = Field(..., description="이전 페이지 존재 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "product_id": 1,
                        "product_name": "기본 면 티셔츠",
                        "description": "편안한 착용감의 기본 면 티셔츠입니다.",
                        "price": 25000,
                        "category_name": "티셔츠",
                        "created_at": "2025-08-12T15:00:00",
                        "available_variants": 5
                    }
                ],
                "total_count": 10,
                "total_pages": 1,
                "current_page": 1,
                "page_size": 20,
                "has_next": False,
                "has_prev": False
            }
        }
