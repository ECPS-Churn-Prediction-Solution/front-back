# 쇼핑몰 FastAPI 백엔드

FastAPI 기반 쇼핑몰 백엔드 API 서버

## 🚀 주요 기능

- **사용자 인증**: 회원가입, 로그인, 세션 관리
- **카테고리 관리**: 메뉴 구성을 위한 카테고리 조회
- **상품 관리**: 상품 목록/상세 조회
- **장바구니**: 상품 추가/조회/수량변경/삭제 (ERD 기반 variant_id)
- **주문 관리**: 주문 생성, 주문 목록, 주문 상세 조회

## ⚙️ 빠른 시작

### 1. 환경 설정
```bash
# 백엔드 폴더로 이동
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements.txt
```

### 2. 데이터베이스 설정 (SQLite)
```bash
# 테이블 생성
python -m db.create_tables  

# 더미 데이터 입력
python insert_dummy_data.py
```

### 3. 서버 실행
```bash
python main.py
```

**Swagger UI**: http://localhost:8000/docs

## 🔗 API 엔드포인트

### 사용자 인증
- `POST /api/users/register` - 회원가입
- `POST /api/users/login` - 로그인
- `GET /api/users/me` - 내 정보 조회
- `POST /api/users/logout` - 로그아웃

### 상품
- `GET /api/products` - 전체 상품 목록
- `GET /api/products/{id}` - 상품 상세 (옵션 포함)

### 카테고리
- `GET /api/categories` - 전체 카테고리 목록 (메뉴 구성용)

### 장바구니
- `GET /api/cart/` - 장바구니 조회
- `POST /api/cart/items` - 상품 추가
- `PUT /api/cart/items/{variant_id}` - 수량 변경
- `DELETE /api/cart/items/{variant_id}` - 상품 제거

### 주문
- `POST /api/orders` - 주문 생성
- `GET /api/orders` - 주문 목록
- `GET /api/orders/{id}` - 주문 상세

## 📝 테스트 예시

### 1. 회원가입
```json
POST /api/users/register
{
  "email": "test@example.com",
  "password": "password123",
  "user_name": "홍길동",
  "gender": "male",
  "birthdate": "1990-01-01",
  "phone_number": "010-1234-5678",
  "interest_categories": [1, 2]
}
```

### 2. 로그인
```json
POST /api/users/login
{
  "email": "test@example.com",
  "password": "password123"
}
```

### 3. 장바구니 추가 (variant_id 사용)
```json
POST /api/cart/items
{
  "variant_id": 1,
  "quantity": 2
}
```

### 4. 주문 생성
```json
POST /api/orders
{
  "recipient_name": "홍길동",
  "shipping_address": {
    "zip_code": "06134",
    "address_main": "서울시 강남구 테헤란로 123",
    "address_detail": "45층 101호"
  },
  "phone_number": "010-1234-5678",
  "shopping_memo": "부재 시 경비실 맡김",
  "payment_method": "credit_card",
  "used_coupon_code": ""
}
```

## 🗄️ 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite (개발용)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Authentication**: Session-based
- **Password**: bcrypt

## 📁 프로젝트 구조

```
backend/
├── main.py              # FastAPI 앱
├── database.py          # DB 연결
├── models.py            # DB 모델 (ERD 기반)
├── schemas.py           # API 스키마
├── crud.py              # DB CRUD 함수
├── auth.py              # 인증 유틸
├── users.py             # 사용자 API
├── products.py          # 상품 API
├── cart.py              # 장바구니 API
├── orders.py            # 주문 API
├── create_tables.py     # 테이블 생성
├── insert_dummy_data.py # 더미 데이터
└── requirements.txt     # 의존성
```

## ✅ 현재 상태

- **ERD 기반 variant_id 시스템** 완전 구현
- **모든 API 엔드포인트** 정상 작동
- **Swagger UI** 완전 문서화
- **전체 플로우** 테스트 완료 (상품 → 장바구니 → 주문)