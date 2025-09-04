"""
Pydantic 스키마 정의
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

# === 카테고리 스키마 ===

class CategoryResponse(BaseModel):
    """
    카테고리 응답 스키마
    """
    category_id: int = Field(..., description="카테고리 ID")
    category_name: str = Field(..., description="카테고리명")
    parent_id: Optional[int] = Field(None, description="상위 카테고리 ID (최상위면 null)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "category_id": 1,
                "category_name": "상의",
                "parent_id": None
            }
        }

class PaymentMethod(str, Enum):
    """
    결제 방식 선택
    """
    CREDIT_CARD = "credit_card"
    CASH = "cash"

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
    ERD에 따라 variant_id를 사용
    """
    variant_id: int = Field(..., description="상품 옵션 ID (variant_id)")
    quantity: int = Field(default=1, ge=1, description="수량 (최소 1개)")

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
    variant_id: int = Field(..., description="상품 옵션 ID")
    product_id: int = Field(..., description="상품 ID")
    product_name: str = Field(..., description="상품명")
    image_url: Optional[str] = Field(None, description="상품 이미지 URL")
    color: Optional[str] = Field(None, description="색상")
    size: Optional[str] = Field(None, description="사이즈")
    price: float = Field(..., description="상품 가격")
    quantity: int = Field(..., description="수량")
    total_price: float = Field(..., description="항목 총 가격")
    added_at: datetime = Field(..., description="장바구니 추가일")

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    """
    장바구니 전체 응답 스키마
    """
    items: List[CartItemResponse] = Field(default=[], description="장바구니 상품 목록")
    total_items: int = Field(..., description="총 상품 종류 수")
    total_amount: float = Field(..., description="총 금액")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "cart_item_id": 1,
                        "variant_id": 1,
                        "product_id": 1,
                        "product_name": "티셔츠",
                        "price": 25000.0,
                        "quantity": 2,
                        "total_price": 50000.0,
                        "added_at": "2024-01-01T10:00:00"
                    }
                ],
                "total_items": 1,
                "total_amount": 50000.0
            }
        }


class ShippingAddress(BaseModel):
    """
    배송 주소 스키마
    """
    zip_code: str = Field(..., description="우편번호")
    address_main: str = Field(..., description="기본 주소")
    address_detail: str = Field(..., description="상세 주소")

    class Config:
        json_schema_extra = {
            "example": {
                "zip_code": "06134",
                "address_main": "서울특별시 강남구 테헤란로 123",
                "address_detail": "45층 101호"
            }
        }

class OrderCreateRequest(BaseModel):
    """
    주문 생성 요청 스키마
    장바구니 정보를 바탕으로 주문 생성
    """
    recipient_name: str = Field(..., description="수령인 이름")
    shipping_address: ShippingAddress = Field(..., description="배송 주소")
    phone_number: str = Field(..., description="연락처")
    shopping_memo: str = Field(default="", description="배송 메모")
    payment_method: PaymentMethod = Field(..., description="결제 방법 (credit_card 또는 cash)")
    used_coupon_code: str = Field(default="", description="사용한 쿠폰 코드")
    shipping_method: str = Field(default="standard", description="배송 방법 (standard | express)")
    shipping_fee: float = Field(default=3000.0, description="배송비")

    class Config:
        json_schema_extra = {
            "example": {
                "recipient_name": "김민준",
                "shipping_address": {
                    "zip_code": "06134",
                    "address_main": "서울특별시 강남구 테헤란로 123",
                    "address_detail": "45층 101호"
                },
                "phone_number": "010-1234-5678",
                "shopping_memo": "부재 시 경비실에 맡겨주세요.",
                "payment_method": "credit_card",
                "used_coupon_code": "SUMMER_SALE_20"
            }
        }

class OrderItemResponse(BaseModel):
    """
    주문 상품 응답 스키마
    ERD에 따라 variant_id를 사용
    """
    order_item_id: int = Field(..., description="주문 항목 ID")
    variant_id: int = Field(..., description="상품 옵션 ID")
    product_id: int = Field(..., description="상품 ID")
    product_name: str = Field(..., description="상품명")
    quantity: int = Field(..., description="주문 수량")
    price_per_item: float = Field(..., description="구매 당시 개당 가격")
    total_price: float = Field(..., description="항목 총 가격")

# === 상품 관련 스키마 ===

class ProductVariantResponse(BaseModel):
    """
    상품 옵션 응답 스키마
    """
    variant_id: int = Field(..., description="옵션 고유 ID")
    color: str = Field(..., description="색상")
    size: str = Field(..., description="사이즈")
    stock_quantity: int = Field(..., description="재고 수량")

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    """
    상품 목록 응답 스키마
    """
    product_id: int = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품명")
    description: Optional[str] = Field(None, description="상품 설명")
    image_url: Optional[str] = Field(None, description="상품 이미지 URL")
    price: float = Field(..., description="상품 가격")
    category_name: str = Field(..., description="카테고리명")
    created_at: datetime = Field(..., description="상품 등록일")
    available_variants: int = Field(..., description="사용 가능한 옵션 수")


    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """
    주문 응답 스키마
    """
    order_id: int = Field(..., description="주문 ID")
    user_id: int = Field(..., description="주문한 사용자 ID")
    order_date: datetime = Field(..., description="주문 일시")
    total_amount: float = Field(..., description="주문 총액")
    shipping_fee: float = Field(..., description="배송비")
    status: str = Field(..., description="주문 상태")
    shopping_address: str = Field(..., description="배송 주소")
    items: List[OrderItemResponse] = Field(default=[], description="주문 상품 목록")

class ProductDetailResponse(BaseModel):
    """
    상품 상세 응답 스키마
    """
    product_id: int = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품명")
    description: Optional[str] = Field(None, description="상품 설명")
    image_url: Optional[str] = Field(None, description="상품 이미지 URL")
    price: float = Field(..., description="상품 가격")
    category_name: str = Field(..., description="카테고리명")
    created_at: datetime = Field(..., description="상품 등록일")
    variants: List[ProductVariantResponse] = Field(..., description="상품 옵션 목록")

    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    """
    주문 목록 응답 스키마
    """
    orders: List[OrderResponse] = Field(default=[], description="주문 목록")
    total_orders: int = Field(..., description="총 주문 수")

    class Config:
        json_schema_extra = {
            "example": {
                "orders": [
                    {
                        "order_id": 1,
                        "user_id": 1,
                        "order_date": "2025-08-07T15:00:00",
                        "total_amount": 139000.0,
                        "status": "pending",
                        "shopping_address": "서울시 강남구 테헤란로 123, 456호",
                        "items": []
                    }
                ],
                "total_orders": 1
            }
        }

class DirectOrderRequest(BaseModel):
    """
    즉시 주문 생성 요청 스키마
    장바구니를 거치지 않고 바로 주문
    """
    variant_id: int = Field(..., description="주문할 상품 옵션 ID")
    quantity: int = Field(..., ge=1, description="주문 수량 (최소 1개)")
    recipient_name: str = Field(..., description="수령인 이름")
    shipping_address: ShippingAddress = Field(..., description="배송 주소")
    phone_number: str = Field(..., description="연락처")
    shopping_memo: str = Field(default="", description="배송 메모")
    payment_method: PaymentMethod = Field(..., description="결제 방법 (credit_card 또는 cash)")
    used_coupon_code: str = Field(default="", description="사용한 쿠폰 코드")
    shipping_method: str = Field(default="standard", description="배송 방법 (standard | express)")
    shipping_fee: float = Field(default=3000.0, description="배송비")

    class Config:
        json_schema_extra = {
            "example": {
                "variant_id": 1,
                "quantity": 2,
                "recipient_name": "김민준",
                "shipping_address": {
                    "zip_code": "06134",
                    "address_main": "서울특별시 강남구 테헤란로 123",
                    "address_detail": "45층 101호"
                },
                "phone_number": "010-1234-5678",
                "shopping_memo": "부재 시 경비실에 맡겨주세요.",
                "payment_method": "credit_card",
                "used_coupon_code": "SUMMER_SALE_20"
            }
        }


class OrderSuccessResponse(BaseModel):
    """
    주문 성공 응답 스키마
    주문 ID, 날짜, 상태, 총액, 메시지 포함
    """
    order_id: int = Field(..., description="주문 ID")
    order_date: datetime = Field(..., description="주문 일시")
    status: str = Field(..., description="주문 상태")
    total_amount: float = Field(..., description="주문 총액")
    shipping_fee: float = Field(..., description="배송비")
    message: str = Field(..., description="주문 성공 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": 1205,
                "order_date": "2025-08-12T11:51:43Z",
                "status": "paid",
                "total_amount": 158000.0,
                "message": "주문이 성공적으로 완료되었습니다."
            }
        }

# === 대시보드 관련 스키마 ===

class ChurnRateOverallResponse(BaseModel):
    """
    전체 Churn Rate 지표 응답 스키마
    """
    reportDt: date
    horizonDays: int
    customersTotal: int
    churnRate: float
    retentionRate: float
    churnCustomers: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "reportDt": "2025-08-29",
                "horizonDays": 30,
                "customersTotal": 120345,
                "churnRate": 0.1325,
                "retentionRate": 0.8675,
                "churnCustomers": 15966
            }
        }

class ChurnRateRFMSegment(BaseModel):
    """
    RFM 그룹별 Churn Rate 세그먼트
    """
    bucket: str
    customers: int
    churnRate: float
    atRiskUsers: int

class ChurnRateRFMResponse(BaseModel):
    """
    RFM 그룹별 Churn Rate 지표 응답 스키마
    """
    reportDt: date
    horizonDays: int
    segments: List[ChurnRateRFMSegment]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "reportDt": "2025-08-29",
                "horizonDays": 30,
                "segments": [
                    {"bucket": "High(10-12)", "customers": 12000, "churnRate": 0.1825, "atRiskUsers": 2190},
                    {"bucket": "Mid(7-9)", "customers": 34000, "churnRate": 0.1120, "atRiskUsers": 3808},
                    {"bucket": "Low(3-6)", "customers": 56000, "churnRate": 0.0835, "atRiskUsers": 4676}
                ]
            }
        }

class ChurnRiskBand(BaseModel):
    """
    위험 밴드별 고객 분포
    """
    riskBand: str
    userCount: int
    ratio: float

class ChurnRiskAtRisk(BaseModel):
    """
    이탈 위험 고객 요약
    """
    userCount: int
    ratio: float

class ChurnRiskDistributionResponse(BaseModel):
    """
    위험 밴드별 고객 수 및 비중 응답 스키마
    """
    reportDt: date
    horizonDays: int
    bands: List[ChurnRiskBand]
    atRisk: ChurnRiskAtRisk

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "reportDt": "2025-08-29",
                "horizonDays": 30,
                "bands": [
                    {"riskBand": "VH", "userCount": 8200, "ratio": 0.0681},
                    {"riskBand": "H", "userCount": 10250, "ratio": 0.0851}
                ],
                "atRisk": {"userCount": 18450, "ratio": 0.1532}
            }
        }

class HighRiskUserAction(BaseModel):
    """
    고위험 고객에 대한 추천 액션
    """
    policyId: int
    policy_name: str

class HighRiskUser(BaseModel):
    """
    고위험 고객 상세 정보
    """
    userId: int
    riskBand: str
    churnProbability: float
    action: HighRiskUserAction

class HighRiskUserListResponse(BaseModel):
    """
    고위험 고객 리스트 응답 스키마
    """
    reportDt: date
    horizonDays: int
    total: int
    items: List[HighRiskUser]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "reportDt": "2025-08-29",
                "horizonDays": 30,
                "total": 18450,
                "items": [
                    {
                        "userId": 100023,
                        "riskBand": "VH",
                        "churnProbability": 0.9123,
                        "action": {"policyId": 3, "policy_name": "50% 쿠폰제공"}
                    }
                ]
            }
        }

class PolicyActionRequest(BaseModel):
    """정책 승인/거절 요청 스키마"""
    userId: int
    policyId: int
    action: str  # "approve" or "reject"
    reason: Optional[str] = None

class PolicyActionResponse(BaseModel):
    """정책 승인/거절 응답 스키마"""
    userId: int
    policyId: int
    policyName: str
    status: str
