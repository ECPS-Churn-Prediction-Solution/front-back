"""
Pydantic 스키마 정의
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date, datetime
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