"""
주문 관련 API 엔드포인트
주문 생성, 조회, 상세 조회 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import (
    OrderCreateRequest, OrderResponse, OrderListResponse,
    MessageResponse, UserResponse, OrderItemResponse, DirectOrderRequest,
    OrderSuccessResponse
)
from db.crud import (
    create_order_from_cart, get_user_orders, get_order_by_id, create_direct_order
)
from api.users import get_current_user
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
        # 입력 데이터 검증
        if not order_data.recipient_name or not order_data.recipient_name.strip():
            raise ValueError("수령인 이름은 필수입니다.")

        if not order_data.phone_number or not order_data.phone_number.strip():
            raise ValueError("연락처는 필수입니다.")

        if not order_data.shipping_address or not order_data.shipping_address.address_main:
            raise ValueError("배송 주소는 필수입니다.")

        # 장바구니를 바탕으로 주문 생성
        new_order = create_order_from_cart(db, current_user.user_id, order_data)

        if not new_order:
            raise ValueError("주문 생성에 실패했습니다.")

        # 안전한 타입 변환
        try:
            total_amount_int = int(new_order.total_amount) if new_order.total_amount else 0
        except (ValueError, TypeError):
            total_amount_int = 0

        # 배송 상태 안전 처리
        order_status = new_order.status.value if hasattr(new_order.status, 'value') else str(new_order.status)

        # 성공 메시지 (터미널용)
        success_message = f"✅ 주문 생성 성공! 주문번호: {new_order.order_id}, 총 금액: {total_amount_int:,}원"
        logger.info(success_message)

        # Swagger Response body에 표시될 응답
        # 배송비는 총액과 상품합계 차액으로 계산 (정책상 3000원)
        shipping_fee = int(getattr(new_order, 'shipping_fee', 0) or 0)

        return OrderSuccessResponse(
            order_id=new_order.order_id,
            order_date=new_order.order_date,
            status=order_status,  # 배송 상태
            total_amount=total_amount_int,
            shipping_fee=shipping_fee,
            message="주문이 성공적으로 완료되었습니다."
        )

    except ValueError as e:
        # 장바구니 비어있음 등의 비즈니스 로직 오류
        error_message = f"주문 생성 실패: {str(e)}"
        logger.warning(f"❌ {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    except HTTPException:
        # 이미 처리된 HTTP 예외는 다시 발생
        raise
    except Exception as e:
        # 예상치 못한 서버 오류
        error_message = f"주문 생성 중 서버 오류가 발생했습니다."
        logger.error(f"❌ {error_message}: {str(e)}")
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
    try:
        # 터미널용 로그
        logger.info(f"📋 주문 내역 조회: 사용자 ID {current_user.user_id}")

        orders = get_user_orders(db, current_user.user_id)

        if orders is None:
            orders = []

        # 주문 응답 데이터 생성
        order_responses = []
        total_amount_sum = 0

        for order in orders:
            try:
                # 주문 상품들 조회
                order_items = []
                if hasattr(order, 'order_items') and order.order_items:
                    for item in order.order_items:
                        try:
                            # 안전한 타입 변환
                            price_per_item = int(item.price_per_item) if item.price_per_item else 0
                            quantity = int(item.quantity) if item.quantity else 0
                            total_price = price_per_item * quantity

                            # 상품명 안전 처리
                            product_name = "상품명 없음"
                            product_id = 0
                            if hasattr(item, 'variant') and item.variant and hasattr(item.variant, 'product'):
                                if item.variant.product and hasattr(item.variant.product, 'product_name'):
                                    product_name = item.variant.product.product_name or "상품명 없음"
                                    product_id = item.variant.product.product_id

                            order_items.append(OrderItemResponse(
                                order_item_id=item.order_item_id,
                                variant_id=item.variant_id,
                                product_id=product_id,
                                product_name=product_name,
                                quantity=quantity,
                                price_per_item=price_per_item,
                                total_price=total_price
                            ))
                        except Exception as e:
                            logger.warning(f"주문 상품 처리 중 오류: {str(e)}")
                            continue

                # 배송 주소 안전 조합
                address_main = order.address_main or ""
                address_detail = order.address_detail or ""
                full_address = f"{address_main}, {address_detail}".strip(", ") if address_detail else address_main

                # 주문 총액 안전 처리
                order_total = int(order.total_amount) if order.total_amount else 0
                total_amount_sum += order_total

                # 배송 상태 안전 처리
                order_status = order.status.value if hasattr(order.status, 'value') else str(order.status)

                # 배송비 계산: 총액 - 상품합계
                shipping_fee = int(getattr(order, 'shipping_fee', 0) or 0)

                order_responses.append(OrderResponse(
                    order_id=order.order_id,
                    user_id=order.user_id,
                    order_date=order.order_date,
                    total_amount=order_total,
                    shipping_fee=shipping_fee,
                    status=order_status,
                    shopping_address=full_address,
                    items=order_items
                ))

            except Exception as e:
                logger.warning(f"주문 처리 중 오류 (주문 ID: {getattr(order, 'order_id', 'Unknown')}): {str(e)}")
                continue

        # 터미널용 로그
        logger.info(f"✅ 주문 내역 조회 완료: {len(order_responses)}개 주문, 총 주문금액: {total_amount_sum:,}원")

        return OrderListResponse(
            orders=order_responses,
            total_orders=len(order_responses)
        )

    except Exception as e:
        error_message = "주문 내역 조회 중 오류가 발생했습니다."
        logger.error(f"❌ {error_message}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
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
    try:
        # 입력 검증
        if order_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효하지 않은 주문 ID입니다."
            )

        # 터미널용 로그
        logger.info(f"🔍 주문 상세 조회: 사용자 ID {current_user.user_id}, 주문 ID {order_id}")

        order = get_order_by_id(db, current_user.user_id, order_id)

        if not order:
            error_message = f"주문을 찾을 수 없습니다. (주문 ID: {order_id})"
            logger.warning(f"❌ {error_message}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )

        # 주문 상품들 안전 조회
        order_items = []
        if hasattr(order, 'order_items') and order.order_items:
            for item in order.order_items:
                try:
                    # 안전한 타입 변환
                    price_per_item = int(item.price_per_item) if item.price_per_item else 0
                    quantity = int(item.quantity) if item.quantity else 0
                    total_price = price_per_item * quantity

                    # 상품명 안전 처리
                    product_name = "상품명 없음"
                    product_id = 0
                    if hasattr(item, 'variant') and item.variant and hasattr(item.variant, 'product'):
                        if item.variant.product and hasattr(item.variant.product, 'product_name'):
                            product_name = item.variant.product.product_name or "상품명 없음"
                            product_id = item.variant.product.product_id

                    order_items.append(OrderItemResponse(
                        order_item_id=item.order_item_id,
                        variant_id=item.variant_id,
                        product_id=product_id,
                        product_name=product_name,
                        quantity=quantity,
                        price_per_item=price_per_item,
                        total_price=total_price
                    ))
                except Exception as e:
                    logger.warning(f"주문 상품 처리 중 오류: {str(e)}")
                    continue

        # 안전한 타입 변환
        try:
            total_amount_int = int(order.total_amount) if order.total_amount else 0
        except (ValueError, TypeError):
            total_amount_int = 0

        # 터미널용 로그
        logger.info(f"✅ 주문 상세 조회 완료: 주문 ID {order_id}, 상품 {len(order_items)}개, 총 금액 {total_amount_int:,}원")

        # 배송 주소 안전 조합
        address_main = order.address_main or ""
        address_detail = order.address_detail or ""
        full_address = f"{address_main}, {address_detail}".strip(", ") if address_detail else address_main

        # 배송 상태 안전 처리
        order_status = order.status.value if hasattr(order.status, 'value') else str(order.status)

        shipping_fee = int(getattr(order, 'shipping_fee', 0) or 0)
        return OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_date=order.order_date,
            total_amount=total_amount_int,
            shipping_fee=shipping_fee,
            status=order_status,
            shopping_address=full_address,
            items=order_items
        )

    except HTTPException:
        # 이미 처리된 HTTP 예외는 다시 발생
        raise
    except Exception as e:
        error_message = "주문 상세 조회 중 오류가 발생했습니다."
        logger.error(f"❌ {error_message}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
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
    try:
        # 입력 데이터 검증
        if not order_data.variant_id or order_data.variant_id <= 0:
            raise ValueError("유효하지 않은 상품 옵션 ID입니다.")

        if not order_data.quantity or order_data.quantity <= 0:
            raise ValueError("주문 수량은 1개 이상이어야 합니다.")

        if order_data.quantity > 100:  # 최대 주문 수량 제한
            raise ValueError("한 번에 주문할 수 있는 최대 수량은 100개입니다.")

        if not order_data.recipient_name or not order_data.recipient_name.strip():
            raise ValueError("수령인 이름은 필수입니다.")

        if not order_data.phone_number or not order_data.phone_number.strip():
            raise ValueError("연락처는 필수입니다.")

        if not order_data.shipping_address or not order_data.shipping_address.address_main:
            raise ValueError("배송 주소는 필수입니다.")

        # 터미널용 로그
        logger.info(f"🚀 즉시 주문 시도: 사용자 ID {current_user.user_id}, 상품 옵션 ID {order_data.variant_id}, 수량 {order_data.quantity}")

        # 즉시 주문 생성
        new_order = create_direct_order(db, current_user.user_id, order_data)

        if not new_order:
            raise ValueError("주문 생성에 실패했습니다.")

        # 안전한 타입 변환
        try:
            total_amount_int = int(new_order.total_amount) if new_order.total_amount else 0
        except (ValueError, TypeError):
            total_amount_int = 0

        # 배송 상태 안전 처리
        order_status = new_order.status.value if hasattr(new_order.status, 'value') else str(new_order.status)

        # 성공 메시지 (터미널용)
        success_message = f"✅ 즉시 주문 성공! 주문번호: {new_order.order_id}, 상품 수량: {order_data.quantity}개, 총 금액: {total_amount_int:,}원"
        logger.info(success_message)

        # Swagger Response body에 표시될 응답
        shipping_fee = int(getattr(new_order, 'shipping_fee', 0) or 0)
        return OrderSuccessResponse(
            order_id=new_order.order_id,
            order_date=new_order.order_date,
            status=order_status,  # 배송 상태
            total_amount=total_amount_int,
            shipping_fee=shipping_fee,
            message="주문이 성공적으로 완료되었습니다."
        )

    except ValueError as e:
        # 상품 없음, 재고 부족 등의 비즈니스 로직 오류
        error_message = f"즉시 주문 실패: {str(e)}"
        logger.warning(f"❌ {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    except HTTPException:
        # 이미 처리된 HTTP 예외는 다시 발생
        raise
    except Exception as e:
        # 예상치 못한 서버 오류
        error_message = "즉시 주문 중 서버 오류가 발생했습니다."
        logger.error(f"❌ {error_message}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )
