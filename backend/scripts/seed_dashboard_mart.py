"""
대시보드용 마트 테이블 더미 데이터 삽입 스크립트

대상 테이블(스키마 포함):
- mart.daily_churn_kpi(report_dt, customers_total, churn_rate, retention_rate, churn_customers[, horizon_days?])
- mart.churn_risk_distribution(report_dt, risk_band, user_count, ratio, horizon_days)
- mart.churn_segment_aggr(report_dt, segment_key, customers, churn_rate, horizon_days)
- mart.high_risk_users(report_dt, user_id, risk_band, churn_probability, action_code, horizon_days)
- analytics.action_recommendations(risk_band, action_code, policy_name)
- mart.refresh_queue(report_dt, enqueued_at)

주의:
- 실제 RDS 스키마와 일부 컬럼이 다를 수 있어 컬럼 존재 여부를 동적으로 점검하여 WHERE/INSERT 컬럼을 조정합니다.
- 동일 report_dt(+horizon_days) 데이터가 있으면 삭제 후 삽입합니다.(idempotent)

사용법 예시(기본: 오늘 날짜, 시드 42):
  python -m backend.scripts.seed_dashboard_mart --report-dt 2025-08-29 --seed 42
"""

from __future__ import annotations

import argparse
import logging
import math
import random
from datetime import date, datetime, timezone
from typing import Dict, Iterable, List, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.database import engine  # noqa: E402


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


RISK_BANDS: List[str] = ["VH", "H", "M", "L"]
DEFAULT_SEGMENTS: List[str] = ["High(10-12)", "Mid(7-9)", "Low(3-6)"]
DEFAULT_HORIZONS: List[int] = [1, 7, 15, 30]


def fetch_existing_columns(session: Session, schema_name: str, table_name: str) -> List[str]:
    """정보 스키마에서 컬럼 목록을 조회한다(PostgreSQL/SQLite 호환)."""
    try:
        # PostgreSQL 정보스키마
        rows = session.execute(
            text(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = :schema AND table_name = :table
                ORDER BY ordinal_position
                """
            ),
            {"schema": schema_name, "table": table_name},
        ).fetchall()
        if rows:
            return [r[0] for r in rows]
    except Exception:
        pass

    # SQLite의 경우 스키마 개념이 달라 pragma 사용(로컬 개발 대응)
    try:
        rows = session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
        if rows:
            return [r[1] for r in rows]
    except Exception:
        pass
    return []


def delete_existing(session: Session, fq_table: str, where_cols: Dict[str, object]) -> None:
    """조건에 맞는 기존 행 삭제. 컬럼 존재 여부를 확인하여 안전하게 처리한다."""
    schema_name, table_name = fq_table.split(".")
    cols = fetch_existing_columns(session, schema_name, table_name)
    valid_items = [(k, v) for k, v in where_cols.items() if k in cols]
    if not valid_items:
        # 조건 컬럼이 하나도 없으면 전체 삭제를 방지하기 위해 패스
        return
    where_clause = " AND ".join([f"{k} = :{k}" for k, _ in valid_items])
    params = {k: v for k, v in valid_items}
    session.execute(text(f"DELETE FROM {fq_table} WHERE {where_clause}"), params)


def upsert_policy_reference(session: Session) -> None:
    """analytics.action_recommendations 기본 정책 셋을 보장한다.

    이미 정책이 존재하면 아무 것도 하지 않는다(중복 방지).
    """
    # 하나라도 존재하면 스킵
    try:
        cnt = session.execute(text("SELECT COUNT(1) FROM analytics.action_recommendations")).scalar_one()
        if cnt and int(cnt) > 0:
            logger.info("action_recommendations already populated — skip seeding policies")
            return
    except Exception:
        # 존재 유무 확인 실패 시에는 보수적으로 진행
        pass

    policies: List[Tuple[str, str, str]] = [
        ("VH", "A50", "50% 쿠폰 제공"),
        ("H", "A30", "30% 쿠폰 제공"),
        ("M", "AFS", "무료배송 제공"),
        ("L", "APNT", "포인트 3,000 적립"),
    ]

    for risk_band, action_code, policy_name in policies:
        # 간단 존재 검사 후 삽입
        exists = session.execute(
            text(
                """
                SELECT policy_id FROM analytics.action_recommendations
                WHERE risk_band = :risk_band AND action_code = :action_code
                LIMIT 1
                """
            ),
            {"risk_band": risk_band, "action_code": action_code},
        ).scalar()

        if not exists:
            session.execute(
                text(
                    """
                    INSERT INTO analytics.action_recommendations (risk_band, action_code, policy_name, is_active, effective_from)
                    VALUES (:risk_band, :action_code, :policy_name, true, now())
                    """
                ),
                {"risk_band": risk_band, "action_code": action_code, "policy_name": policy_name},
            )


def get_policy_id_map(session: Session) -> Dict[Tuple[str, str], int]:
    """(risk_band, action_code) -> policy_id 매핑을 조회한다."""
    rows = session.execute(
        text(
            """
            SELECT risk_band, action_code, policy_id
            FROM analytics.action_recommendations
            """
        )
    ).fetchall()
    return {(r[0], r[1]): int(r[2]) for r in rows}


def generate_kpi(customers_total: int, horizon_days: int) -> Tuple[float, float, int]:
    """
    기간별 이탈률/유지율/이탈고객 수를 생성한다.
    짧은 기간은 낮고, 긴 기간일수록 높은 이탈률이 나오도록 스케일한다.
    반환: (churn_rate, retention_rate, churn_customers)
    """
    # base churn for 30d: 8% ~ 16%
    base30_min, base30_max = 0.08, 0.16
    # 기간에 따른 스케일(대략적인 비율)
    scale = {1: 0.06, 7: 0.35, 15: 0.65, 30: 1.0}.get(horizon_days, 1.0)
    churn30 = random.uniform(base30_min, base30_max)
    churn = max(0.0, min(0.99, churn30 * scale))
    retention = max(0.0, 1.0 - churn)
    churn_customers = math.floor(customers_total * churn)
    return churn, retention, churn_customers


def generate_band_distribution(customers_total: int) -> List[Tuple[str, int, float]]:
    """VH/H/M/L 분포를 생성한다. 각 비중은 0~1 합계 1.0 내외."""
    # 기본 분포 및 랜덤 지터
    base = {"VH": 0.12, "H": 0.22, "M": 0.38, "L": 0.28}
    # 랜덤 지터(±0.03) 후 정규화
    jittered = {k: max(0.02, v + random.uniform(-0.03, 0.03)) for k, v in base.items()}
    s = sum(jittered.values())
    ratios = {k: v / s for k, v in jittered.items()}
    rows: List[Tuple[str, int, float]] = []
    for band in RISK_BANDS:
        r = ratios.get(band, 0.0)
        cnt = max(0, int(round(customers_total * r)))
        rows.append((band, cnt, r))
    return rows


def generate_segments(customers_total: int) -> List[Tuple[str, int, float]]:
    """세그먼트별 고객 수와 이탈률을 생성한다."""
    # 고객 수 분배: High/Mid/Low = 0.2/0.4/0.4 ± 지터
    weights = [0.2, 0.4, 0.4]
    weights = [max(0.05, w + random.uniform(-0.05, 0.05)) for w in weights]
    s = sum(weights)
    weights = [w / s for w in weights]

    buckets = DEFAULT_SEGMENTS
    cust_counts = [int(round(customers_total * w)) for w in weights]

    # 이탈률: High 낮게, Low 높게
    churn_rates = [random.uniform(0.06, 0.10), random.uniform(0.10, 0.15), random.uniform(0.15, 0.22)]
    return [(buckets[i], cust_counts[i], churn_rates[i]) for i in range(3)]


def pick_action_for_band(band: str) -> Tuple[str, str]:
    """밴드별 기본 액션 코드/이름(폴백용). 실제 policy_id는 테이블에서 재확인한다."""
    # 운영 테이블 예시: VH=REACTIVATE, H=NUDGE, M=NUDGE, L=LOYALTY
    mapping = {
        "VH": ("REACTIVATE", "재유치 캠페인"),
        "H": ("NUDGE", "행동 유도"),
        "M": ("NUDGE", "행동 유도"),
        "L": ("LOYALTY", "유지/보상"),
    }
    return mapping.get(band, ("NUDGE", "행동 유도"))


def get_policy_for_band(session: Session, band: str, preferred_code: str | None) -> Tuple[int | None, str | None]:
    """(risk_band, preferred_code) 우선으로 policy_id를 찾고, 없으면 해당 밴드의 활성 정책 중 하나를 반환."""
    # 우선 선호 코드로 조회
    if preferred_code:
        row = session.execute(
            text(
                """
                SELECT policy_id, action_code
                FROM analytics.action_recommendations
                WHERE risk_band = :band AND action_code = :code AND coalesce(is_active, true) = true
                ORDER BY effective_from DESC NULLS LAST, policy_id DESC
                LIMIT 1
                """
            ),
            {"band": band, "code": preferred_code},
        ).first()
        if row:
            return int(row[0]), str(row[1])

    # 선호 코드가 없거나 실패하면 밴드 기준으로 아무거나 하나 선택
    row = session.execute(
        text(
            """
            SELECT policy_id, action_code
            FROM analytics.action_recommendations
            WHERE risk_band = :band AND coalesce(is_active, true) = true
            ORDER BY effective_from DESC NULLS LAST, policy_id DESC
            LIMIT 1
            """
        ),
        {"band": band},
    ).first()
    if row:
        return int(row[0]), str(row[1])
    return None, preferred_code


def seed_for_report_dt(session: Session, report_dt: date, horizons: Iterable[int], customers_total: int, users_base: int) -> None:
    """지정된 기준일에 대해 모든 표 대상 데이터를 생성/삽입한다."""
    # 1) KPI + 분포/세그먼트 + 사용자 목록
    for horizon_days in horizons:
        churn_rate, retention_rate, churn_customers = generate_kpi(customers_total, horizon_days)

        # daily_churn_kpi : horizon_days 컬럼 유무에 따라 삭제/삽입 조건 조정
        delete_existing(
            session,
            "mart.daily_churn_kpi",
            {"report_dt": report_dt, "horizon_days": horizon_days},
        )
        cols_daily = fetch_existing_columns(session, "mart", "daily_churn_kpi")
        values_daily = {
            "report_dt": report_dt,
            "customers_total": customers_total,
            "churn_rate": churn_rate,
            # 일부 환경에는 retention_rate 컬럼이 없으므로 존재할 때만 넣는다
            "retention_rate": retention_rate,
            "churn_customers": churn_customers,
            "horizon_days": horizon_days,
        }
        col_names = [c for c in values_daily.keys() if c in cols_daily]
        placeholders = ", ".join([f":{c}" for c in col_names])
        session.execute(
            text(f"INSERT INTO mart.daily_churn_kpi ({', '.join(col_names)}) VALUES ({placeholders})"),
            {k: values_daily[k] for k in col_names},
        )

        # risk distribution
        delete_existing(
            session,
            "mart.churn_risk_distribution",
            {"report_dt": report_dt, "horizon_days": horizon_days},
        )
        for band, user_count, ratio in generate_band_distribution(customers_total):
            session.execute(
                text(
                    """
                    INSERT INTO mart.churn_risk_distribution (report_dt, risk_band, user_count, ratio, horizon_days)
                    VALUES (:report_dt, :risk_band, :user_count, :ratio, :horizon_days)
                    """
                ),
                {
                    "report_dt": report_dt,
                    "risk_band": band,
                    "user_count": user_count,
                    "ratio": ratio,
                    "horizon_days": horizon_days,
                },
            )

        # segment analysis
        delete_existing(
            session,
            "mart.churn_segment_aggr",
            {"report_dt": report_dt, "horizon_days": horizon_days},
        )
        for segment_key, seg_customers, seg_churn_rate in generate_segments(customers_total):
            session.execute(
                text(
                    """
                    INSERT INTO mart.churn_segment_aggr (report_dt, horizon_days, segment_type, segment_key, customers, churn_rate)
                    VALUES (:report_dt, :horizon_days, :segment_type, :segment_key, :customers, :churn_rate)
                    """
                ),
                {
                    "report_dt": report_dt,
                    "horizon_days": horizon_days,
                    "segment_type": "rfm_segment",
                    "segment_key": segment_key,
                    "customers": seg_customers,
                    "churn_rate": seg_churn_rate,
                },
            )

        # high-risk users (페이지 크기와 무관하게 샘플 n개 생성)
        delete_existing(
            session,
            "mart.high_risk_users",
            {"report_dt": report_dt, "horizon_days": horizon_days},
        )
        # risk band별 생성 개수 분배(VH>H>M>L)
        per_horizon = 100
        weights = {"VH": 0.4, "H": 0.3, "M": 0.2, "L": 0.1}
        distribution_counts = {b: int(round(per_horizon * w)) for b, w in weights.items()}
        uid = users_base
        for band in RISK_BANDS:
            count = distribution_counts.get(band, 0)
            # 폴백 코드(운영 환경의 코드와 다를 수 있음)
            preferred_code, _ = pick_action_for_band(band)
            policy_id, resolved_code = get_policy_for_band(session, band, preferred_code)
            action_code = resolved_code or preferred_code
            for _ in range(count):
                # churn probability: VH 0.85~0.97, H 0.7~0.85, M 0.45~0.7, L 0.2~0.45
                ranges = {
                    "VH": (0.85, 0.97),
                    "H": (0.70, 0.85),
                    "M": (0.45, 0.70),
                    "L": (0.20, 0.45),
                }
                lo, hi = ranges[band]
                churn_prob = random.uniform(lo, hi)
                # 컬럼 존재 체크 후 동적 삽입(정의에 따라 policy_id가 없을 수도 있음)
                cols_hr = fetch_existing_columns(session, "mart", "high_risk_users")
                payload = {
                    "report_dt": report_dt,
                    "horizon_days": horizon_days,
                    "user_id": uid,
                    "risk_band": band,
                    "churn_probability": churn_prob,
                    "action_code": action_code,
                    "policy_id": policy_id,
                }
                use_cols = [k for k in payload.keys() if k in cols_hr]
                session.execute(
                    text(
                        f"INSERT INTO mart.high_risk_users ({', '.join(use_cols)}) VALUES ({', '.join(':'+c for c in use_cols)})"
                    ),
                    {k: payload[k] for k in use_cols},
                )
                uid += 1

    # 2) refresh_queue (환경에 따라 horizon_days가 NOT NULL일 수 있으므로 컬럼 체크 후 삽입)
    cols_rq = fetch_existing_columns(session, "mart", "refresh_queue")
    # 기존 데이터 삭제: report_dt(및 horizon_days가 있으면 해당 목록) 기준
    if "horizon_days" in cols_rq:
        for h in horizons:
            delete_existing(session, "mart.refresh_queue", {"report_dt": report_dt, "horizon_days": h})
    else:
        delete_existing(session, "mart.refresh_queue", {"report_dt": report_dt})

    enq_ts = datetime.now(timezone.utc)
    if "horizon_days" in cols_rq:
        for h in horizons:
            session.execute(
                text("INSERT INTO mart.refresh_queue (report_dt, horizon_days, enqueued_at) VALUES (:report_dt, :h, :enq)"),
                {"report_dt": report_dt, "h": h, "enq": enq_ts},
            )
    else:
        session.execute(
            text("INSERT INTO mart.refresh_queue (report_dt, enqueued_at) VALUES (:report_dt, :enq)"),
            {"report_dt": report_dt, "enq": enq_ts},
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed dashboard mart tables with dummy data")
    parser.add_argument("--report-dt", type=str, default=date.today().isoformat(), help="기준 보고일 (YYYY-MM-DD)")
    parser.add_argument("--customers-total", type=int, default=48000, help="총 고객 수")
    parser.add_argument("--seed", type=int, default=42, help="랜덤 시드")
    parser.add_argument(
        "--horizons",
        type=str,
        default="1,7,15,30",
        help="콤마 구분 horizon_days 목록 (예: 1,7,15,30)",
    )

    args = parser.parse_args()
    report_dt = date.fromisoformat(args.report_dt)
    customers_total = args.customers_total
    random.seed(args.seed)
    horizons = [int(x) for x in args.horizons.split(",") if x.strip()]

    with Session(bind=engine) as session:
        try:
            logger.info(f"Seeding dashboard marts for report_dt={report_dt} horizons={horizons} ...")
            upsert_policy_reference(session)
            seed_for_report_dt(session, report_dt, horizons, customers_total, users_base=100000)
            session.commit()
            logger.info("Done. ✨")
        except Exception as exc:
            session.rollback()
            logger.error(f"Failed: {exc}")
            raise


if __name__ == "__main__":
    main()


