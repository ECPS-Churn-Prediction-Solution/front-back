"""
데이터베이스 CRUD (Create, Read, Update, Delete) 함수들
사용자 관련 데이터베이스 작업을 처리
"""

from sqlalchemy.orm import Session
from models import User, UserInterest
from schemas import UserRegisterRequest
from auth import get_password_hash, verify_password
from typing import Optional, List

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    이메일로 사용자 조회
    
    Args:
        db: 데이터베이스 세션
        email: 사용자 이메일
    
    Returns:
        User: 사용자 객체 (없으면 None)
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    사용자 ID로 사용자 조회
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
    
    Returns:
        User: 사용자 객체 (없으면 None)
    """
    return db.query(User).filter(User.user_id == user_id).first()

def create_user(db: Session, user_data: UserRegisterRequest) -> User:
    """
    새 사용자 생성 (회원가입)
    사용자 정보와 관심사를 데이터베이스에 저장
    
    Args:
        db: 데이터베이스 세션
        user_data: 회원가입 요청 데이터
    
    Returns:
        User: 생성된 사용자 객체
    """
    # 비밀번호 해싱
    hashed_password = get_password_hash(user_data.password)
    
    # 사용자 객체 생성
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        user_name=user_data.user_name,
        gender=user_data.gender,
        birthdate=user_data.birthdate,
        phone_number=user_data.phone_number
    )
    
    # 데이터베이스에 사용자 추가
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 관심사 추가 (있는 경우)
    if user_data.interest_categories:
        add_user_interests(db, db_user.user_id, user_data.interest_categories)
    
    return db_user

def add_user_interests(db: Session, user_id: int, category_ids: List[int]) -> None:
    """
    사용자의 관심사 추가
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        category_ids: 관심 카테고리 ID 리스트
    """
    for category_id in category_ids:
        # 이미 존재하는 관심사인지 확인
        existing_interest = db.query(UserInterest).filter(
            UserInterest.user_id == user_id,
            UserInterest.category_id == category_id
        ).first()
        
        # 존재하지 않으면 추가
        if not existing_interest:
            interest = UserInterest(user_id=user_id, category_id=category_id)
            db.add(interest)
    
    db.commit()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    사용자 인증 (로그인)
    이메일과 비밀번호로 사용자 검증
    
    Args:
        db: 데이터베이스 세션
        email: 사용자 이메일
        password: 평문 비밀번호
    
    Returns:
        User: 인증된 사용자 객체 (인증 실패 시 None)
    """
    # 이메일로 사용자 조회
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # 비밀번호 검증
    if not verify_password(password, user.password_hash):
        return None
    
    return user

def get_user_interests(db: Session, user_id: int) -> List[int]:
    """
    사용자의 관심사 카테고리 ID 리스트 조회
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
    
    Returns:
        List[int]: 관심 카테고리 ID 리스트
    """
    interests = db.query(UserInterest.category_id).filter(
        UserInterest.user_id == user_id
    ).all()
    
    return [interest.category_id for interest in interests]