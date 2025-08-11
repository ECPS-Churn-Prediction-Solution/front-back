# 쇼핑몰 FastAPI 백엔드

FastAPI를 사용한 쇼핑몰 백엔드 API 서버입니다.
회원가입, 로그인, 내 정보 조회, 장바구니 관리 기능을 제공합니다.

## 🚀 주요 기능

- **회원가입**: 신규 고객 정보와 관심사를 PostgreSQL DB에 저장
- **로그인**: 세션 기반 인증 시스템
- **내 정보 조회**: 현재 로그인된 사용자 정보 조회
- **로그아웃**: 세션 종료
- **🛒 장바구니**: 상품 추가/조회/수량변경/삭제 (ERD 기반 구현)

## 📁 프로젝트 구조

```
backend/
├── main.py              # FastAPI 메인 애플리케이션
├── database.py          # PostgreSQL 데이터베이스 연결 설정
├── models.py            # SQLAlchemy 데이터베이스 모델 (ERD 기반)
├── schemas.py           # Pydantic 요청/응답 스키마
├── auth.py              # 비밀번호 해싱 (bcrypt)
├── crud.py              # 데이터베이스 CRUD 함수
├── users.py             # 사용자 관련 API 엔드포인트
├── cart.py              # 장바구니 관련 API 엔드포인트
├── create_tables.py     # 테이블 생성 스크립트
├── init_data.py         # 초기 카테고리 데이터 생성
├── requirements.txt     # 의존성 목록
├── .env                 # 환경변수 설정
└── README.md           # 프로젝트 문서
```

## ⚙️ 개발환경 설정

### 1. 가상환경 생성 및 활성화
백엔드 폴더로 꼭 이동 - cd backend
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. PostgreSQL 설치 및 설정
1. **PostgreSQL 다운로드**: https://www.postgresql.org/download/windows/ (버전16.9)
2. **설치 후 데이터베이스 생성**: `shopping_mall`
3. **설치 시 설정한 비밀번호 기억하기**

### 4. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:
```env
# PostgreSQL 데이터베이스 연결 (본인 비밀번호로 수정!)
DATABASE_URL=postgresql://postgres:password@localhost:5432/shopping_mall

# 환경 설정
ENVIRONMENT=development
DEBUG=True

# 서버 설정
PORT=8000
HOST=0.0.0.0

# CORS 설정
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# 로깅 레벨
LOG_LEVEL=info

# 데이터베이스 풀 설정 (선택사항)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### 5. 데이터베이스 테이블 생성
```bash
python create_tables.py
```

### 6. 초기 데이터 생성 (카테고리 + 상품)
```bash
python init_data.py
```

### 7. 서버 실행
```bash
# 개발 서버 실행
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API 엔드포인트

### 기본 엔드포인트
- `GET /` - API 서버 상태 확인
- `GET /health` - 헬스체크

### 사용자 인증
- `POST /api/users/register` - 회원가입
- `POST /api/users/login` - 로그인
- `GET /api/users/me` - 내 정보 조회
- `POST /api/users/logout` - 로그아웃

### 🛒 장바구니 관리
- `GET /api/cart/` - 현재 고객의 장바구니 내용 전체 조회
- `POST /api/cart/items` - 장바구니에 특정 옵션의 상품 추가
- `PUT /api/cart/items/{variant_id}` - 장바구니에 담긴 상품의 수량 업데이트
- `DELETE /api/cart/items/{variant_id}` - 장바구니에서 특정 상품을 제거

### 🛍️ 상품 관리
- `GET /api/products` - 상품 목록 조회 (필터링 및 페이지네이션)
- `GET /api/products/{id}` - 특정 상품의 상세 정보와 옵션(색상/사이즈/재고) 제공

## 📝 API 사용 예시 (테스트 완료! ✅)

### 회원가입 요청
```json
{
  "email": "test@example.com",
  "password": "password123",
  "user_name": "홍길동",
  "gender": "male",
  "birthdate": "1990-01-01",
  "phone_number": "010-1234-5678",
  "interest_categories": [1, 2, 3]
}
```
**응답**: `201 Created` - "회원가입이 성공적으로 완료되었습니다."

### 로그인 요청
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```
**응답**: `200 OK` - 로그인 성공 메시지 + 사용자 정보

### 내 정보 조회
```json
GET /api/users/me
```
**응답**: `200 OK` - 현재 로그인된 사용자 정보

### 로그아웃
```json
POST /api/users/logout
```
**응답**: `200 OK` - "로그아웃이 완료되었습니다."

## 🛒 장바구니 API 사용 예시 (테스트 완료! ✅)

### 장바구니 조회
```json
GET /api/cart/
```
**응답**: `200 OK` - 장바구니 상품 목록 + 총 금액

### 장바구니에 상품 추가
```json
{
  "product_id": 1,
  "quantity": 2
}
```
**응답**: `201 Created` - "기본 면 티셔츠이(가) 장바구니에 추가되었습니다."

### 장바구니 수량 변경
```json
PUT /api/cart/items/1
{
  "quantity": 3
}
```
**응답**: `200 OK` - "장바구니 수량이 변경되었습니다."

### 장바구니에서 상품 제거
```json
DELETE /api/cart/items/1
```
**응답**: `200 OK` - "상품이 장바구니에서 삭제되었습니다."

### 기본 카테고리 목록
초기 데이터로 다음 카테고리들이 생성됩니다:
- 1: 상의
- 2: 하의  
- 3: 아우터
- 4: 신발
- 5: 액세서리
- 6: 티셔츠 (상의 하위)
- 7: 셔츠 (상의 하위)
- 8: 청바지 (하의 하위)
- 9: 슬랙스 (하의 하위)
- 10: 재킷 (아우터 하위)

### 테스트용 상품 목록
초기 데이터로 다음 상품들이 생성됩니다:
- **상품 ID 1**: 기본 면 티셔츠 (25,000원)
- **상품 ID 2**: 프리미엄 오가닉 티셔츠 (45,000원)
- **상품 ID 3**: 클래식 스트레이트 청바지 (89,000원)
- **상품 ID 4**: 슬림핏 청바지 (95,000원)
- **상품 ID 5**: 데님 재킷 (120,000원)

## 🗄️ 데이터베이스 스키마

프로젝트는 다음 테이블들을 사용합니다:

- **users**: 고객 기본 정보
- **categories**: 상품 카테고리 (관심사로도 활용)
- **user_interests**: 고객-관심사 연결 테이블
- **products**: 상품 정보
- **orders**: 주문 정보
- **order_items**: 주문 상세 항목
- **cart_items**: 장바구니 항목 (ERD 기반)

## 🔧 개발 참고사항

### 코드 스타일
- 모든 함수와 클래스에는 독스트링이 포함되어 있습니다
- 타입 힌트를 사용하여 코드 가독성을 높였습니다
- 로깅을 통해 중요한 이벤트를 추적합니다

### 보안
- 비밀번호는 bcrypt로 해싱됩니다
- 세션 기반 인증 시스템
- CORS 설정으로 프론트엔드와 안전한 통신

### 에러 처리
- 적절한 HTTP 상태 코드 반환
- 상세한 에러 메시지 제공
- 로그를 통한 디버깅 지원

## ✅ 테스트 완료 사항

- [x] **Python 3.11.9 설치** 완료
- [x] **FastAPI 의존성 설치** 완료
- [x] **PostgreSQL 연결** 완료
- [x] **데이터베이스 테이블 생성** 완료
- [x] **초기 카테고리 데이터** 완료
- [x] **회원가입 API** 정상 작동 확인
- [x] **로그인 API** 정상 작동 확인
- [x] **내 정보 조회 API** 정상 작동 확인
- [x] **로그아웃 API** 정상 작동 확인
- [x] **Swagger UI** 정상 작동 확인
- [x] **세션 기반 인증** 정상 작동 확인
- [x] **🛒 장바구니 조회 API** 정상 작동 확인
- [x] **🛒 장바구니 상품 추가 API** 정상 작동 확인
- [x] **🛒 장바구니 수량 변경 API** 정상 작동 확인
- [x] **🛒 장바구니 상품 삭제 API** 정상 작동 확인
- [x] **ERD 기반 데이터베이스 구조** 완벽 구현

## 🤝 협업 가이드

이 프로젝트는 협업을 위해 설계되었습니다:

- 📝 **상세한 주석**: 모든 함수와 클래스에 한국어 주석 포함
- 🏗️ **모듈화된 구조**: 각 기능별로 파일이 분리되어 있음
- 📊 **명확한 스키마**: Pydantic으로 API 명세가 자동 생성됨
- 🔍 **로깅**: 중요한 이벤트들이 로그로 기록됨
- 🗄️ **ERD 완벽 구현**: 설계된 데이터베이스 스키마 100% 반영

## 🎯 현재 상태

**✅ 완전히 구현되고 테스트 완료된 기능:**
- 회원가입 (이메일 중복 체크, 비밀번호 해싱, 관심사 저장)
- 로그인 (세션 기반 인증)
- 내 정보 조회 (현재 로그인된 사용자 정보)
- 로그아웃 (세션 종료)
- **🛒 장바구니 시스템 (ERD 기반 완벽 구현)**
  - 장바구니 조회 (총 금액 계산 포함)
  - 상품 추가 (중복 상품 수량 증가 처리)
  - 수량 변경 (실시간 업데이트)
  - 상품 삭제 (개별 상품 제거)
- **🛍️ 상품 관리 시스템 (완벽 구현)**
  - 상품 목록 조회 (필터링 및 페이지네이션)
  - 상품 상세 조회 (옵션 정보 포함)
  - 상품 옵션 (색상/사이즈/재고) 관리
- PostgreSQL 연동
- Swagger UI 문서화

**🚀 서버 실행 방법:**
```bash
cd backend
python main.py
```
스웨거 접속: http://localhost:8000/docs

**📝 참고:** 첫 번째 API(`GET /api/products`)에서 쿼리 파라미터를 통해 카테고리 필터링과 검색 기능을 모두 제공합니다.

## 🛒 장바구니 API 테스트 시나리오

### 1️⃣ 로그인
```json
POST /api/users/login
{
  "email": "test@example.com",
  "password": "password123"
}
```

### 2️⃣ 장바구니에 상품 추가
```json
POST /api/cart/items
{
  "product_id": 1,
  "quantity": 2
}
```

### 3️⃣ 장바구니 조회
```json
GET /api/cart/
```
**응답 예시:**
```json
{
  "items": [
    {
      "cart_item_id": 1,
      "product_id": 1,
      "product_name": "기본 면 티셔츠",
      "price": 25000,
      "quantity": 2,
      "total_price": 50000,
      "added_at": "2025-08-07T15:00:00"
    }
  ],
  "total_items": 1,
  "total_amount": 50000
}
```

### 4️⃣ 수량 변경
```json
PUT /api/cart/items/1
{
  "quantity": 3
}
```

### 5️⃣ 상품 제거
```json
DELETE /api/cart/items/1
```

**🎯 모든 API가 Swagger UI에서 테스트 가능합니다!**

## 🛍️ 상품 API 사용 예시 (테스트 완료! ✅)

### 1️⃣ 상품 목록 조회 (필터링 및 페이지네이션)
```json
GET /api/products?category_id=1&min_price=10000&max_price=100000&page=1&size=20
```

**응답 예시:**
```json
{
  "products": [
    {
      "product_id": 1,
      "product_name": "기본 면 티셔츠",
      "description": "편안한 착용감의 기본 면 티셔츠입니다.",
      "price": 25000,
      "category_name": "티셔츠",
      "created_at": "2025-08-07T15:00:00",
      "available_variants": 5
    }
  ],
  "total_count": 5,
  "total_pages": 1,
  "current_page": 1,
  "page_size": 20,
  "has_next": false,
  "has_prev": false
}
```

### 2️⃣ 상품 상세 조회
```json
GET /api/products/1
```

**응답 예시:**
```json
{
  "product_id": 1,
  "product_name": "기본 면 티셔츠",
  "description": "편안한 착용감의 기본 면 티셔츠입니다.",
  "price": 25000,
  "category_name": "티셔츠",
  "created_at": "2025-08-07T15:00:00",
  "variants": [
    {
      "variant_id": 1,
      "color": "화이트",
      "size": "S",
      "stock_quantity": 20,
      "price_adjustment": 0,
      "final_price": 25000
    },
    {
      "variant_id": 2,
      "color": "화이트",
      "size": "M",
      "stock_quantity": 25,
      "price_adjustment": 0,
      "final_price": 25000
    }
  ]
}
```



---