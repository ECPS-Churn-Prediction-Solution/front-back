"""
카테고리 관련 API 엔드포인트
사이트 메뉴 구성을 위한 카테고리 조회 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from crud import get_all_categories
from schemas import CategoryResponse

router = APIRouter(tags=["categories"])

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """
    전체 카테고리 목록 조회
    
    사이트 메뉴 구성을 위한 전체 카테고리 목록을 제공합니다.
    상위 카테고리와 하위 카테고리를 모두 포함합니다.
    """
    try:
        # 전체 카테고리 조회
        categories = get_all_categories(db)
        
        # 응답 데이터 구성
        category_responses = []
        for category in categories:
            category_response = CategoryResponse(
                category_id=category.category_id,
                category_name=category.category_name,
                parent_id=category.parent_id
            )
            category_responses.append(category_response)
        
        return category_responses
        
    except Exception as e:
        print(f"카테고리 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="카테고리 목록 조회 중 오류가 발생했습니다.")
