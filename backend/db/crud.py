"""
데이터베이스 CRUD (Create, Read, Update, Delete) 함수들
사용자 관련 데이터베이스 작업을 처리
"""

from sqlalchemy.orm import Session
from db.models import (
    User, Product, Category, CartItem, Order, OrderItem, ProductVariant, UserInterest,
    DailyChurnKpi, ChurnSegmentAggr, ChurnRiskDistribution, HighRiskUser,ActionRecommendation
)
from db.schemas import UserRegisterRequest, OrderCreateRequest, CartItemAdd, DirectOrderRequest
from api.auth import get_password_hash, verify_password
from typing import Optional, List
from decimal import Decimal
from datetime import date

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
        # 카테고리 존재 여부 검증 (외래키 오류 방지)
        category_exists = db.query(Category.category_id).filter(Category.category_id == category_id).first()
        if not category_exists:
            # 존재하지 않는 카테고리는 건너뜀
            continue
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

# === 상품 관련 CRUD 함수 ===

def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    """
    상품 ID로 상품 조회

    Args:
        db: 데이터베이스 세션
        product_id: 상품 ID

    Returns:
        Product: 상품 객체 (없으면 None)
    """
    return db.query(Product).filter(Product.product_id == product_id).first()

def get_variant_by_id(db: Session, variant_id: int) -> Optional[ProductVariant]:
    """
    상품 옵션 ID로 상품 옵션 조회

    Args:
        db: 데이터베이스 세션
        variant_id: 상품 옵션 ID

    Returns:
        Optional[ProductVariant]: 상품 옵션 객체 또는 None
    """
    return db.query(ProductVariant).filter(ProductVariant.variant_id == variant_id).first()

# === 장바구니 관련 CRUD 함수 === //////

def get_cart_items(db: Session, user_id: int) -> List[CartItem]:
    """
    사용자의 장바구니 아이템들 조회

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID

    Returns:
        List[CartItem]: 장바구니 아이템 리스트
    """
    return db.query(CartItem).filter(CartItem.user_id == user_id).all()

def add_to_cart(db: Session, user_id: int, cart_item: CartItemAdd) -> CartItem:
    """
    장바구니에 상품 추가 또는 수량 증가

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        cart_item: 장바구니 추가 데이터

    Returns:
        CartItem: 장바구니 아이템 객체
    """
    # 이미 장바구니에 있는 상품인지 확인 (variant_id 기준)
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.variant_id == cart_item.variant_id
    ).first()

    if existing_item:
        # 이미 있으면 수량 증가
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # 새로 추가
        new_item = CartItem(
            user_id=user_id,
            variant_id=cart_item.variant_id,
            quantity=cart_item.quantity
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

def update_cart_item(db: Session, user_id: int, cart_item_id: int, quantity: int) -> Optional[CartItem]:
    """
    장바구니 상품 수량 변경

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        cart_item_id: 장바구니 아이템 ID
        quantity: 새로운 수량

    Returns:
        CartItem: 수정된 장바구니 아이템 (없으면 None)
    """
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.cart_item_id == cart_item_id
    ).first()

    if cart_item:
        cart_item.quantity = quantity
        db.commit()
        db.refresh(cart_item)
        return cart_item

    return None

def get_cart_item_for_user(db: Session, cart_item_id: int, user_id: int) -> Optional[CartItem]:
    """
    특정 사용자의 특정 장바구니 아이템 조회 (삭제 전 권한 확인용)

    Args:
        db: 데이터베이스 세션
        cart_item_id: 장바구니 아이템 ID
        user_id: 사용자 ID

    Returns:
        Optional[CartItem]: 장바구니 아이템 객체 (없거나 권한이 없으면 None)
    """
    return db.query(CartItem).filter(
        CartItem.cart_item_id == cart_item_id,
        CartItem.user_id == user_id,
    ).first()

def remove_cart_item_by_id(db: Session, cart_item_id: int) -> bool:
    """
    장바구니 아이템 ID로 상품 삭제

    Args:
        db: 데이터베이스 세션
        cart_item_id: 장바구니 아이템 ID

    Returns:
        bool: 삭제 성공 여부
    """
    # cart.py에서 get_cart_item_for_user를 통해 권한 확인이 선행됨
    cart_item = db.query(CartItem).filter(CartItem.cart_item_id == cart_item_id).first()

    if cart_item:
        db.delete(cart_item)
        db.commit()
        return True

    return False

def clear_cart(db: Session, user_id: int) -> bool:
    """
    사용자의 장바구니 전체 비우기

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID

    Returns:
        bool: 성공 여부
    """
    try:
        # 사용자의 모든 장바구니 항목 삭제
        deleted_count = db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        db.commit()

        print(f"사용자 {user_id}의 장바구니 {deleted_count}개 항목 삭제 완료")
        return True

    except Exception as e:
        print(f"장바구니 비우기 실패: {e}")
        db.rollback()
        return False

# === 카테고리 관련 CRUD 함수 ===

def get_all_categories(db: Session) -> List[Category]:
    """
    모든 카테고리 목록 조회

    Args:
        db: 데이터베이스 세션

    Returns:
        List[Category]: 전체 카테고리 목록
    """
    return db.query(Category).order_by(Category.category_id).all()

# === 상품 관련 CRUD 함수 ===

def get_all_products(db: Session) -> List[Product]:
    """
    모든 상품 목록 조회 (간단 버전)

    Args:
        db: 데이터베이스 세션

    Returns:
        List[Product]: 전체 상품 목록
    """
    return db.query(Product).all()

def get_product_by_id_with_variants(db: Session, product_id: int) -> Optional[Product]:
    """
    상품 ID로 상품과 옵션 정보 조회

    Args:
        db: 데이터베이스 세션
        product_id: 상품 ID

    Returns:
        Product: 상품 객체 (옵션 포함)
    """
    return db.query(Product).filter(Product.product_id == product_id).first()

def get_product_variants(db: Session, product_id: int) -> List[ProductVariant]:
    """
    상품의 모든 옵션 조회

    Args:
        db: 데이터베이스 세션
        product_id: 상품 ID

    Returns:
        List[ProductVariant]: 상품 옵션 목록
    """
    return db.query(ProductVariant).filter(ProductVariant.product_id == product_id).all()

# === 주문 관련 CRUD 함수 ===

def create_order_from_cart(db: Session, user_id: int, order_data: OrderCreateRequest) -> Order:
    """장바구니에서 주문 생성 (쿠폰 적용 포함)"""
    # 장바구니 아이템들 조회
    cart_items = get_cart_items(db, user_id)
    if not cart_items:
        raise ValueError("장바구니가 비어있습니다.")

    # 재고 확인
    for cart_item in cart_items:
        variant = cart_item.variant
        if variant.stock_quantity < cart_item.quantity:
            raise ValueError(f"재고가 부족합니다.")

    # 상품 총액 계산
    items_total = sum(float(cart_item.variant.product.price * cart_item.quantity) for cart_item in cart_items)
    shipping_fee = float(order_data.shipping_fee or 3000.0)

    # 쿠폰 적용 로직
    coupon_discount = 0.0
    if order_data.used_coupon_code:
        coupon = get_coupon_by_code(db, user_id, order_data.used_coupon_code)
        if coupon:
            coupon_discount = float(coupon.discount_amount)
        else:
            raise ValueError("유효하지 않은 쿠폰입니다.")

    # 최종 금액 계산
    total_amount = max(0, items_total + shipping_fee - coupon_discount)

    # 주문 생성
    new_order = Order(
        user_id=user_id,
        total_amount=total_amount,
        shipping_fee=shipping_fee,
        status="pending",
        shipping_address=f"{order_data.shipping_address.address_main}, {order_data.shipping_address.address_detail}",
        shipping_memo=order_data.shopping_memo,
        payment_method=order_data.payment_method,
        used_coupon_code=order_data.used_coupon_code,
        recipient_name=order_data.recipient_name,
        zip_code=order_data.shipping_address.zip_code,
        address_main=order_data.shipping_address.address_main,
        address_detail=order_data.shipping_address.address_detail,
        phone_number=order_data.phone_number
    )
    db.add(new_order)
    db.flush()

    # 주문 상품들 생성
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=new_order.order_id,
            variant_id=cart_item.variant_id,
            quantity=cart_item.quantity,
            price_per_item=cart_item.variant.product.price
        )
        cart_item.variant.stock_quantity -= cart_item.quantity
        db.add(order_item)

    # 쿠폰 사용 처리
    if order_data.used_coupon_code and coupon_discount > 0:
        coupon = get_coupon_by_code(db, user_id, order_data.used_coupon_code)
        if coupon:
            coupon.is_used = True
            coupon.used_at = datetime.now()

    # 장바구니 비우기
    clear_cart(db, user_id)

    db.commit()
    db.refresh(new_order)
    return new_order

def get_user_orders(db: Session, user_id: int) -> List[Order]:
    """
    사용자의 모든 주문 조회

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID

    Returns:
        List[Order]: 주문 리스트 (최신순)
    """
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.order_date.desc()).all()

def get_order_by_id(db: Session, user_id: int, order_id: int) -> Optional[Order]:
    """
    특정 주문 상세 조회

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        order_id: 주문 ID

    Returns:
        Order: 주문 객체 (없으면 None)
    """
    return db.query(Order).filter(
        Order.order_id == order_id,
        Order.user_id == user_id
    ).first()

def create_direct_order(db: Session, user_id: int, order_data: DirectOrderRequest) -> Order:
    """
    즉시 주문 생성 (장바구니를 거치지 않고 바로 주문)

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        order_data: 즉시 주문 데이터

    Returns:
        Order: 생성된 주문 객체

    Raises:
        ValueError: 상품이 존재하지 않거나 재고가 부족할 때
    """
    # 상품 옵션 존재 여부 및 재고 확인
    variant = get_variant_by_id(db, order_data.variant_id)
    if not variant:
        raise ValueError(f"상품 옵션 ID {order_data.variant_id}를 찾을 수 없습니다.")

    if variant.stock_quantity < order_data.quantity:
        raise ValueError(f"재고가 부족합니다. 현재 재고: {variant.stock_quantity}개, 주문 수량: {order_data.quantity}개")

    # 총 금액 계산 (상품 총액 + 배송비)
    items_total = float(variant.product.price * order_data.quantity)
    requested_fee = float(getattr(order_data, 'shipping_fee', 0) or 0)
    shipping_fee = requested_fee if requested_fee > 0 else (3000.0 if order_data.quantity > 0 else 0.0)
    total_amount = items_total + shipping_fee

    # 주문 생성
    new_order = Order(
        user_id=user_id,
        total_amount=total_amount,
        shipping_fee=shipping_fee,
        status="pending",
        shipping_address=f"{order_data.shipping_address.address_main}, {order_data.shipping_address.address_detail}",
        shipping_memo=order_data.shopping_memo,
        payment_method=order_data.payment_method,
        used_coupon_code=order_data.used_coupon_code,
        recipient_name=order_data.recipient_name,
        zip_code=order_data.shipping_address.zip_code,
        address_main=order_data.shipping_address.address_main,
        address_detail=order_data.shipping_address.address_detail,
        phone_number=order_data.phone_number
    )
    db.add(new_order)
    db.flush()  # order_id를 얻기 위해 flush

    # 주문 상품 생성
    order_item = OrderItem(
        order_id=new_order.order_id,
        variant_id=order_data.variant_id,
        quantity=order_data.quantity,
        price_per_item=variant.product.price
    )
    db.add(order_item)

    # 재고 차감
    variant.stock_quantity -= order_data.quantity

    db.commit()
    db.refresh(new_order)
    return new_order

# === 대시보드 관련 CRUD 함수 ===

def get_overall_churn_rate(db: Session, report_dt: date, horizon_days: int):
    """
    전체 Churn Rate 지표를 데이터베이스에서 조회
    """
    kpi_data = db.query(DailyChurnKpi).filter(
        DailyChurnKpi.report_dt == report_dt,
        DailyChurnKpi.horizon_days == horizon_days
    ).first()

    if not kpi_data:
        # 데이터가 없을 경우, 기본 0 값으로 응답 객체를 생성
        return {
            "reportDt": report_dt,
            "horizonDays": horizon_days,
            "customersTotal": 0,
            "churnRate": 0.0,
            "retentionRate": 1.0,
            "churnCustomers": 0
        }

    retention_rate = 1 - kpi_data.churn_rate
    return {
        "reportDt": kpi_data.report_dt,
        "horizonDays": kpi_data.horizon_days,
        "customersTotal": kpi_data.customers_total,
        "churnRate": kpi_data.churn_rate,
        "retentionRate": retention_rate,
        "churnCustomers": kpi_data.churn_customers
    }

def get_rfm_churn_rate(db: Session, report_dt: date, horizon_days: int):
    """
    RFM 그룹별 Churn Rate 지표를 데이터베이스에서 조회
    """
    segments_data = db.query(ChurnSegmentAggr).filter(
        ChurnSegmentAggr.report_dt == report_dt,
        ChurnSegmentAggr.horizon_days == horizon_days,
        ChurnSegmentAggr.segment_type == 'rfm_segment'
    ).all()

    if not segments_data:
        # 데이터가 없을 경우, 빈 세그먼트 리스트로 응답
        return {
            "reportDt": report_dt,
            "horizonDays": horizon_days,
            "segments": []
        }

    segments = [
        {
            "bucket": s.segment_key,
            "customers": s.customers,
            "churnRate": s.churn_rate,
            "atRiskUsers": round(s.customers * s.churn_rate)
        } for s in segments_data
    ]

    return {
        "reportDt": report_dt,
        "horizonDays": horizon_days,
        "segments": segments
    }

def get_churn_risk_distribution(db: Session, report_dt: date, horizon_days: int):
    """
    위험 밴드별 고객 분포 지표를 데이터베이스에서 조회
    """
    distribution_data = db.query(ChurnRiskDistribution).filter(
        ChurnRiskDistribution.report_dt == report_dt,
        ChurnRiskDistribution.horizon_days == horizon_days
    ).all()

    if not distribution_data:
        # 데이터가 없을 경우, 빈 밴드 리스트와 0 값으로 응답
        return {
            "reportDt": report_dt,
            "horizonDays": horizon_days,
            "bands": [],
            "atRisk": {
                "userCount": 0,
                "ratio": 0.0
            }
        }

    bands = [
        {"riskBand": d.risk_band, "userCount": d.user_count, "ratio": d.ratio}
        for d in distribution_data
    ]

    at_risk_bands = [d for d in distribution_data if d.risk_band in ('VH', 'H')]
    at_risk_user_count = sum(d.user_count for d in at_risk_bands)
    at_risk_ratio = sum(d.ratio for d in at_risk_bands)

    return {
        "reportDt": report_dt,
        "horizonDays": horizon_days,
        "bands": bands,
        "atRisk": {
            "userCount": at_risk_user_count,
            "ratio": at_risk_ratio
        }
    }

def get_high_risk_users(db: Session, report_dt: date, horizon_days: int, page: int = 1, per_page: int = 10):
    """
    고위험 사용자 리스트를 데이터베이스에서 조회 (페이징 지원)
    """
    offset = (page - 1) * per_page

    # Query for the total count first
    total_count_query = db.query(HighRiskUser).filter(
        HighRiskUser.report_dt == report_dt,
        HighRiskUser.horizon_days == horizon_days
    )
    total_count = total_count_query.count()

    # Query for the paginated items with join - risk_band로 매칭
    users_query = total_count_query.join(
        ActionRecommendation,
        (HighRiskUser.policy_id == ActionRecommendation.policy_id) &
        (HighRiskUser.risk_band == ActionRecommendation.risk_band)
    ).order_by(
        HighRiskUser.churn_probability.desc()
    ).offset(offset).limit(per_page)

    results = users_query.all()

    items = [
        {
            "userId": r.user_id,
            "riskBand": r.risk_band,
            "churnProbability": r.churn_probability,
            "action": {
                "policyId": r.policy_id,
                "policy_name": r.action_recommendation.policy_name
            }
        } for r in results
    ]

    return {
        "reportDt": report_dt,
        "horizonDays": horizon_days,
        "total": total_count,
        "items": items
    }

def get_action_recommendation(db: Session, policy_id: int, risk_band: str):
    """
    정책 ID와 위험군으로 액션 추천 정보 조회
    """
    return db.query(ActionRecommendation).filter(
        ActionRecommendation.policy_id == policy_id,
        ActionRecommendation.risk_band == risk_band
    ).first()

def get_user_coupons(db: Session, user_id: int):
    """사용자의 사용 가능한 쿠폰 목록 조회"""
    from db.models import Coupon
    from datetime import datetime

    return db.query(Coupon).filter(
        Coupon.user_id == user_id,
        Coupon.expires_at > datetime.now(),
        Coupon.is_used == False
    ).order_by(Coupon.created_at.desc()).all()

def get_coupon_by_code(db: Session, user_id: int, coupon_code: str):
    """쿠폰 코드로 쿠폰 조회"""
    from db.models import Coupon
    from datetime import datetime

    return db.query(Coupon).filter(
        Coupon.coupon_code == coupon_code,
        Coupon.user_id == user_id,
        Coupon.is_used == False,
        Coupon.expires_at > datetime.now()
    ).first()

def issue_coupon_for_user(db: Session, user_id: int, policy_name: str) -> str:
    """사용자에게 쿠폰을 지급합니다."""
    from datetime import datetime, timedelta
    from db.models import Coupon
    import random
    import string

    # 쿠폰 코드 생성
    coupon_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # 쿠폰 만료일 (30일 후)
    expires_at = datetime.now() + timedelta(days=30)

    # 할인 금액 결정 (정책명에 따라)
    discount_amount = 5000  # 기본값
    if "50%" in policy_name:
        discount_amount = 10000
    elif "30%" in policy_name:
        discount_amount = 7000
    elif "20%" in policy_name:
        discount_amount = 5000

    # 쿠폰 생성
    new_coupon = Coupon(
        user_id=user_id,
        coupon_code=coupon_code,
        discount_amount=discount_amount,
        policy_name=policy_name,
        expires_at=expires_at,
        created_at=datetime.now()
    )

    db.add(new_coupon)
    db.commit()
    db.refresh(new_coupon)

    return coupon_code

def delete_high_risk_user(db: Session, user_id: int, policy_id: int) -> bool:
    """
    고위험 사용자 데이터를 삭제합니다.
    """
    from sqlalchemy import text

    try:
        result = db.execute(text("""
            DELETE FROM mart.high_risk_users
            WHERE user_id = :user_id AND policy_id = :policy_id
        """), {
            "user_id": user_id,
            "policy_id": policy_id
        })
        db.commit()
        return result.rowcount > 0
    except Exception as e:
        print(f"고위험 사용자 삭제 실패: {e}")
        db.rollback()
        return False
