"""
대규모 유저 시뮬레이터 (비동기)

- 회원가입(존재시 스킵) → 로그인(세션 쿠키) → 상품 탐색 → 상세 → 장바구니 → 주문 생성
- httpx.AsyncClient + CookieJar 로 세션 유지
- --users, --concurrency, --ramp, --host 옵션 지원
"""

from __future__ import annotations

import asyncio
import random
import string
from dataclasses import dataclass
from typing import Optional, List, Tuple
from datetime import date, timedelta

import httpx


def _rand_email(suffix: str = "example.com") -> str:
    user = "sim" + "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{user}@{suffix}"


def _rand_name() -> str:
    return "user-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


def _rand_gender() -> str:
    return random.choice(["male", "female", "other"])


def _rand_birthdate() -> str:
    # 1970-01-01 ~ 2005-12-31 사이 임의 날짜
    start = date(1970, 1, 1)
    end = date(2005, 12, 31)
    delta_days = (end - start).days
    d = start + timedelta(days=random.randint(0, delta_days))
    return d.isoformat()


def _rand_phone() -> str:
    return f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}"


async def _fetch_category_ids(client: httpx.AsyncClient) -> List[int]:
    try:
        r = await client.get("/api/categories/")
        r.raise_for_status()
        cats = r.json() or []
        return [c.get("category_id") for c in cats if c.get("category_id") is not None]
    except Exception:
        return []


def _rand_zip() -> str:
    return f"{random.randint(10000,99999)}"


def _rand_address_main() -> str:
    cities = [
        "서울 강남구 테헤란로",
        "서울 서초구 서초대로",
        "서울 마포구 월드컵북로",
        "서울 송파구 올림픽로",
        "부산 해운대구 해운대로",
        "대구 수성구 달구벌대로",
        "대전 유성구 대학로",
        "광주 서구 상무대로",
    ]
    return f"{random.choice(cities)} {random.randint(1,999)}"


def _rand_address_detail() -> str:
    return f"{random.randint(1,50)}층 {random.randint(101,200)}호"


def _rand_recipient_name() -> str:
    family = ["김", "이", "박", "최", "정", "조", "강", "윤", "장", "임"]
    given = ["민준", "서연", "지호", "예은", "도윤", "하은", "지우", "현우", "서준", "수빈"]
    return random.choice(family) + random.choice(given)


def _rand_memo() -> str:
    memos = [
        "부재 시 경비실",
        "문 앞에 놓아주세요",
        "연락 주세요",
        "벨 누르지 말아주세요",
        "빠른 배송 부탁드립니다",
        "낮 시간대 배송 희망",
        "파손주의",
    ]
    return random.choice(memos)


def _rand_payment_method() -> str:
    return random.choice(["credit_card", "cash"])


def _rand_shipping_method_and_fee() -> Tuple[str, float]:
    method = random.choice(["standard", "express"])
    fee = 3000.0 if method == "standard" else 5000.0
    return method, fee


@dataclass
class SimulationConfig:
    base_url: str
    ramp_up_ms: int
    max_products_to_browse: int
    variant_retry: int
    debug_limit: int


async def ensure_register_and_login(client: httpx.AsyncClient, email: str, password: str) -> None:
    # 회원가입 시도 (이미 있으면 무시)
    cat_pool = await _fetch_category_ids(client)
    interests: List[int] = []
    if cat_pool:
        k = random.randint(0, min(3, len(cat_pool)))
        interests = random.sample(cat_pool, k)
    register_payload = {
        "email": email,
        "password": password,
        "user_name": _rand_name(),
        "gender": _rand_gender(),
        "birthdate": _rand_birthdate(),
        "phone_number": _rand_phone(),
        "interest_categories": interests,
    }
    try:
        await client.post("/api/users/register", json=register_payload, timeout=10)
    except Exception:
        pass

    # 회원가입 직후 잠시 대기(컨시스턴시/부하 흡수)
    await asyncio.sleep(random.uniform(0.05, 0.2))

    # 로그인 (세션 쿠키 획득) - 지수백오프 재시도
    login_payload = {"email": email, "password": password}
    delay = 0.1
    for attempt in range(5):
        try:
            resp = await client.post("/api/users/login", json=login_payload, timeout=10)
            resp.raise_for_status()
            break
        except Exception:
            if attempt == 4:
                raise
            await asyncio.sleep(delay)
            delay *= 2


async def pick_product_and_variant(client: httpx.AsyncClient) -> Optional[dict]:
    r = await client.get("/api/products/", timeout=10)
    r.raise_for_status()
    products: List[dict] = r.json() or []
    if not products:
        return None
    product = random.choice(products)

    d = await client.get(f"/api/products/{product['product_id']}", timeout=10)
    d.raise_for_status()
    detail = d.json()
    variants = detail.get("variants") or []
    if not variants:
        return None
    variant = random.choice(variants)
    return {
        "product_id": detail["product_id"],
        "variant_id": variant["variant_id"],
        "price": detail.get("price", 0),
        "product_name": detail.get("product_name", "")
    }


async def simulate_single_user(user_idx: int, config: SimulationConfig) -> Tuple[bool, str]:
    # 램프업: 사용자를 시간차로 시작
    if config.ramp_up_ms > 0:
        await asyncio.sleep((user_idx * config.ramp_up_ms) / 1000.0)

    async with httpx.AsyncClient(base_url=config.base_url, follow_redirects=True) as client:
        email = _rand_email()
        password = "password123"

        try:
            stage = "login"
            await ensure_register_and_login(client, email, password)

            # 탐색: 상품 n개 랜덤 조회(목록/상세)
            browse_count = random.randint(1, config.max_products_to_browse)
            for _ in range(browse_count):
                _ = await pick_product_and_variant(client)

            # 장바구니 담기 대상 선택
            stage = "pick_variant"
            pv = None
            for _ in range(max(1, config.variant_retry)):
                pv = await pick_product_and_variant(client)
                if pv:
                    break
            if not pv:
                return False, "no_variant"

            add_payload = {"variant_id": pv["variant_id"], "quantity": random.randint(1, 3)}
            stage = "cart_add"
            await client.post("/api/cart/items", json=add_payload, timeout=10)

            # 장바구니 조회
            stage = "cart_view"
            await client.get("/api/cart/", timeout=10)

            # 주문 생성
            stage = "order_create"
            ship_method, ship_fee = _rand_shipping_method_and_fee()
            order_payload = {
                "recipient_name": _rand_recipient_name(),
                "shipping_address": {
                    "zip_code": _rand_zip(),
                    "address_main": _rand_address_main(),
                    "address_detail": _rand_address_detail(),
                },
                "phone_number": _rand_phone(),
                "shopping_memo": _rand_memo(),
                "payment_method": _rand_payment_method(),
                "used_coupon_code": "",
                "shipping_method": ship_method,
                "shipping_fee": ship_fee,
            }
            order_resp = await client.post("/api/orders/", json=order_payload, timeout=15)
            order_resp.raise_for_status()
            return True, "ok"

        except httpx.HTTPStatusError as e:
            # 4xx/5xx는 조용히 무시 (대량 시뮬 중 일부 실패 허용)
            try:
                status = e.response.status_code
            except Exception:
                status = "?"
            return False, f"{stage}:{status}"
        except Exception:
            return False, stage


async def run(users: int, concurrency: int, ramp_ms: int, base_url: str, max_browse: int, progress_every: int, variant_retry: int, debug_limit: int) -> None:
    config = SimulationConfig(base_url=base_url, ramp_up_ms=ramp_ms, max_products_to_browse=max_browse, variant_retry=variant_retry, debug_limit=debug_limit)

    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    stats = {"done": 0, "success": 0, "fail": 0}
    error_samples: List[str] = []

    print(f"[simulate] start users={users} concurrency={concurrency} ramp_ms={ramp_ms} host={base_url}")

    async def _guarded(idx: int):
        async with sem:
            ok, reason = await simulate_single_user(idx, config)
            async with lock:
                stats["done"] += 1
                if ok:
                    stats["success"] += 1
                else:
                    stats["fail"] += 1
                    if len(error_samples) < config.debug_limit:
                        error_samples.append(reason)
                if progress_every > 0 and stats["done"] % progress_every == 0:
                    if error_samples:
                        print(f"[progress] done={stats['done']}/{users} success={stats['success']} fail={stats['fail']} sample_errors={error_samples}")
                        error_samples.clear()
                    else:
                        print(f"[progress] done={stats['done']}/{users} success={stats['success']} fail={stats['fail']}")

    tasks = [_guarded(i) for i in range(users)]
    await asyncio.gather(*tasks)
    print(f"[summary] total={users} success={stats['success']} fail={stats['fail']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Async user simulation for shopping flow")
    parser.add_argument("--users", type=int, default=1000, help="총 사용자 수")
    parser.add_argument("--concurrency", type=int, default=100, help="동시 실행 최대 수")
    parser.add_argument("--ramp", type=int, default=10, help="사용자별 램프업 간격(ms)")
    parser.add_argument("--host", type=str, default="http://localhost:8000", help="백엔드 베이스 URL")
    parser.add_argument("--max-browse", type=int, default=3, help="상품 탐색(상세 조회) 최대 횟수")
    parser.add_argument("--progress", type=int, default=50, help="몇 명 완료될 때마다 진행률 출력")
    parser.add_argument("--variant-retry", type=int, default=7, help="옵션 선택 재시도 횟수")
    parser.add_argument("--debug", type=int, default=5, help="진행률 출력 시 표본 에러 메시지 최대 개수")

    args = parser.parse_args()

    asyncio.run(run(args.users, args.concurrency, args.ramp, args.host, args.max_browse, args.progress, args.variant_retry, args.debug))


if __name__ == "__main__":
    main()


