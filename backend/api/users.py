"""
사용자 관련 API 엔드포인트
회원가입, 로그인 등의 사용자 인증 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import UserRegisterRequest, UserLoginRequest, UserResponse, LoginResponse, MessageResponse
from db import crud  # crud 모듈 import
from db.crud import get_user_by_email, create_user, authenticate_user, get_user_by_id, get_user_coupons
from api.logs import log_event
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()

@router.options("/register")
async def options_register():
    return {"message": "OK"}

@router.options("/login")
async def options_login():
    return {"message": "OK"}

@router.options("/admin/login")
async def options_admin_login():
    return {"message": "OK"}

@router.options("/me")
async def options_me():
    return {"message": "OK"}

@router.options("/logout")
async def options_logout():
    return {"message": "OK"}

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
        created_at=user.created_at,
        is_admin=user.is_admin
    )

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db), request: Request = None):
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
        # 가입 생성일(created_at) 백데이트: 시뮬레이터/클라이언트가 보낸 X-Event-Time 헤더가 있으면 우선 적용
        try:
            hdr_dt = request.headers.get("X-Event-Time") if request is not None else None
            if hdr_dt:
                from datetime import datetime
                try:
                    parsed_dt = datetime.fromisoformat(hdr_dt)
                    new_user.created_at = parsed_dt
                    db.commit()
                    db.refresh(new_user)
                except Exception:
                    pass
        except Exception:
            pass
        # 로깅: 회원가입 성공
        try:
            log_event("auth_register", request, {"user_id": new_user.user_id, "email": new_user.email})
            # 프로필 스냅샷 이벤트 추가 (이후 피처 엔지니어링용)
            try:
                # gender를 Enum 문자열이 아닌 원시 값("male"|"female"|"other")으로 기록
                _g = getattr(new_user, "gender", None)
                try:
                    gender_str = (getattr(_g, "value") if _g is not None and hasattr(_g, "value") else (str(_g) if _g is not None else ""))
                except Exception:
                    gender_str = str(_g or "")

                profile_payload = {
                    "user_id": new_user.user_id,
                    "gender": gender_str,
                    "birthdate": str(getattr(new_user, "birthdate", "") or ""),
                    "created_at": str(getattr(new_user, "created_at", "") or ""),
                    "interest_categories": list(getattr(user_data, "interest_categories", []) or []),
                    "num_interests": len(getattr(user_data, "interest_categories", []) or []),
                }
                log_event("user_profile", request, profile_payload)
            except Exception:
                pass
        except Exception:
            pass
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
    """
    logger.info(f"로그인 시도: {login_data.email}")
    print(f"🔍 로그인 시도: {login_data.email}")  # 디버그용

    # 사용자 인증
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        logger.warning(f"로그인 실패: {login_data.email}")
        # 로깅: 로그인 실패
        try:
            log_event("auth_login_fail", request, {"email": login_data.email})
        except Exception:
            pass
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
        created_at=user.created_at,
        is_admin=user.is_admin
    )

    logger.info(f"로그인 성공: {user.email} (ID: {user.user_id})")
    # 로깅: 로그인 성공
    try:
        log_event("auth_login", request, {"user_id": user.user_id, "email": user.email})
    except Exception:
        pass

    return LoginResponse(
        message="로그인 성공",
        user=user_response
    )

@router.post("/admin/login", response_model=LoginResponse)
async def admin_login(login_data: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    관리자 로그인
    이메일, 비밀번호 인증 후 관리자 여부 확인
    """
    logger.info(f"관리자 로그인 시도: {login_data.email}")
    
    # 사용자 인증
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        logger.warning(f"관리자 로그인 실패 (인증 실패): {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 관리자 여부 확인
    if not user.is_admin:
        logger.warning(f"관리자 로그인 실패 (권한 없음): {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 없습니다."
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
        created_at=user.created_at,
        is_admin=user.is_admin
    )
    
    logger.info(f"관리자 로그인 성공: {user.email} (ID: {user.user_id})")
    
    return LoginResponse(
        message="관리자 로그인 성공",
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
        user_id = request.session.get("user_id")
        del request.session["user_id"]
        logger.info("로그아웃 성공")
        # 로깅: 로그아웃
        try:
            log_event("auth_logout", request, {"user_id": user_id})
        except Exception:
            pass
        return MessageResponse(message="로그아웃이 완료되었습니다.")
    else:
        return MessageResponse(message="이미 로그아웃된 상태입니다.")

@router.get("/my-coupons")
async def get_my_coupons(
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """현재 사용자의 사용 가능한 쿠폰 목록"""
    coupons = crud.get_user_coupons(db, current_user.user_id)

    coupon_list = []
    for coupon in coupons:
        # coupon 객체에서 policy_name 속성을 직접 사용하도록 수정
        policy_name = coupon.policy_name if coupon.policy_name else "알 수 없는 정책"

        coupon_list.append({
            "coupon_id": coupon.coupon_id,
            "coupon_code": coupon.coupon_code,
            "discount_amount": coupon.discount_amount,
            "policy_name": policy_name,  # 수정된 부분
            "expires_at": coupon.expires_at.isoformat(),
            "created_at": coupon.created_at.isoformat()
        })

    return coupon_list
