"""
FastAPI 메인 애플리케이션
쇼핑몰 백엔드 API 서버의 진입점
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import logging
from api.users import router as users_router
from api.cart import router as cart_router
from api.orders import router as orders_router
from api.products import router as products_router
from api.categories import router as categories_router
from api.logs import router as logs_router

# 로깅 설정
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Shopping Mall API",
    description="쇼핑몰 백엔드 API - 회원가입 및 로그인 기능",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# 세션 미들웨어 추가 (세션 기반 인증용)
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-this-in-production"
)

# CORS 미들웨어 설정 (프론트엔드 연결용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],  # 프론트엔드 도메인
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# API 라우터 등록
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(cart_router, prefix="/api/cart", tags=["cart"])
app.include_router(orders_router, prefix="/api/orders", tags=["orders"])
app.include_router(products_router, prefix="/api/products")
app.include_router(categories_router, prefix="/api/categories")
app.include_router(logs_router) # 로그 라우터 추가


@app.get("/", tags=["root"])
def read_root():
    """
    루트 엔드포인트
    API 서버 상태 확인
    """
    return {
        "message": "Shopping Mall FastAPI Backend Server",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["health"])
def health_check():
    """
    헬스체크 엔드포인트
    서버 상태 모니터링용
    """
    return {
        "status": "healthy",
        "message": "서버가 정상 작동 중입니다."
    }

# 개발 서버 실행 (프로덕션에서는 사용하지 않음)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=False,  # 리로드 비활성화
        log_level="info"  # 디버그 모드로 변경
    )