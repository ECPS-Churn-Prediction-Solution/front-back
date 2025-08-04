# React 의류 쇼핑몰 프론트엔드 템플릿

## 실행 방법

```bash
cd frontend
npm install
npm run dev
```

## 폴더 구조

```
frontend/
  ├── public/
  │   └── mock-images/   # 샘플 이미지 폴더 (이미지 파일 직접 추가)
  ├── src/
  │   ├── assets/
  │   ├── components/
  │   │   ├── common/
  │   │   └── home/
  │   ├── data/
  │   ├── layouts/
  │   ├── pages/
  │   ├── routes/
  │   └── styles/
  ├── package.json
  └── ...
```

## 목업 이미지 적용
- `public/mock-images` 폴더에 jpg/png 파일을 직접 넣어주세요.
- 예시 파일명: `collection1.jpg`, `collection2.jpg`, `week1.jpg` 등
- 이미지가 없으면 기본적으로 빈 이미지로 표시됩니다.

## 주요 기능
- 반응형 헤더/푸터/메인/관리자 대시보드
- 라우팅: 홈, 카테고리, 상품상세, 장바구니, 관리자
- 스타일: styled-components
- 차트: recharts (관리자)

---
추가 개발 및 문의는 언제든 요청해주세요!
