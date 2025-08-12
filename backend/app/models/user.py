"""
사용자 관련 모델
"""

from sqlalchemy import Column, Integer, String, Date, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
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
    zip_code = Column(String(10), nullable=True, comment="우편번호")
    address_main = Column(String(255), nullable=True, comment="기본 주소")
    address_detail = Column(String(255), nullable=True, comment="상세 주소")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="가입일")
    
    # 관계 설정
    interests = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    logins = relationship("UserLogin", back_populates="user")

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

class UserLogin(Base):
    """
    사용자 로그인 기록 테이블
    """
    __tablename__ = "user_logins"

    login_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="로그인 기록 고유 번호")
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment="사용자 ID")
    login_at = Column(TIMESTAMP, server_default=func.now(), comment="로그인 시간")

    # 관계 설정
    user = relationship("User", back_populates="logins")
