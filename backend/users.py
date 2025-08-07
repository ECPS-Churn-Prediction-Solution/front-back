"""
사용자 관련 API 엔드포인트
회원가입, 로그인 등의 사용자 인증 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserRegisterRequest, UserLoginRequest, UserResponse, LoginResponse, MessageResponse
from crud import get_user_by_email, create_user, authenticate_user, get_user_by_id
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()

# 간단한 세션 저장소 (실제 프로덕션에서는 Redis 등을 사용)
active_sessions = {}

def get_current_user(request: Request, db: Session = Depends(get_db)) -> UserResponse:
    """
    현재 로그인된 사용자 정보 반환
    세션에서 사용자 ID를 가져와 사용자 정보를 조회
    """
    # 세션에서 사용자 ID 가져오기
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )
    
    # 데이터베이스에서 사용자 정보 조회
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        user_name=user.user_name,
        gender=user.gender,
        birthdate=user.birthdate,
        phone_number=user.phone_number,
        created_at=user.created_at
    )

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
async def login_user(login_data: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    사용자 로그인
    이메일, 비밀번호 인증 후 사용자 정보 반환
    
    Args:
        login_data: 로그인 요청 데이터
        request: HTTP 요청 객체 (세션 접근용)
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
    
    # 세션에 사용자 ID 저장
    request.session["user_id"] = user.user_id
    
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

@router.get("/me", response_model=UserResponse)
async def get_my_info(current_user: UserResponse = Depends(get_current_user)):
    """
    현재 로그인된 사용자의 정보 조회
    
    Args:
        current_user: 현재 로그인된 사용자 정보 (의존성 주입)
    
    Returns:
        UserResponse: 현재 사용자 정보
    
    Raises:
        HTTPException: 로그인되지 않은 경우
    """
    logger.info(f"내 정보 조회: {current_user.email} (ID: {current_user.user_id})")
    return current_user

@router.post("/logout", response_model=MessageResponse)
async def logout_user(request: Request):
    """
    사용자 로그아웃
    세션에서 사용자 정보 제거
    
    Args:
        request: HTTP 요청 객체
    
    Returns:
        MessageResponse: 로그아웃 성공 메시지
    """
    # 세션에서 사용자 ID 제거
    if "user_id" in request.session:
        del request.session["user_id"]
        logger.info("로그아웃 성공")
        return MessageResponse(message="로그아웃이 완료되었습니다.")
    else:
        return MessageResponse(message="이미 로그아웃된 상태입니다.")