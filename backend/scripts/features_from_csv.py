import argparse
import json
import math
import os
from datetime import datetime, timedelta, date
from typing import Optional

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute user-level features from exported event CSV (line-delimited)"
    )
    parser.add_argument("--in", dest="input_csv", required=True, help="Path to events CSV")
    parser.add_argument("--out", dest="output_csv", required=True, help="Path to write features CSV")
    parser.add_argument("--asof", dest="asof", default=None, help="As-of date (YYYY-MM-DD). Default = max(event_time).date()")
    parser.add_argument("--xlsx", dest="excel_path", default=None, help="Optional: Path to write Excel (.xlsx)")
    parser.add_argument("--sheet", dest="sheet_name", default="features", help="Excel sheet name (default: features)")
    return parser.parse_args()


def to_numeric_safe(s: pd.Series, dtype: str = "float") -> pd.Series:
    if s is None:
        return pd.Series(dtype=dtype)
    s2 = pd.to_numeric(s, errors="coerce")
    return s2.astype(dtype) if dtype == "int" else s2


def extract_user_id(series: pd.Series) -> pd.Series:
    # 숫자만 추출 → pandas nullable Int64
    v = series.astype(str).str.extract(r"(\d+)", expand=False)
    return pd.to_numeric(v, errors="coerce").astype("Int64")


def coalesce(*cols: pd.Series) -> pd.Series:
    out = None
    for c in cols:
        if out is None:
            out = c
        else:
            out = out.combine_first(c)
    return out


def compute_ntile(series: pd.Series, tiles: int, invert: bool = False) -> pd.Series:
    s = series.dropna()
    if s.empty:
        return pd.Series(index=series.index, dtype="float")
    labels = list(range(1, tiles + 1))
    if invert:
        labels = labels[::-1]
    try:
        q = pd.qcut(s, q=tiles, labels=labels, duplicates="drop")
        out = pd.Series(index=series.index, dtype="float")
        out.loc[s.index] = q.astype(float)
        return out
    except Exception:
        # Fallback: rank 기반 등분
        r = s.rank(method="average")
        buckets = np.ceil(r / (len(s) / tiles))
        buckets = buckets.clip(1, tiles)
        if invert:
            buckets = tiles + 1 - buckets
        out = pd.Series(index=series.index, dtype="float")
        out.loc[s.index] = buckets.astype(float)
        return out


def load_events(path: str) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        low_memory=False,
        dtype={
            "user_id": "string",
            "order_id": "string",
            "event_name": "string",
            "log_type": "string",
            "birthdate": "string",
            "created_at": "string",
            "gender": "string",
            "interest_categories": "string",
            "used_coupon_code": "string",
            "coupon_code": "string",
            "coupon_id": "string",
            "items_count": "string",
            "items_total": "string",
            "price": "string",
            "shipping_fee": "string",
        },
        parse_dates=["event_time"],
    )
    # 표준 이벤트명
    df["etype"] = df["event_name"].where(
        df["event_name"].notna() & (df["event_name"].astype(str) != ""), df["log_type"]
    ).astype(str).str.lower()
    # user_id 정규화
    df["user_id"] = extract_user_id(df.get("user_id"))
    # 숫자 컬럼
    df["items_count_n"] = to_numeric_safe(df.get("items_count"), dtype="float")
    df["price_n"] = to_numeric_safe(df.get("price"))
    df["shipping_fee_n"] = to_numeric_safe(df.get("shipping_fee"))
    df["items_total_n"] = to_numeric_safe(df.get("items_total"))
    df["event_date"] = pd.to_datetime(df["event_time"]).dt.date
    return df


def compute_profiles(df: pd.DataFrame, asof: date) -> pd.DataFrame:
    prof = df[df["etype"] == "user_profile"].copy()
    if prof.empty:
        return pd.DataFrame(columns=["user_id", "age", "gender", "tenure_days", "num_interests"]).astype(
            {"user_id": "Int64", "age": "int", "gender": "int", "tenure_days": "int", "num_interests": "int"}
        )

    # gender 정규화
    gtxt = prof["gender"].astype(str).str.lower()
    gtxt = gtxt.str.replace(r"^genderenum\.", "", regex=True)
    gender_map = {"male": 1, "female": 2, "other": 3}
    prof["gender_i"] = gtxt.map(gender_map).fillna(0).astype(int)
    # 문자열 성별 컬럼도 생성
    try:
        import numpy as _np
        prof["gender_str"] = _np.where(gtxt.isin(["male","female","other"]), gtxt, "")
    except Exception:
        prof["gender_str"] = gtxt.where(gtxt.isin(["male","female","other"]), "")

    # birthdate / created_at 파싱
    b = pd.to_datetime(prof["birthdate"], errors="coerce").dt.date
    c = pd.to_datetime(prof["created_at"], errors="coerce").dt.date
    prof["age"] = ((pd.to_datetime(asof) - pd.to_datetime(b)).dt.days // 365).fillna(0).astype(int)
    prof["tenure_days"] = ((pd.to_datetime(asof) - pd.to_datetime(c)).dt.days).fillna(0).astype(int)

    # num_interests
    if "num_interests" in prof.columns and prof["num_interests"].notna().any():
        ni = to_numeric_safe(prof["num_interests"], dtype="int").fillna(0)
    else:
        parsed = (
            prof["interest_categories"].fillna("[]").astype(str).apply(lambda s: len(json.loads(s)) if s else 0)
        )
        ni = pd.to_numeric(parsed, errors="coerce").fillna(0).astype(int)
    prof["num_interests_i"] = ni

    # 최신 스냅샷
    prof_sorted = prof.sort_values(["user_id", "event_time"])  # ascending → 마지막이 최신
    last = prof_sorted.groupby("user_id").tail(1)
    out = last[["user_id", "age", "gender_i", "tenure_days", "num_interests_i", "gender_str"]].rename(
        columns={"gender_i": "gender_num", "num_interests_i": "num_interests", "gender_str": "gender"}
    )
    out["user_id"] = out["user_id"].astype("Int64")
    return out


def compute_orders(df: pd.DataFrame, asof: date) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    orders = df[df["etype"] == "order_paid"].copy()
    if orders.empty:
        empty = pd.DataFrame({"user_id": pd.Series(dtype="Int64")})
        return (
            empty,
            empty,
            empty,
            empty,
        )

    orders["order_dt"] = pd.to_datetime(orders["event_time"]).dt.date
    # 주문 금액 추정: items_total > (price + shipping) > price
    orders["order_amt"] = orders["items_total_n"].combine_first(orders["price_n"] + orders["shipping_fee_n"]).combine_first(
        orders["price_n"]
    )
    # 안전한 주문 키
    key = orders["order_id"].where(orders["order_id"].notna() & (orders["order_id"].astype(str) != ""), orders["request_id"])
    key = key.where(key.notna() & (key.astype(str) != ""), orders["event_id"])
    orders["order_key"] = key.astype(str)

    # 기본 집계
    ord_base = (
        orders.groupby("user_id").agg(
            last_order_dt=("order_dt", "max"),
            order_count=("order_key", "nunique"),
            total_spend=("order_amt", "sum"),
            avg_order_value=("order_amt", "mean"),
            avg_items_per_order=("items_count_n", "mean"),
        )
    )

    # 쿠폰 사용률
    coupon_used = (
        (orders.get("used_coupon_code").fillna("").astype(str).str.len() > 0)
        | (orders.get("coupon_code", pd.Series(["" for _ in range(len(orders))])).fillna("").astype(str).str.len() > 0)
        | (orders.get("coupon_id", pd.Series(["" for _ in range(len(orders))])).fillna("").astype(str).str.len() > 0)
    ).astype(int)
    ord_cpn = orders.assign(coupon_used=coupon_used).groupby("user_id")["coupon_used"].mean().to_frame("coupon_usage_rate")

    # 주문 간 평균 일수
    def _avg_diff_days(g: pd.DataFrame) -> float:
        ds = pd.Series(sorted(g["order_dt"].dropna().unique()))
        if len(ds) <= 1:
            return np.nan
        diffs = ds.diff().dt.days.dropna()
        return float(diffs.mean()) if not diffs.empty else np.nan

    days_between = orders.groupby("user_id").apply(_avg_diff_days).to_frame("days_between_orders")

    # 기간 주문 수
    asof_ts = pd.to_datetime(asof)
    last30 = orders[orders["order_dt"] >= (asof_ts - pd.Timedelta(days=30)).date()].groupby("user_id").size().to_frame(
        "frequency_last_30d"
    )
    last90 = orders[orders["order_dt"] >= (asof_ts - pd.Timedelta(days=90)).date()].groupby("user_id").size().to_frame(
        "frequency_last_90d"
    )

    return ord_base, ord_cpn, days_between, last30.join(last90, how="outer")


def compute_sessions_and_cart(df: pd.DataFrame, asof: date) -> tuple[pd.DataFrame, pd.DataFrame]:
    asof_ts = pd.to_datetime(asof)
    # 세션
    pv = df[df["etype"] == "page_view"][['user_id', 'event_time']].copy()
    if pv.empty:
        last_session_days = pd.DataFrame(columns=["user_id", "days_since_last_session"]).set_index("user_id")
    else:
        last_dt = pv.groupby("user_id")["event_time"].max().dt.date
        days = (asof_ts.date() - last_dt).apply(lambda x: x.days if pd.notna(x) else np.nan)
        last_session_days = days.to_frame("days_since_last_session")

    # 장바구니 30일
    cart = df[df["etype"].isin(["cart_add", "add_to_cart"])][["user_id", "event_time"]].copy()
    cart30 = cart[cart["event_time"].dt.date >= (asof_ts - pd.Timedelta(days=30)).date()].groupby("user_id").size().to_frame(
        "cart_additions_last_30d"
    )

    return last_session_days, cart30


def compute_rfm_scores(ord_base: pd.DataFrame, asof: date) -> pd.DataFrame:
    if ord_base.empty:
        return pd.DataFrame(columns=["user_id", "recency_score", "frequency_score", "monetary_score"]).set_index("user_id")
    recency_days_orders = (pd.to_datetime(asof) - pd.to_datetime(ord_base["last_order_dt"]))
    recency_days_orders = recency_days_orders.dt.days
    rs = compute_ntile(recency_days_orders, 5, invert=True)  # 최근일수 작을수록 높게
    fs = compute_ntile(ord_base["order_count"], 5, invert=False)
    ms = compute_ntile(ord_base["total_spend"], 5, invert=False)
    return pd.DataFrame(
        {
            "recency_score": rs,
            "frequency_score": fs,
            "monetary_score": ms,
        },
        index=ord_base.index,
    )


def main():
    args = parse_args()
    df = load_events(args.input_csv)

    # 기준일(as-of)
    if args.asof:
        asof_d = datetime.strptime(args.asof[:10], "%Y-%m-%d").date()
    else:
        asof_d = pd.to_datetime(df["event_time"]).dt.date.max()

    # 사용자 집합
    base_users = df["user_id"].dropna().astype("Int64").unique()
    base_index = pd.Index(base_users, name="user_id")

    # 프로필
    prof = compute_profiles(df, asof_d).set_index("user_id")

    # 주문 관련
    ord_base, ord_cpn, days_between, lastX = compute_orders(df, asof_d)
    ord_base = ord_base
    ord_cpn = ord_cpn
    days_between = days_between
    lastX = lastX

    # 세션/카트
    last_session_days, cart30 = compute_sessions_and_cart(df, asof_d)

    # RFM 점수
    rfm = compute_rfm_scores(ord_base, asof_d)

    # 병합
    feats = (
        pd.DataFrame(index=base_index)
        .join(prof, how="left")
        .join(ord_base[["avg_order_value", "avg_items_per_order"]], how="left")
        .join(lastX, how="left")
        .join(days_between, how="left")
        .join(ord_cpn, how="left")
        .join(last_session_days, how="left")
        .join(cart30, how="left")
        .join(rfm, how="left")
    )

    # 기본값 채우기 & 타입 정리
    feats = feats.reindex(columns=[
        "age","gender","tenure_days","num_interests",
        "recency_score","frequency_score","monetary_score",
        "avg_order_value","avg_items_per_order",
        "frequency_last_30d","frequency_last_90d","days_between_orders",
        "coupon_usage_rate","days_since_last_session","cart_additions_last_30d"
    ])

    feats = feats.fillna({
        "age": 0,
        "gender": "",
        "tenure_days": 0,
        "num_interests": 0,
        "recency_score": 1,
        "frequency_score": 1,
        "monetary_score": 1,
        "avg_order_value": 0.0,
        "avg_items_per_order": 0.0,
        "frequency_last_30d": 0,
        "frequency_last_90d": 0,
        "days_between_orders": 0.0,
        "coupon_usage_rate": 0.0,
        "days_since_last_session": 9999,
        "cart_additions_last_30d": 0,
    })

    # churn 라벨
    churn = ((feats["frequency_last_90d"] == 0) & (feats["days_since_last_session"] > 30)).astype(int)

    out_df = feats.copy()
    out_df.insert(0, "user_id", out_df.index.astype("Int64"))
    out_df["monetary_avg_order"] = out_df.pop("avg_order_value")
    out_df["churn"] = churn

    # 최종 컬럼 순서
    cols = [
        "user_id","age","gender","tenure_days","num_interests",
        "recency_score","frequency_score","monetary_score",
        "monetary_avg_order","avg_items_per_order",
        "frequency_last_30d","frequency_last_90d","days_between_orders",
        "coupon_usage_rate","days_since_last_session","cart_additions_last_30d","churn"
    ]
    out_df = out_df[cols]

    os.makedirs(os.path.dirname(args.output_csv) or ".", exist_ok=True)
    out_df.to_csv(args.output_csv, index=False)
    print(f"wrote features: {args.output_csv} rows={len(out_df)}")

    # Optional Excel export
    if args.excel_path:
        os.makedirs(os.path.dirname(args.excel_path) or ".", exist_ok=True)
        try:
            with pd.ExcelWriter(args.excel_path, engine="openpyxl") as writer:
                out_df.to_excel(writer, index=False, sheet_name=args.sheet_name)
        except Exception:
            try:
                with pd.ExcelWriter(args.excel_path, engine="xlsxwriter") as writer:
                    out_df.to_excel(writer, index=False, sheet_name=args.sheet_name)
            except Exception as e:
                print(f"failed to write excel: {e}")
            else:
                print(f"wrote excel: {args.excel_path} rows={len(out_df)}")
        else:
            print(f"wrote excel: {args.excel_path} rows={len(out_df)}")


if __name__ == "__main__":
    main()


