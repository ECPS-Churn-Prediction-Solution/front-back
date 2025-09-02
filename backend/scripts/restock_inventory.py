"""
재고 보강 스크립트

- 모든 상품 옵션(product_variants)의 stock_quantity를 일괄 상향
- --min, --set, --topup 모드 지원
  - 기본: --set 10000 (전 옵션을 특정 값으로 설정)
  - --min X: 재고가 X 미만인 옵션만 X로 맞춤
  - --topup X: 현재 재고에 X만큼 가산
"""

from __future__ import annotations

import argparse
from sqlalchemy import text
from sqlalchemy.orm import Session
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.database import engine


def restock(set_value: int | None, min_value: int | None, topup_value: int | None) -> None:
    with Session(bind=engine) as session:
        if set_value is not None:
            session.execute(text("UPDATE product_variants SET stock_quantity = :v"), {"v": set_value})
        elif min_value is not None:
            session.execute(text("UPDATE product_variants SET stock_quantity = :v WHERE stock_quantity < :v"), {"v": min_value})
        elif topup_value is not None:
            session.execute(text("UPDATE product_variants SET stock_quantity = stock_quantity + :v"), {"v": topup_value})
        else:
            # 기본값: set 10000
            session.execute(text("UPDATE product_variants SET stock_quantity = 10000"))

        session.commit()


def main():
    parser = argparse.ArgumentParser(description="Restock all product variants")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--set", dest="set_value", type=int, help="모든 옵션 재고를 지정 값으로 설정")
    g.add_argument("--min", dest="min_value", type=int, help="재고가 지정값 미만인 옵션만 해당 값으로 설정")
    g.add_argument("--topup", dest="topup_value", type=int, help="모든 옵션 재고에 지정값을 가산")

    args = parser.parse_args()
    restock(args.set_value, args.min_value, args.topup_value)


if __name__ == "__main__":
    main()


