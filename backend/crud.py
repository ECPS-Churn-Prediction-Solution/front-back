"""
데이터베이스 CRUD (Create, Read, Update, Delete) 함수들
사용자 관련 데이터베이스 작업을 처리
"""

from sqlalchemy.orm import Session
from models import User, UserInterest, CartItem, Product, Order, OrderItem
from schemas import UserRegisterRequest, CartItemAdd, OrderCreateRequest
from auth import get_password_hash, verify_password
from typing import Optional, List
from decimal import Decimal

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

# === 장바구니 관련 CRUD 함수 ===

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
    # 이미 장바구니에 있는 상품인지 확인
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == cart_item.product_id
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
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

def update_cart_item(db: Session, user_id: int, product_id: int, quantity: int) -> Optional[CartItem]:
    """
    장바구니 상품 수량 변경

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        product_id: 상품 ID
        quantity: 새로운 수량

    Returns:
        CartItem: 수정된 장바구니 아이템 (없으면 None)
    """
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == product_id
    ).first()

    if cart_item:
        cart_item.quantity = quantity
        db.commit()
        db.refresh(cart_item)
        return cart_item

    return None

def remove_from_cart(db: Session, user_id: int, product_id: int) -> bool:
    """
    장바구니에서 상품 삭제

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        product_id: 상품 ID

    Returns:
        bool: 삭제 성공 여부
    """
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == product_id
    ).first()

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
        bool: 삭제 성공 여부 (삭제된 항목이 있으면 True)
    """
    deleted_count = db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
    return deleted_count > 0

# === 주문 관련 CRUD 함수 ===

def create_order_from_cart(db: Session, user_id: int, order_data: OrderCreateRequest) -> Order:
    """
    장바구니 정보를 바탕으로 주문 생성

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        order_data: 주문 생성 데이터

    Returns:
        Order: 생성된 주문 객체

    Raises:
        ValueError: 장바구니가 비어있을 때
    """
    # 장바구니 아이템들 조회
    cart_items = get_cart_items(db, user_id)

    if not cart_items:
        raise ValueError("장바구니가 비어있습니다.")

    # 총 금액 계산
    total_amount = Decimal('0')
    for cart_item in cart_items:
        total_amount += cart_item.product.price * cart_item.quantity

    # 주문 생성
    new_order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status="pending",
        shopping_address=order_data.shopping_address
    )
    db.add(new_order)
    db.flush()  # order_id를 얻기 위해 flush

    # 주문 상품들 생성
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=new_order.order_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price_per_item=cart_item.product.price
        )
        db.add(order_item)

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