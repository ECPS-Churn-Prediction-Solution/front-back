"""
주문 관련 API 엔드포인트
주문 생성, 조회, 상세 조회 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    OrderCreateRequest, OrderResponse, OrderListResponse,
    MessageResponse, UserResponse, OrderItemResponse, DirectOrderRequest,
    OrderSuccessResponse, CustomerOrderInfo, ShippingAddress
)
from crud import (
    create_order_from_cart, get_user_orders, get_order_by_id, create_direct_order
)
from users import get_current_user
from decimal import Decimal
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()

@router.post("/", response_model=OrderSuccessResponse, status_code=status.HTTP_201_CREATED)
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
        total_amount_int = int(new_order.total_amount)
        success_message = f"✅ 주문 생성 성공! 주문번호: {new_order.order_id}, 총 금액: {total_amount_int:,}원"
        logger.info(success_message)

        # 고객 주문 정보 생성
        customer_info = CustomerOrderInfo(
            recipient_name=new_order.recipient_name,
            shipping_address=ShippingAddress(
                zip_code=new_order.zip_code,
                address_main=new_order.address_main,
                address_detail=new_order.address_detail
            ),
            phone_number=new_order.phone_number,
            shopping_memo=new_order.shopping_memo,
            payment_method=new_order.payment_method,
            used_coupon_code=new_order.used_coupon_code
        )

        # Swagger Response body에 표시될 메시지 + 고객 정보
        return OrderSuccessResponse(
            message=success_message,
            customer_info=customer_info
        )
        
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
                price_per_item=int(item.price_per_item),
                total_price=int(item.price_per_item * item.quantity)
            ))

        # 배송 주소 조합
        full_address = f"{order.address_main}, {order.address_detail}" if order.address_detail else order.address_main

        order_responses.append(OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_date=order.order_date,
            total_amount=int(order.total_amount),
            status=order.status,
            shopping_address=full_address,
            items=order_items
        ))

    # 터미널용 로그
    total_amount_sum = sum(int(order.total_amount) for order in orders)
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
            price_per_item=int(item.price_per_item),
            total_price=int(item.price_per_item * item.quantity)
        ))

    # 터미널용 로그
    total_amount_int = int(order.total_amount)
    logger.info(f"✅ 주문 상세 조회 완료: 주문 ID {order_id}, 상품 {len(order_items)}개, 총 금액 {total_amount_int:,}원")

    # 배송 주소 조합
    full_address = f"{order.address_main}, {order.address_detail}" if order.address_detail else order.address_main

    return OrderResponse(
        order_id=order.order_id,
        user_id=order.user_id,
        order_date=order.order_date,
        total_amount=int(order.total_amount),
        status=order.status,
        shopping_address=full_address,
        items=order_items
    )

@router.post("/direct", response_model=OrderSuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_direct_order_api(
    order_data: DirectOrderRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    즉시 주문 생성
    장바구니를 거치지 않고 상품을 바로 주문
    """
    # 터미널용 로그
    logger.info(f"🚀 즉시 주문 시도: 사용자 ID {current_user.user_id}, 상품 ID {order_data.product_id}, 수량 {order_data.quantity}")

    try:
        # 즉시 주문 생성
        new_order = create_direct_order(db, current_user.user_id, order_data)

        # 성공 메시지 (터미널 + Swagger 둘 다 사용)
        total_amount_int = int(new_order.total_amount)
        success_message = f"✅ 즉시 주문 성공! 주문번호: {new_order.order_id}, 상품 수량: {order_data.quantity}개, 총 금액: {total_amount_int:,}원"
        logger.info(success_message)

        # 고객 주문 정보 생성
        customer_info = CustomerOrderInfo(
            recipient_name=new_order.recipient_name,
            shipping_address=ShippingAddress(
                zip_code=new_order.zip_code,
                address_main=new_order.address_main,
                address_detail=new_order.address_detail
            ),
            phone_number=new_order.phone_number,
            shopping_memo=new_order.shopping_memo,
            payment_method=new_order.payment_method,
            used_coupon_code=new_order.used_coupon_code
        )

        # Swagger Response body에 표시될 메시지 + 고객 정보
        return OrderSuccessResponse(
            message=success_message,
            customer_info=customer_info
        )

    except ValueError as e:
        # 상품 없음, 재고 부족 등의 비즈니스 로직 오류
        error_message = f"❌ 즉시 주문 실패: {str(e)}"
        logger.warning(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    except Exception as e:
        # 예상치 못한 서버 오류
        error_message = f"❌ 즉시 주문 중 서버 오류 발생: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )
