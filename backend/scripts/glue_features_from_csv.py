"""
Glue 4.0 / Spark 3
S3 CSV 이벤트에서 사용자 피처를 산출하는 Glue 잡 스크립트

Arguments (getResolvedOptions):
- --JOB_NAME           : Glue 잡 이름(필수)
- --DB                 : Glue Data Catalog DB 이름(필수)
- --EVENTS_TABLE       : Glue Data Catalog 테이블 이름(필수)
- --OUT_PREFIX         : (선택) 출력 S3 prefix (예: s3://bucket/features)
- --DT                 : (선택) 기준일(YYYY-MM-DD). 미지정 시 이벤트의 최대 event_time 날짜

출력: OUT_PREFIX/dt=DT/ 에 Parquet 파일(단일 파티션) 생성
스키마: features_from_csv.py와 동일 (gender는 문자열 male/female/other)
"""

import sys
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql import Window as W


base_keys = ['JOB_NAME', 'DB', 'EVENTS_TABLE']
# 필수만 Glue 파서로 받고, 선택 인자는 수동 파싱(트레일링 스페이스 등 변형 대응)
args = getResolvedOptions(sys.argv, base_keys)

def parse_opt(name: str):
    key = f'--{name}'
    argv = list(sys.argv)
    for i, token in enumerate(argv):
        t = str(token).strip()
        # 정확히 일치(--KEY) 또는 --KEY=값 만 허용. --KEY_MODE 같은 접두사 오탐 방지
        if t == key or t.startswith(key + '='):
            # --KEY=value 형태
            if '=' in t:
                return t.split('=', 1)[1].strip()
            # --KEY value 형태 (다음 토큰이 값인 경우)
            if i + 1 < len(argv):
                nxt = str(argv[i + 1]).strip()
                if not nxt.startswith('--'):
                    return nxt
            return ''
    return None

JOB_NAME = args['JOB_NAME']
DB = args['DB']
EVT_TABLE = args['EVENTS_TABLE']

# 출력 경로와 기준일: 잡 파라미터 > 환경변수 > 기본값 순으로 결정
OUT_PREFIX = (parse_opt('OUT_PREFIX') or os.getenv('OUT_PREFIX') or 's3://ecps-event-log/features').rstrip('/')
# --DT가 명시되면 사용하고, 없으면 DT_MODE 규칙 적용
DT = parse_opt('DT')
DT_MODE = (parse_opt('DT_MODE') or os.getenv('DT_MODE') or 'yesterday').lower()
TIMEZONE = parse_opt('TIMEZONE') or os.getenv('TIMEZONE') or 'Asia/Seoul'

# DT가 문자열 모드로 들어오면 즉시 해석(run/yesterday/data_max)
try:
    tz = ZoneInfo(TIMEZONE)
except Exception:
    tz = None
now_local = datetime.now(tz) if tz else datetime.now().astimezone()
if isinstance(DT, str):
    dt_lower = DT.strip().lower()
    if dt_lower == 'run':
        DT = now_local.date().strftime('%Y-%m-%d')
    elif dt_lower == 'yesterday':
        DT = (now_local.date() - timedelta(days=1)).strftime('%Y-%m-%d')
    elif dt_lower == 'data_max':
        DT = None

# DT가 미지정이면 DT_MODE에 따라 결정
if not DT:
    if DT_MODE == 'run':
        DT = now_local.date().strftime('%Y-%m-%d')
    elif DT_MODE == 'yesterday':
        DT = (now_local.date() - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        DT = None  # data_max는 아래 as-of 계산 시 결정

print(f"[CONFIG] OUT_PREFIX={OUT_PREFIX}, DT={DT}, DT_MODE={DT_MODE}, TIMEZONE={TIMEZONE}")

sc = SparkContext()
glue = GlueContext(sc)
spark = glue.spark_session
job = Job(glue)
job.init(JOB_NAME, args)


def read_events_from_catalog(database: str, table: str):
    dyf = glue.create_dynamic_frame.from_catalog(database=database, table_name=table)
    return dyf.toDF()


def build_features(df):
    # 결측 컬럼 보강 유틸
    def ensure_col(d, name: str, dtype: str = 'string'):
        return d if name in d.columns else d.withColumn(name, F.lit(None).cast(dtype))

    # 다운스트림에서 참조하는 주요 컬럼들 보강(없으면 널로 생성)
    for c, t in [
        ('event_name','string'), ('log_type','string'), ('event_time','string'),
        ('user_id','string'), ('gender','string'), ('birthdate','string'), ('created_at','string'),
        ('num_interests','int'), ('interest_categories','string'),
        ('items_count','string'), ('price','string'), ('shipping_fee','string'), ('items_total','string'),
        ('order_id','string'), ('request_id','string'), ('event_id','string'),
        ('used_coupon_code','string'), ('coupon_code','string'), ('coupon_id','string')
    ]:
        df = ensure_col(df, c, t)

    # 표준 이벤트명
    df = df.withColumn('event_name', F.col('event_name').cast('string')) \
           .withColumn('log_type', F.col('log_type').cast('string'))
    df = df.withColumn('etype',
           F.when(F.length(F.coalesce(F.col('event_name'), F.lit(''))) > 0,
                  F.lower(F.col('event_name')))
            .otherwise(F.lower(F.col('log_type'))))

    # 시간/날짜
    df = df.withColumn('event_time_ts', F.to_timestamp('event_time')) \
           .withColumn('event_dt', F.to_date('event_time_ts'))

    # user_id 정규화(숫자만)
    df = df.withColumn('user_id', F.regexp_extract(F.col('user_id').cast('string'), r'(\d+)', 1).cast('bigint'))

    # 숫자 캐스팅
    to_double = lambda c: F.regexp_replace(F.col(c).cast('string'), r'[^0-9.\-]', '').cast('double')
    to_int = lambda c: F.regexp_replace(F.col(c).cast('string'), r'[^0-9\-]', '').cast('int')
    df = (df
          .withColumn('items_count_n', to_double('items_count'))
          .withColumn('price_n', to_double('price'))
          .withColumn('shipping_fee_n', to_double('shipping_fee'))
          .withColumn('items_total_n', to_double('items_total')))

    # as-of 결정
    global DT
    if DT is None:  # DT_MODE == data_max 이거나 상위에서 결정 실패 시 데이터 기반
        dt_row = df.select(F.max('event_dt').alias('mx')).first()
        DT = (dt_row.mx or datetime.utcnow().date()).strftime('%Y-%m-%d') if hasattr(dt_row.mx, 'strftime') else str(dt_row.mx)
    asof = F.lit(DT).cast('date')

    # Profiles (user_profile)
    prof = df.filter(F.col('etype') == 'user_profile') \
             .withColumn('gender_txt', F.lower(F.col('gender').cast('string'))) \
             .withColumn('gender_txt', F.regexp_replace('gender_txt', r'^genderenum\.', ''))
    prof = (prof
            .withColumn('gender', F.when(F.col('gender_txt').isin('male', 'female', 'other'), F.col('gender_txt')).otherwise(F.lit('')))
            .withColumn('birth_dt', F.to_date('birthdate'))
            .withColumn('created_dt', F.to_date('created_at'))
            .withColumn('age', F.floor(F.months_between(asof, F.col('birth_dt'))/12).cast('int'))
            .withColumn('num_interests', F.when(F.col('num_interests').isNotNull(), F.col('num_interests').cast('int'))
                                         .otherwise(F.size(F.from_json(F.col('interest_categories').cast('string'), 'array<int>')))))

    w_prof = W.partitionBy('user_id').orderBy(F.col('event_time_ts').desc())
    prof_last = (prof.withColumn('rn', F.row_number().over(w_prof)).filter(F.col('rn') == 1)
                  .select('user_id', 'age', 'gender',
                          F.datediff(asof, F.col('created_dt')).alias('tenure_days'),
                          'num_interests'))

    # Orders (order_paid)
    orders = (df.filter(F.col('etype') == 'order_paid')
                .withColumn('order_dt', F.to_date('event_time_ts'))
                .withColumn('order_amt', F.coalesce(F.col('items_total_n'), F.col('price_n') + F.col('shipping_fee_n'), F.col('price_n')))
                .withColumn('order_key', F.coalesce(F.col('order_id'), F.col('request_id'), F.col('event_id')).cast('string'))
             )

    ord_base = (orders.groupBy('user_id').agg(
        F.max('order_dt').alias('last_order_dt'),
        F.countDistinct('order_key').alias('order_count'),
        F.sum('order_amt').alias('total_spend'),
        F.avg('order_amt').alias('avg_order_value'),
        F.avg('items_count_n').alias('avg_items_per_order')
    ))

    # 쿠폰 사용률 (카탈로그 스키마에 맞춰 used_coupon_code / coupon_id만 사용)
    coupon_used = (F.when(F.length(F.coalesce(F.col('used_coupon_code').cast('string'), F.lit(''))) > 0, 1)
                    .when(F.length(F.coalesce(F.col('coupon_id').cast('string'), F.lit(''))) > 0, 1)
                    .otherwise(0))
    ord_cpn = orders.withColumn('coupon_used', coupon_used) \
                   .groupBy('user_id').agg(F.avg('coupon_used').alias('coupon_usage_rate'))

    # 주문 간 평균 일수
    w_ord = W.partitionBy('user_id').orderBy('order_dt')
    days_between = (orders
        .withColumn('prev_dt', F.lag('order_dt').over(w_ord))
        .withColumn('diff_days', F.datediff(F.col('order_dt'), F.col('prev_dt')))
        .groupBy('user_id').agg(F.avg('diff_days').alias('days_between_orders')))

    # 30/90일 빈도
    last30 = (orders.filter(F.col('order_dt') >= F.date_sub(asof, 30))
                    .groupBy('user_id').agg(F.count('*').alias('frequency_last_30d')))
    last90 = (orders.filter(F.col('order_dt') >= F.date_sub(asof, 90))
                    .groupBy('user_id').agg(F.count('*').alias('frequency_last_90d')))

    # 세션/카트
    last_session = (df.filter(F.col('etype') == 'page_view')
                      .groupBy('user_id').agg(F.max('event_dt').alias('last_session_dt')))
    last_session_days = last_session.select('user_id', F.datediff(asof, F.col('last_session_dt')).alias('days_since_last_session'))

    cart30 = (df.filter(F.col('etype').isin('cart_add', 'add_to_cart'))
                .filter(F.col('event_dt') >= F.date_sub(asof, 30))
                .groupBy('user_id').agg(F.count('*').alias('cart_additions_last_30d')))

    # RFM 점수
    pop = ord_base.select('user_id', F.datediff(asof, F.col('last_order_dt')).alias('recency_days_orders'),
                          'order_count', 'total_spend')
    r_win = W.orderBy(F.col('recency_days_orders').asc())
    f_win = W.orderBy(F.col('order_count').desc())
    m_win = W.orderBy(F.col('total_spend').desc())
    rfm = (pop
           .select('user_id',
                   F.ntile(5).over(r_win).alias('recency_score'),
                   F.ntile(5).over(f_win).alias('frequency_score'),
                   F.ntile(5).over(m_win).alias('monetary_score')))

    # 사용자 집합
    base_users = df.select('user_id').where(F.col('user_id').isNotNull()).distinct()

    # 병합
    feats = (base_users
        .join(prof_last, 'user_id', 'left')
        .join(ord_base.select('user_id', 'avg_order_value', 'avg_items_per_order'), 'user_id', 'left')
        .join(last30, 'user_id', 'left')
        .join(last90, 'user_id', 'left')
        .join(days_between, 'user_id', 'left')
        .join(ord_cpn, 'user_id', 'left')
        .join(last_session_days, 'user_id', 'left')
        .join(cart30, 'user_id', 'left')
        .join(rfm, 'user_id', 'left'))

    # 기본값 채움 & 컬럼 정리
    feats = (feats
        .fillna({'age': 0, 'gender': '', 'tenure_days': 0, 'num_interests': 0,
                 'recency_score': 1, 'frequency_score': 1, 'monetary_score': 1,
                 'avg_order_value': 0.0, 'avg_items_per_order': 0.0,
                 'frequency_last_30d': 0, 'frequency_last_90d': 0,
                 'days_between_orders': 0.0, 'coupon_usage_rate': 0.0,
                 'days_since_last_session': 9999, 'cart_additions_last_30d': 0})
        .withColumn('monetary_avg_order', F.col('avg_order_value'))
        .withColumn('churn', F.when((F.col('frequency_last_90d') == 0) & (F.col('days_since_last_session') > 30), 1).otherwise(0).cast('int')))

    select_cols = ['user_id', 'age', 'gender', 'tenure_days', 'num_interests',
                   'recency_score', 'frequency_score', 'monetary_score',
                   'monetary_avg_order', 'avg_items_per_order',
                   'frequency_last_30d', 'frequency_last_90d', 'days_between_orders',
                   'coupon_usage_rate', 'days_since_last_session', 'cart_additions_last_30d', 'churn']
    feats = feats.select(*select_cols)
    return feats


events = read_events_from_catalog(DB, EVT_TABLE)
features = build_features(events)

out_path = f"{OUT_PREFIX}/dt={DT}/"
features.repartition(1).write.mode('append').parquet(out_path)
print(f"Wrote features to {out_path}")

job.commit()


