"""
주문 관련 API 엔드포인트
주문 생성, 조회, 상세 조회 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    OrderCreateRequest, OrderResponse, OrderListResponse,
    MessageResponse, UserResponse, OrderItemResponse
)
from crud import (
    create_order_from_cart, get_user_orders, get_order_by_id
)
from users import get_current_user
from decimal import Decimal
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    주문 생성
    장바구니 정보를 바탕으로 신규 주문 생성(결제 처리)
    """
    # 터미널용 로그
    logger.info(f"📦 주문 생성 시도: 사용자 ID {current_user.user_id}")
    
    try:
        # 장바구니를 바탕으로 주문 생성
        new_order = create_order_from_cart(db, current_user.user_id, order_data)
        
        # 성공 메시지 (터미널 + Swagger 둘 다 사용)
        success_message = f"✅ 주문 생성 성공! 주문번호: {new_order.order_id}, 총 금액: {new_order.total_amount:,}원, 배송지: {new_order.shopping_address}"
        logger.info(success_message)
        
        # Swagger Response body에 표시될 메시지
        return MessageResponse(message=success_message)
        
    except ValueError as e:
        # 장바구니 비어있음 등의 비즈니스 로직 오류
        error_message = f"❌ 주문 생성 실패: {str(e)}"
        logger.warning(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    except Exception as e:
        # 예상치 못한 서버 오류
        error_message = f"❌ 주문 생성 중 서버 오류 발생: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )

@router.get("/", response_model=OrderListResponse)
async def get_orders(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    주문 내역 조회
    고객 본인의 전체 주문 내역 목록 반환
    """
    # 터미널용 로그
    logger.info(f"📋 주문 내역 조회: 사용자 ID {current_user.user_id}")

    orders = get_user_orders(db, current_user.user_id)

    # 주문 응답 데이터 생성
    order_responses = []
    for order in orders:
        # 주문 상품들 조회
        order_items = []
        for item in order.order_items:
            order_items.append(OrderItemResponse(
                order_item_id=item.order_item_id,
                product_id=item.product_id,
                product_name=item.product.product_name,
                quantity=item.quantity,
                price_per_item=item.price_per_item,
                total_price=item.price_per_item * item.quantity
            ))

        order_responses.append(OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_date=order.order_date,
            total_amount=order.total_amount,
            status=order.status,
            shopping_address=order.shopping_address,
            items=order_items
        ))

    # 터미널용 로그
    total_amount_sum = sum(order.total_amount for order in orders)
    logger.info(f"✅ 주문 내역 조회 완료: {len(orders)}개 주문, 총 주문금액: {total_amount_sum:,}원")

    return OrderListResponse(
        orders=order_responses,
        total_orders=len(orders)
    )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    주문 상세 조회
    특정 주문의 상세 정보 반환
    """
    # 터미널용 로그
    logger.info(f"🔍 주문 상세 조회: 사용자 ID {current_user.user_id}, 주문 ID {order_id}")

    order = get_order_by_id(db, current_user.user_id, order_id)

    if not order:
        error_message = f"❌ 주문을 찾을 수 없습니다: 주문 ID {order_id}"
        logger.warning(error_message)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message
        )

    # 주문 상품들 조회
    order_items = []
    for item in order.order_items:
        order_items.append(OrderItemResponse(
            order_item_id=item.order_item_id,
            product_id=item.product_id,
            product_name=item.product.product_name,
            quantity=item.quantity,
            price_per_item=item.price_per_item,
            total_price=item.price_per_item * item.quantity
        ))

    # 터미널용 로그
    logger.info(f"✅ 주문 상세 조회 완료: 주문 ID {order_id}, 상품 {len(order_items)}개, 총 금액 {order.total_amount:,}원")

    return OrderResponse(
        order_id=order.order_id,
        user_id=order.user_id,
        order_date=order.order_date,
        total_amount=order.total_amount,
        status=order.status,
        shopping_address=order.shopping_address,
        items=order_items
    )
