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
from datetime import date, timedelta, datetime

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


def _hdr_for(dt: datetime) -> dict:
    return {"X-Event-Time": dt.isoformat()}


def _advance(dt: datetime, min_seconds: int = 30, max_seconds: int = 600) -> datetime:
    return dt + timedelta(seconds=random.randint(min_seconds, max_seconds))


async def _track_page_view(client: httpx.AsyncClient, dt: datetime, path: str, referrer: str | None = None) -> None:
    try:
        base = str(getattr(client, "base_url", ""))
        page_url = f"{base}{path}"
        payload = {"event_name": "page_view", "page_url": page_url}
        if referrer:
            payload["referrer"] = referrer
        await client.post("/log/track", json=payload, headers=_hdr_for(dt), timeout=10)
    except Exception:
        pass


async def _fetch_category_ids(client: httpx.AsyncClient, dt: datetime) -> List[int]:
    try:
        r = await client.get("/api/categories/", headers=_hdr_for(dt))
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
    mode: str  # 'new' | 'return'
    reuse: bool
    email_prefix: str
    coupon_prob: float


async def ensure_register_and_login(client: httpx.AsyncClient, email: str, password: str, dt: datetime) -> datetime:
    # 회원가입 시도 (이미 있으면 무시)
    cat_pool = await _fetch_category_ids(client, dt)
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
        await client.post("/api/users/register", json=register_payload, timeout=10, headers=_hdr_for(dt))
    except Exception:
        pass

    # 회원가입 직후 잠시 대기(컨시스턴시/부하 흡수)
    await asyncio.sleep(random.uniform(0.05, 0.2))
    dt = _advance(dt, 10, 120)

    # 로그인 (세션 쿠키 획득) - 지수백오프 재시도
    login_payload = {"email": email, "password": password}
    delay = 0.1
    for attempt in range(5):
        try:
            resp = await client.post("/api/users/login", json=login_payload, timeout=10, headers=_hdr_for(dt))
            resp.raise_for_status()
            break
        except Exception:
            if attempt == 4:
                raise
            await asyncio.sleep(delay)
            delay *= 2
    # 로그인 후 랜딩 페이지 페이지뷰 기록
    dt = _advance(dt, 5, 60)
    await _track_page_view(client, dt, "/")
    dt = _advance(dt, 30, 300)
    return dt


async def login_only(client: httpx.AsyncClient, email: str, password: str, dt: datetime) -> None:
    login_payload = {"email": email, "password": password}
    await client.post("/api/users/login", json=login_payload, timeout=10, headers=_hdr_for(dt))


async def pick_product_and_variant(client: httpx.AsyncClient, dt: datetime) -> Tuple[Optional[dict], datetime]:
    # 상품 목록 페이지뷰 + 목록 API 호출
    await _track_page_view(client, dt, "/products")
    r = await client.get("/api/products/", timeout=10, headers=_hdr_for(dt))
    r.raise_for_status()
    products: List[dict] = r.json() or []
    if not products:
        return None, dt
    product = random.choice(products)

    dt = _advance(dt, 5, 120)
    # 상품 상세 페이지뷰 + 상세 API 호출
    await _track_page_view(client, dt, f"/products/{product['product_id']}")
    d = await client.get(f"/api/products/{product['product_id']}", timeout=10, headers=_hdr_for(dt))
    d.raise_for_status()
    detail = d.json()
    variants = detail.get("variants") or []
    if not variants:
        return None, dt
    variant = random.choice(variants)
    return {
        "product_id": detail["product_id"],
        "variant_id": variant["variant_id"],
        "price": detail.get("price", 0),
        "product_name": detail.get("product_name", "")
    }, dt


async def simulate_single_user(user_idx: int, config: SimulationConfig) -> Tuple[bool, str]:
    # 램프업: 사용자를 시간차로 시작
    if config.ramp_up_ms > 0:
        await asyncio.sleep((user_idx * config.ramp_up_ms) / 1000.0)

    async with httpx.AsyncClient(base_url=config.base_url, follow_redirects=True) as client:
        # 이메일 재사용 옵션: 동일 prefix+index 고정 이메일
        if config.reuse:
            email = f"{config.email_prefix}{user_idx}@example.com"
        else:
            email = _rand_email()
        password = "password123"

        try:
            stage = "login"
            # 시작 시점: 과거(재방문 모드면 60~180일 전, 아니면 0~119일 전)
            if config.mode == "return":
                start_dt = datetime.now().astimezone() - timedelta(days=random.randint(60, 180), minutes=random.randint(0, 1440))
            else:
                start_dt = datetime.now().astimezone() - timedelta(days=random.randint(0, 119), minutes=random.randint(0, 1440))

            # Phase A: 과거 세션(가입/로그인→탐색→장바구니→주문)
            current_dt = await ensure_register_and_login(client, email, password, start_dt)

            browse_count = random.randint(1, config.max_products_to_browse)
            for _ in range(browse_count):
                _, current_dt = await pick_product_and_variant(client, current_dt)
                current_dt = _advance(current_dt, 30, 900)

            stage = "pick_variant"
            pv = None
            for _ in range(max(1, config.variant_retry)):
                pv, current_dt = await pick_product_and_variant(client, current_dt)
                if pv:
                    break
            if pv:
                add_payload = {"variant_id": pv["variant_id"], "quantity": random.randint(1, 3)}
                stage = "cart_add"
                await client.post("/api/cart/items", json=add_payload, timeout=10, headers=_hdr_for(current_dt))

                stage = "cart_view"
                current_dt = _advance(current_dt, 30, 300)
                await _track_page_view(client, current_dt, "/cart")
                current_dt = _advance(current_dt, 30, 900)
                await client.get("/api/cart/", timeout=10, headers=_hdr_for(current_dt))

                stage = "order_create"
                ship_method, ship_fee = _rand_shipping_method_and_fee()
                current_dt = _advance(current_dt, 30, 600)
                await _track_page_view(client, current_dt, "/checkout")
                coupon_code = random.choice(["PROMO10","SALE20","WELCOME5"]) if random.random() < max(0.0, min(1.0, config.coupon_prob)) else ""
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
                    "used_coupon_code": coupon_code,
                    "shipping_method": ship_method,
                    "shipping_fee": ship_fee,
                }
                current_dt = _advance(current_dt, 120, 3600)
                order_resp = await client.post("/api/orders/", json=order_payload, timeout=15, headers=_hdr_for(current_dt))
                order_resp.raise_for_status()

            # Phase B: 재방문 모드면 오늘 세션 추가(로그인→페이지뷰→탐색→주문 확률적으로)
            if config.mode == "return":
                today_dt = datetime.now().astimezone()
                await login_only(client, email, password, today_dt)
                await _track_page_view(client, today_dt, "/")
                tmp_dt = _advance(today_dt, 10, 300)
                _, tmp_dt = await pick_product_and_variant(client, tmp_dt)
                # 70% 확률로 구매 수행
                if random.random() < 0.7:
                    pv2, tmp_dt = await pick_product_and_variant(client, tmp_dt)
                    if pv2:
                        await client.post("/api/cart/items", json={"variant_id": pv2["variant_id"], "quantity": random.randint(1, 2)}, timeout=10, headers=_hdr_for(tmp_dt))
                        tmp_dt = _advance(tmp_dt, 30, 300)
                        await _track_page_view(client, tmp_dt, "/checkout")
                        ship_method, ship_fee = _rand_shipping_method_and_fee()
                        coupon_code2 = random.choice(["PROMO10","SALE20","WELCOME5"]) if random.random() < max(0.0, min(1.0, config.coupon_prob)) else ""
                        order_payload2 = {
                            "recipient_name": _rand_recipient_name(),
                            "shipping_address": {"zip_code": _rand_zip(), "address_main": _rand_address_main(), "address_detail": _rand_address_detail()},
                            "phone_number": _rand_phone(),
                            "shopping_memo": _rand_memo(),
                            "payment_method": _rand_payment_method(),
                            "used_coupon_code": coupon_code2,
                            "shipping_method": ship_method,
                            "shipping_fee": ship_fee,
                        }
                        tmp_dt = _advance(tmp_dt, 60, 900)
                        order_resp2 = await client.post("/api/orders/", json=order_payload2, timeout=15, headers=_hdr_for(tmp_dt))
                        order_resp2.raise_for_status()

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


async def run(users: int, concurrency: int, ramp_ms: int, base_url: str, max_browse: int, progress_every: int, variant_retry: int, debug_limit: int, mode: str, reuse: bool, email_prefix: str, coupon_prob: float = 0.3) -> None:
    config = SimulationConfig(base_url=base_url, ramp_up_ms=ramp_ms, max_products_to_browse=max_browse, variant_retry=variant_retry, debug_limit=debug_limit, mode=mode, reuse=reuse, email_prefix=email_prefix, coupon_prob=coupon_prob)

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
    parser.add_argument("--mode", type=str, choices=["new", "return"], default="return", help="사용자 시나리오: 신규(new) 또는 재방문(return)")
    parser.add_argument("--reuse", action="store_true", help="이메일을 사용자 인덱스 기반으로 재사용")
    parser.add_argument("--email-prefix", type=str, default="simuser-", help="재사용 이메일 prefix (ex: simuser-0@example.com)")
    parser.add_argument("--coupon-prob", type=float, default=0.3, help="쿠폰 사용 확률(0~1). 기본 0.3")

    args = parser.parse_args()

    asyncio.run(run(args.users, args.concurrency, args.ramp, args.host, args.max_browse, args.progress, args.variant_retry, args.debug, args.mode, args.reuse, args.email_prefix, args.coupon_prob))


if __name__ == "__main__":
    main()


