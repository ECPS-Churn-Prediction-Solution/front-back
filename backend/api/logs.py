import logging
import logging.handlers
import os
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Query, Path

# --- Logger Setup ---
# LogBack/Log4j와 유사한 파일 기반 로깅을 설정합니다.
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_format = "% (asctime)s\t%(message)s"
date_format = "%Y-%m-%dT%H:%M:%S%z"

# 이벤트 로거 설정
event_logger = logging.getLogger("event_logger")
event_logger.setLevel(logging.INFO)

# 10MB 크기의 5개 파일을 순환 사용하는 핸들러
handler = logging.handlers.RotatingFileHandler(
    os.path.join(LOG_DIR, "events.log"),
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
formatter = logging.Formatter(log_format, datefmt=date_format)
handler.setFormatter(formatter)
event_logger.addHandler(handler)
event_logger.propagate = False

# --- Router ---
router = APIRouter(
    prefix="/log",
    tags=["Logging"],
)

# --- Helper Functions ---
def get_product_info(product_id: int) -> Dict[str, Any]:
    """DB 대신 임시로 상품 정보를 반환하는 더미 함수"""
    return {
        "product_id": product_id,
        "name": f"Sample Product {product_id}",
        "category": "Sample Category",
        "price": (product_id % 100) * 1000,
    }

def log_event(log_type: str, request: Request, data: Dict[str, Any]):
    """
    탭으로 구분된 형식의 로그 메시지를 생성하고 기록합니다.
    """
    # 공통 필드
    base_data = {
        "log_type": log_type,
        "method": request.method,
        "url": str(request.url),
        "user_id": data.get("user_id"),
        "client_ip": request.client.host if request.client else "N/A",
    }

    # UTM 파라미터 추가
    utm_params = {key: request.query_params.get(key) for key in ["utm_source", "utm_medium", "utm_campaign", "utm_content"]}
    
    # 모든 데이터를 합칩니다.
    full_log_data = {**base_data, **utm_params, **data}
    
    # JSON 필드를 문자열로 변환
    if "product_info" in full_log_data and full_log_data["product_info"]:
        full_log_data["product_info"] = json.dumps(full_log_data["product_info"], ensure_ascii=False)
    
    # 탭으로 구분된 문자열 생성
    log_message = "\t".join(str(v) for v in full_log_data.values())
    event_logger.info(log_message)


# --- API Endpoints ---

@router.get("/product/view/{product_id}")
async def log_product_view(
    request: Request,
    product_id: int = Path(..., title="Product ID"),
    user_id: Optional[str] = Query(None, title="User ID"),
):
    """
    사용자가 특정 상품의 상세 페이지를 조회했을 때 호출됩니다.

    **Example (curl):**
    ```bash
    curl -X GET "http://localhost:8000/log/product/view/123?user_id=user01&utm_source=google&utm_medium=cpc"
    ```
    """
    log_data = {
        "user_id": user_id,
        "product_id": product_id,
        "product_info": get_product_info(product_id),
    }
    log_event("product_view", request, log_data)
    return {"status": "logged"}

@router.get("/cart/add")
async def log_cart_add(
    request: Request,
    user_id: Optional[str] = Query(None, title="User ID"),
    product_id: int = Query(..., title="Product ID"),
    quantity: int = Query(1, title="Product Quantity"),
    options: Optional[str] = Query(None, title="JSON string for product options"),
):
    """
    사용자가 장바구니에 상품을 담는 행동을 기록합니다.

    **Example (curl):**
    ```bash
    # options의 JSON은 URL 인코딩 필요
    curl -X GET 'http://localhost:8000/log/cart/add?user_id=user01&product_id=456&quantity=2&options=%7B%22color%22:%22red%22%7D'
    ```
    """
    log_data = {
        "user_id": user_id,
        "product_id": product_id,
        "product_info": get_product_info(product_id),
        "quantity": quantity,
        "options": json.loads(options) if options else {},
    }
    log_event("cart_add", request, log_data)
    return {"status": "logged"}

@router.get("/order/place/prepare")
async def log_order_prepare(
    request: Request,
    user_id: Optional[str] = Query(None, title="User ID"),
    cart_id: Optional[str] = Query(None, title="Cart ID"),
    product_id: int = Query(..., title="Product ID"),
    price: float = Query(..., title="Total Price"),
):
    """
    사용자의 주문이 발생했음을 기록합니다 (결제 전).

    **Example (curl):**
    ```bash
    curl -X GET "http://localhost:8000/log/order/place/prepare?user_id=user01&cart_id=cart123&product_id=789&price=100000"
    ```
    """
    log_data = {
        "user_id": user_id,
        "cart_id": cart_id,
        "product_id": product_id,
        "product_info": get_product_info(product_id),
        "is_paid": 0,
        "price": price,
    }
    log_event("order_prepare", request, log_data)
    return {"status": "logged"}

@router.get("/payment/status/{status_id}")
async def log_payment_status(
    request: Request,
    status_id: int = Path(..., title="Status ID (-1: pending, 0: fail, 1: success)"),
    user_id: Optional[str] = Query(None, title="User ID"),
    order_id: str = Query(..., title="Order ID"),
    payment_method: str = Query(..., title="Payment Method"),
    price_total: float = Query(..., title="Total Price"),
    coupon_id: Optional[str] = Query(None, title="Coupon ID"),
):
    """
    결제 상태 변경을 기록합니다.

    **Example (curl):**
    ```bash
    curl -X GET "http://localhost:8000/log/payment/status/1?user_id=user01&order_id=order555&payment_method=credit_card&price_total=125000&coupon_id=SUMMER2024"
    ```
    """
    log_data = {
        "user_id": user_id,
        "order_id": order_id,
        "status_id": status_id,
        "payment_method": payment_method,
        "price_total": price_total,
        "coupon_id": coupon_id,
    }
    log_event("payment_status", request, log_data)
    return {"status": "logged"}

@router.get("/order/place/paid")
async def log_order_paid(
    request: Request,
    user_id: Optional[str] = Query(None, title="User ID"),
    cart_id: Optional[str] = Query(None, title="Cart ID"),
    product_id: int = Query(..., title="Product ID"),
    payment_id: str = Query(..., title="Payment ID"),
    price: float = Query(..., title="Total Price"),
):
    """
    사용자의 주문이 결제 완료되었음을 기록합니다.

    **Example (curl):**
    ```bash
    curl -X GET "http://localhost:8000/log/order/place/paid?user_id=user01&cart_id=cart123&product_id=789&payment_id=pay_abcde12345&price=125000"
    ```
    """
    log_data = {
        "user_id": user_id,
        "cart_id": cart_id,
        "product_id": product_id,
        "product_info": get_product_info(product_id),
        "payment_id": payment_id,
        "is_paid": 1,
        "price": price,
    }
    log_event("order_paid", request, log_data)
    return {"status": "logged"}

@router.get("/shipping/status/{status_id}")
async def log_shipping_status(
    request: Request,
    status_id: int = Path(..., title="Status ID (-1: shipping, 0: fail, 1: delivered)"),
    user_id: Optional[str] = Query(None, title="User ID"),
    order_id: str = Query(..., title="Order ID"),
    shipment_id: str = Query(..., title="Shipment ID"),
):
    """
    배송 상태 변경을 기록합니다.

    **Example (curl):**
    ```bash
    curl -X GET "http://localhost:8000/log/shipping/status/-1?user_id=user01&order_id=order555&shipment_id=ship_xyz789"
    ```
    """
    log_data = {
        "user_id": user_id,
        "order_id": order_id,
        "shipment_id": shipment_id,
        "status_id": status_id,
    }
    log_event("shipping_status", request, log_data)
    return {"status": "logged"}
