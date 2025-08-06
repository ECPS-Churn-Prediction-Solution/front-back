"""
사용자 관련 API 엔드포인트
회원가입, 로그인 등의 사용자 인증 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserRegisterRequest, UserLoginRequest, UserResponse, LoginResponse, MessageResponse
from crud import get_user_by_email, create_user, authenticate_user
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    사용자 회원가입
    신규 고객 정보와 관심사를 DB에 저장
    
    Args:
        user_data: 회원가입 요청 데이터
        db: 데이터베이스 세션
    
    Returns:
        MessageResponse: 회원가입 결과 메시지
    
    Raises:
        HTTPException: 이메일 중복 또는 서버 오류
    """
    logger.info(f"회원가입 시도: {user_data.email}")
    
    # 이메일 중복 확인
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        logger.warning(f"이메일 중복 시도: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 이메일입니다."
        )
    
    try:
        # 사용자 생성
        new_user = create_user(db, user_data)
        logger.info(f"회원가입 성공: {new_user.email} (ID: {new_user.user_id})")
        
        return MessageResponse(message="회원가입이 성공적으로 완료되었습니다.")
    
    except Exception as e:
        logger.error(f"회원가입 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원가입 중 오류가 발생했습니다."
        )

@router.post("/login", response_model=LoginResponse)
async def login_user(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """
    사용자 로그인
    이메일, 비밀번호 인증 후 사용자 정보 반환
    
    Args:
        login_data: 로그인 요청 데이터
        db: 데이터베이스 세션
    
    Returns:
        LoginResponse: 로그인 성공 메시지와 사용자 정보
    
    Raises:
        HTTPException: 인증 실패
    """
    logger.info(f"로그인 시도: {login_data.email}")
    
    # 사용자 인증
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        logger.warning(f"로그인 실패: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 사용자 응답 데이터 생성
    user_response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        user_name=user.user_name,
        gender=user.gender,
        birthdate=user.birthdate,
        phone_number=user.phone_number,
        created_at=user.created_at
    )
    
    logger.info(f"로그인 성공: {user.email} (ID: {user.user_id})")
    
    return LoginResponse(
        message="로그인 성공",
        user=user_response
    )