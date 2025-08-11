"""
Pydantic 스키마 정의
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class GenderEnum(str, Enum):
    """성별 Enum"""
    male = "male"
    female = "female"
    other = "other"

# === 요청 스키마 ===

class UserRegisterRequest(BaseModel):
    """
    회원가입 요청 스키마
    신규 고객 정보와 관심사를 받는 데이터 모델
    """
    email: EmailStr = Field(..., description="사용자 이메일 (로그인 ID)")
    password: str = Field(..., min_length=6, max_length=100, description="비밀번호 (최소 6자)")
    user_name: str = Field(..., min_length=1, max_length=50, description="사용자 이름")
    gender: Optional[GenderEnum] = Field(None, description="성별 (선택사항)")
    birthdate: date = Field(..., description="생년월일 (YYYY-MM-DD)")
    phone_number: Optional[str] = Field(None, max_length=20, description="전화번호 (선택사항)")
    interest_categories: List[int] = Field(default=[], description="관심 카테고리 ID 리스트")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123",
                "user_name": "홍길동",
                "gender": "male",
                "birthdate": "1990-01-01",
                "phone_number": "010-1234-5678",
                "interest_categories": [1, 2, 3]
            }
        }

class UserLoginRequest(BaseModel):
    """
    로그인 요청 스키마
    이메일과 비밀번호를 받는 데이터 모델
    """
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., description="비밀번호")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }

# === 응답 스키마 ===

class UserResponse(BaseModel):
    """
    사용자 정보 응답 스키마
    비밀번호를 제외한 사용자 정보 반환
    """
    user_id: int = Field(..., description="사용자 고유 ID")
    email: str = Field(..., description="사용자 이메일")
    user_name: str = Field(..., description="사용자 이름")
    gender: Optional[GenderEnum] = Field(None, description="성별")
    birthdate: date = Field(..., description="생년월일")
    phone_number: Optional[str] = Field(None, description="전화번호")
    created_at: datetime = Field(..., description="가입일시")

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """
    로그인 응답 스키마
    로그인 성공 시 사용자 정보 반환
    """
    message: str = Field(default="로그인 성공", description="로그인 결과 메시지")
    user: UserResponse = Field(..., description="사용자 정보")

class MessageResponse(BaseModel):
    """
    일반 메시지 응답 스키마
    성공/실패 메시지 반환
    """
    message: str = Field(..., description="응답 메시지")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "작업이 성공적으로 완료되었습니다."
            }
        }

# === 장바구니 관련 스키마 ===

class CartItemAdd(BaseModel):
    """
    장바구니 상품 추가 요청 스키마
    특정 옵션의 상품을 장바구니에 추가
    """
    product_id: int = Field(..., description="상품 ID (variant_id)")
    quantity: int = Field(default=1, ge=1, description="수량 (최소 1개)")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "quantity": 2
            }
        }

class CartItemUpdate(BaseModel):
    """
    장바구니 상품 수량 변경 요청 스키마
    """
    quantity: int = Field(..., ge=1, description="변경할 수량 (최소 1개)")

    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 3
            }
        }

class CartItemResponse(BaseModel):
    """
    장바구니 상품 응답 스키마
    """
    cart_item_id: int = Field(..., description="장바구니 항목 ID")
    product_id: int = Field(..., description="상품 ID")
    product_name: str = Field(..., description="상품명")
    price: Decimal = Field(..., description="상품 가격")
    quantity: int = Field(..., description="수량")
    total_price: Decimal = Field(..., description="항목 총 가격")
    added_at: datetime = Field(..., description="장바구니 추가일")

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    """
    장바구니 전체 응답 스키마
    """
    items: List[CartItemResponse] = Field(default=[], description="장바구니 상품 목록")
    total_items: int = Field(..., description="총 상품 종류 수")
    total_amount: Decimal = Field(..., description="총 금액")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "cart_item_id": 1,
                        "product_id": 1,
                        "product_name": "티셔츠",
                        "price": 25000,
                        "quantity": 2,
                        "total_price": 50000,
                        "added_at": "2024-01-01T10:00:00"
                    }
                ],
                "total_items": 1,
                "total_amount": 50000
            }
        }

# === 상품 관련 스키마 ===

class ProductVariantResponse(BaseModel):
    """
    상품 옵션 응답 스키마
    """
    variant_id: int = Field(..., description="옵션 고유 ID")
    color: str = Field(..., description="색상")
    size: str = Field(..., description="사이즈")
    stock_quantity: int = Field(..., description="재고 수량")
    price_adjustment: Decimal = Field(..., description="가격 조정")
    final_price: Decimal = Field(..., description="최종 가격 (기본가 + 조정가)")

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    """
    상품 목록 응답 스키마
    """
    product_id: int = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품명")
    description: Optional[str] = Field(None, description="상품 설명")
    price: Decimal = Field(..., description="상품 가격")
    category_name: str = Field(..., description="카테고리명")
    created_at: datetime = Field(..., description="상품 등록일")
    available_variants: int = Field(..., description="사용 가능한 옵션 수")

    class Config:
        from_attributes = True

class ProductDetailResponse(BaseModel):
    """
    상품 상세 응답 스키마
    """
    product_id: int = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품명")
    description: Optional[str] = Field(None, description="상품 설명")
    price: Decimal = Field(..., description="상품 가격")
    category_name: str = Field(..., description="카테고리명")
    created_at: datetime = Field(..., description="상품 등록일")
    variants: List[ProductVariantResponse] = Field(..., description="상품 옵션 목록")

    class Config:
        from_attributes = True



class ProductListPaginatedResponse(BaseModel):
    """
    페이지네이션된 상품 목록 응답 스키마
    """
    products: List[ProductListResponse] = Field(..., description="상품 목록")
    total_count: int = Field(..., description="전체 상품 수")
    total_pages: int = Field(..., description="전체 페이지 수")
    current_page: int = Field(..., description="현재 페이지 번호")
    page_size: int = Field(..., description="페이지당 상품 수")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_prev: bool = Field(..., description="이전 페이지 존재 여부")

    class Config:
        from_attributes = True