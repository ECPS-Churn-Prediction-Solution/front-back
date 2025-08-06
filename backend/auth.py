"""
인증 및 보안 관련 유틸리티
JWT 토큰 생성/검증, 비밀번호 해싱 등
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호를 비교하여 검증
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호
    
    Returns:
        bool: 비밀번호 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    평문 비밀번호를 해시화
    
    Args:
        password: 평문 비밀번호
    
    Returns:
        str: 해시된 비밀번호
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성
    
    Args:
        data: 토큰에 포함할 데이터 (보통 사용자 ID)
        expires_delta: 토큰 만료 시간 (선택사항)
    
    Returns:
        str: JWT 토큰
    """
    to_encode = data.copy()
    
    # 만료 시간 설정
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # JWT 토큰 생성
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> int:
    """
    JWT 토큰 검증 및 사용자 ID 추출
    
    Args:
        token: JWT 토큰
    
    Returns:
        int: 사용자 ID
    
    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    """
    try:
        # 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 유효하지 않습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return int(user_id)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )