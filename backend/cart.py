"""
장바구니 관련 API 엔드포인트
장바구니 조회, 추가, 수량변경, 삭제 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import CartItemAdd, CartItemUpdate, CartItemResponse, CartResponse, MessageResponse, UserResponse
from crud import (
    get_cart_items, add_to_cart, update_cart_item, 
    remove_from_cart, clear_cart, get_product_by_id
)
from users import get_current_user
from decimal import Decimal
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()

@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    장바구니 조회
    현재 고객의 장바구니 내용 전체 조회
    """
    logger.info(f"🛒 장바구니 조회: 사용자 ID {current_user.user_id}")

    cart_items = get_cart_items(db, current_user.user_id)
    
    # 장바구니 아이템 응답 데이터 생성
    items = []
    total_amount = Decimal('0')
    
    for cart_item in cart_items:
        product = cart_item.product
        item_total = product.price * cart_item.quantity
        total_amount += item_total
        
        items.append(CartItemResponse(
            cart_item_id=cart_item.cart_item_id,
            product_id=cart_item.product_id,
            product_name=product.product_name,
            price=product.price,
            quantity=cart_item.quantity,
            total_price=item_total,
            added_at=cart_item.added_at
        ))
    
    # 조회 결과 로그
    logger.info(f"✅ 장바구니 조회 완료: {len(items)}개 상품, 총 {total_amount:,}원")

    return CartResponse(
        items=items,
        total_items=len(items),
        total_amount=total_amount
    )

@router.post("/items", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_cart_item(
    cart_item: CartItemAdd,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    장바구니에 상품 추가
    장바구니에 특정 옵션의 상품을 추가
    이미 있는 상품이면 수량 증가, 없으면 새로 추가
    """
    logger.info(f"장바구니 추가: 사용자 ID {current_user.user_id}, 상품 ID {cart_item.product_id}")
    
    # 상품 존재 확인
    product = get_product_by_id(db, cart_item.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 상품입니다."
        )
    
    # 수량 유효성 검사
    if cart_item.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수량은 1개 이상이어야 합니다."
        )
    
    try:
        cart_result = add_to_cart(db, current_user.user_id, cart_item)
        success_message = f"✅ 장바구니 추가 성공: {product.product_name} x {cart_item.quantity}개 (총 가격: {product.price * cart_item.quantity:,}원)"
        logger.info(success_message)
        return MessageResponse(message=success_message)

    except Exception as e:
        error_message = f"❌ 장바구니 추가 실패: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )

@router.put("/items/{variant_id}", response_model=MessageResponse)
async def update_cart_quantity(
    variant_id: int,
    cart_update: CartItemUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    장바구니 수량 변경
    장바구니에 담긴 상품의 수량 업데이트
    """
    logger.info(f"장바구니 수량 변경: 사용자 ID {current_user.user_id}, 상품 ID {variant_id}")

    # 수량 유효성 검사
    if cart_update.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수량은 1개 이상이어야 합니다."
        )

    # 장바구니 아이템 수량 변경
    updated_item = update_cart_item(db, current_user.user_id, variant_id, cart_update.quantity)

    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ 장바구니에서 해당 상품을 찾을 수 없습니다."
        )

    # 상품 정보 조회해서 상세 메시지 생성
    product = get_product_by_id(db, variant_id)
    new_total = product.price * cart_update.quantity if product else 0
    success_message = f"✅ 수량 변경 성공: {product.product_name if product else f'상품 ID {variant_id}'} → {cart_update.quantity}개 (총 가격: {new_total:,}원)"
    logger.info(success_message)
    return MessageResponse(message=success_message)

@router.delete("/items/{variant_id}", response_model=MessageResponse)
async def remove_cart_item(
    variant_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    장바구니 제거
    장바구니에서 특정 상품을 제거
    """
    logger.info(f"장바구니 삭제: 사용자 ID {current_user.user_id}, 상품 ID {variant_id}")

    # 삭제 전에 상품 정보 조회
    product = get_product_by_id(db, variant_id)
    product_name = product.product_name if product else f"상품 ID {variant_id}"

    success = remove_from_cart(db, current_user.user_id, variant_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"❌ 장바구니에서 {product_name}을(를) 찾을 수 없습니다."
        )

    success_message = f"✅ 삭제 성공: {product_name}이(가) 장바구니에서 제거되었습니다."
    logger.info(success_message)
    return MessageResponse(message=success_message)

