import os
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

# 프로젝트 루트를 기준으로 db와 models를 import하기 위한 설정
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database import SessionLocal
from db.models import Event as AnalyticsEvent

# --- 설정 ---
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'events.log')

def parse_and_store_log(db: Session, log_line: str):
    """로그 한 줄을 파싱하여 DB에 저장합니다."""
    try:
        log_data = json.loads(log_line)

        # --- 데이터 추출 및 변환 ---
        event_time_iso = log_data.get("event_time")
        event_time_dt = datetime.fromisoformat(event_time_iso) if event_time_iso else datetime.now().astimezone()

        # user_id를 정수형으로 변환
        user_id_int = None
        user_id_str = log_data.get("user_id")
        if user_id_str:
            try:
                user_id_int = int(''.join(filter(str.isdigit, user_id_str)))
            except (ValueError, TypeError):
                user_id_int = None

        # product_info가 있다면 내부 정보 추출
        product_info = log_data.get("product_info", {})
        if isinstance(product_info, str):
            try:
                product_info = json.loads(product_info)
            except json.JSONDecodeError:
                product_info = {}

        # ID 필드들을 정수형으로 변환 (존재하는 경우)
        order_id_int = int(''.join(filter(str.isdigit, log_data["order_id"]))) if log_data.get("order_id") else None
        payment_id_int = int(''.join(filter(str.isdigit, log_data["payment_id"]))) if log_data.get("payment_id") else None
        coupon_id_int = int(''.join(filter(str.isdigit, log_data["coupon_id"]))) if log_data.get("coupon_id") else None

        # --- AnalyticsEvent 객체 생성 ---
        event = AnalyticsEvent(
            event_time=event_time_dt,
            event_date=event_time_dt.date(),
            event_id=str(uuid.uuid4()),
            event_name=log_data.get("log_type"),
            user_id=user_id_int,
            page_url=log_data.get("url"),
            referrer=log_data.get("referer"),
            is_authenticated=bool(user_id_int),
            
            # UTM 파라미터
            utm_source=log_data.get("utm_source"),
            utm_medium=log_data.get("utm_medium"),
            utm_campaign=log_data.get("utm_campaign"),
            utm_content=log_data.get("utm_content"),

            # ID 필드
            product_id=log_data.get("product_id"),
            order_id=order_id_int,
            payment_id=payment_id_int,
            coupon_id=coupon_id_int,

            # 가격 및 수량
            quantity=log_data.get("quantity"),
            price_at_event=log_data.get("price", product_info.get("price")),
            total_amount_at_event=log_data.get("price_total"),

            # 상품 정보 스냅샷
            product_name_at_event=product_info.get("name"),
            product_category_at_event=product_info.get("category"),
        )

        db.add(event)
        print(f"INFO: Successfully processed event: {log_data.get('log_type')}")

    except json.JSONDecodeError:
        print(f"ERROR: Failed to decode JSON: {log_line}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e} - a t log line: {log_line}")

def process_log_file():
    """로그 파일을 처리하고, 처리된 파일은 이름을 변경합니다."""
    if not os.path.exists(LOG_FILE_PATH):
        print("INFO: Log file not found. Nothing to process.")
        return

    # 처리 시작 전, 임시 파일 이름으로 변경
    processing_file_path = LOG_FILE_PATH + ".processing"
    try:
        os.rename(LOG_FILE_PATH, processing_file_path)
    except FileNotFoundError:
        print("INFO: Log file disappeared before processing. Nothing to do.")
        return
    except Exception as e:
        print(f"ERROR: Could not rename log file: {e}")
        return

    print(f"INFO: Processing file: {processing_file_path}")
    
    db = SessionLocal()
    try:
        with open(processing_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    parse_and_store_log(db, line.strip())
        db.commit()
        print("INFO: Database commit successful.")

    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to process logs. Rolling back changes. Error: {e}")
    finally:
        db.close()

    # 처리가 완료된 파일 이름 변경
    processed_file_path = f"{LOG_FILE_PATH}.processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        os.rename(processing_file_path, processed_file_path)
        print(f"INFO: Successfully processed and renamed log file to: {processed_file_path}")
    except Exception as e:
        print(f"ERROR: Could not rename processed file: {e}")

if __name__ == "__main__":
    process_log_file()
