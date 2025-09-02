import os
import csv
import json
import gzip
from datetime import datetime
from typing import List, Dict, Set

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
import boto3

# 입력 로그 파일 (가공 전)
RAW_LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'events.log')

def read_raw_events(path: str) -> List[Dict]:
    events: List[Dict] = []
    if not os.path.exists(path):
        return events
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            events.append(obj)
    return events

def normalize_event(e: Dict) -> Dict:
    """
    원본 이벤트를 가능한 한 그대로 보존하되, CSV 친화적으로 값들을 직렬화합니다.
    - 누락 키는 제외(헤더 단계에서 공란으로 채움)
    - 객체/배열은 JSON 문자열로 직렬화
    - product_info/name,category는 별도 컬럼으로 파생 추가
    - referer/referrer 혼용은 referer 우선 컬럼으로 정규화하되, 원본 키도 유지
    """
    row: Dict[str, str] = {}

    # 기본 필드 복사 + 직렬화
    for k, v in e.items():
        if v is None:
            row[k] = ""
        elif isinstance(v, (str, int, float, bool)):
            row[k] = str(v)
        else:
            # dict/list 등은 JSON 문자열로
            row[k] = json.dumps(v, ensure_ascii=False)

    # event_time 보정
    if not row.get('event_time'):
        row['event_time'] = datetime.utcnow().isoformat()

    # referer 표준화(referrer 대체)
    if not row.get('referer') and row.get('referrer'):
        row['referer'] = row['referrer']

    # product_info 파생 컬럼
    product_info = e.get('product_info')
    try:
        if isinstance(product_info, str):
            product_info = json.loads(product_info)
    except Exception:
        product_info = None
    if isinstance(product_info, dict):
        if 'name' in product_info and 'product_name' not in row:
            row['product_name'] = str(product_info.get('name') or '')
        if 'category' in product_info and 'product_category' not in row:
            row['product_category'] = str(product_info.get('category') or '')

    return row

def collect_fieldnames(rows: List[Dict]) -> List[str]:
    """이벤트들의 모든 키를 합쳐 헤더 컬럼을 동적으로 생성합니다."""
    keys: Set[str] = set()
    for r in rows:
        keys.update(r.keys())
    # 가독성을 위해 대표 컬럼을 앞쪽에 배치
    preferred = [
        'event_time','log_type','user_id','url','referer','referrer','utm_source','utm_medium','utm_campaign','utm_content',
        'product_id','order_id','payment_id','coupon_id','quantity','price','price_total','product_name','product_category','session_id','request_id'
    ]
    ordered = [c for c in preferred if c in keys]
    rest = sorted([c for c in keys if c not in set(preferred)])
    return ordered + rest

def write_csv_gz(rows: List[Dict], out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(out_dir, f'events_{ts}.csv.gz')
    fieldnames = collect_fieldnames(rows) if rows else []
    with gzip.open(out_path, 'wt', encoding='utf-8', newline='') as gz:
        writer = csv.DictWriter(gz, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return out_path

def upload_to_s3(file_path: str, bucket: str, s3_prefix: str) -> str:
    s3 = boto3.client('s3')
    key = f"{s3_prefix.rstrip('/')}/{os.path.basename(file_path)}"
    s3.upload_file(file_path, bucket, key)
    return key

def main():
    load_dotenv()
    bucket = os.getenv('S3_BUCKET')
    prefix = os.getenv('S3_PREFIX', 'logs/events')
    if not bucket:
        raise RuntimeError('S3_BUCKET 환경변수가 필요합니다.')

    # AWS 자격 증명은 표준 방식 사용: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

    raw = read_raw_events(RAW_LOG_PATH)
    normalized = [normalize_event(e) for e in raw]
    if not normalized:
        print('No events to export.')
        return
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'exports')
    csv_gz_path = write_csv_gz(normalized, out_dir)
    s3_key = upload_to_s3(csv_gz_path, bucket, prefix)
    print(f'Uploaded to s3://{bucket}/{s3_key}')

if __name__ == '__main__':
    main()


