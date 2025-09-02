"""
대시보드 관련 API 엔드포인트
고객 이탈률(Churn Rate) 및 위험도 관련 지표 제공
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from db.database import get_db
from db import crud
from db import schemas

router = APIRouter(
    tags=["dashboard"]
)

@router.get(
    "/churn-rate/overall",
    response_model=schemas.ChurnRateOverallResponse,
    summary="전체 이탈률(Churn Rate) 조회"
)
def read_overall_churn_rate(
    reportDt: date = Query(..., description="보고서 기준일 (YYYY-MM-DD)"),
    horizonDays: int = Query(30, description="예측 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    지정된 기간의 전체 고객 이탈률, 유지율, 이탈 고객 수 등의 지표를 조회합니다.
    """
    data = crud.get_overall_churn_rate(db=db, report_dt=reportDt, horizon_days=horizonDays)
    return data

@router.get(
    "/churn-rate/rfm-segments",
    response_model=schemas.ChurnRateRFMResponse,
    summary="RFM 그룹별 이탈률 조회"
)
def read_rfm_churn_rate(
    reportDt: date = Query(..., description="보고서 기준일 (YYYY-MM-DD)"),
    horizonDays: int = Query(30, description="예측 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    RFM(Recency, Frequency, Monetary) 그룹별 고객 수, 이탈률, 위험 사용자 수 지표를 조회합니다.
    """
    data = crud.get_rfm_churn_rate(db=db, report_dt=reportDt, horizon_days=horizonDays)
    return data

@router.get(
    "/churn-risk/distribution",
    response_model=schemas.ChurnRiskDistributionResponse,
    summary="이탈 위험 등급별 고객 분포 조회"
)
def read_churn_risk_distribution(
    reportDt: date = Query(..., description="보고서 기준일 (YYYY-MM-DD)"),
    horizonDays: int = Query(30, description="예측 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    이탈 위험 등급(VH, H, M, L)에 따른 고객 수와 비율 분포를 조회합니다.
    """
    data = crud.get_churn_risk_distribution(db=db, report_dt=reportDt, horizon_days=horizonDays)
    return data

@router.get(
    "/high-risk-users",
    response_model=schemas.HighRiskUserListResponse,
    summary="고위험 이탈 사용자 목록 조회"
)
def read_high_risk_users(
    reportDt: date = Query(..., description="보고서 기준일 (YYYY-MM-DD)"),
    horizonDays: int = Query(30, description="예측 기간 (일)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db)
):
    """
    이탈 확률이 높은 고위험 사용자 목록과 추천 액션을 페이징하여 조회합니다.
    """
    data = crud.get_high_risk_users(db=db, report_dt=reportDt, horizon_days=horizonDays, page=page, per_page=per_page)
    return data
