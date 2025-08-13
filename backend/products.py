"""
상품 관련 API 엔드포인트
상품 목록 조회, 상세 조회 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from crud import (
    get_products_with_filters,
    get_product_by_id_with_variants,
    get_product_variants
)
from schemas import (
    ProductListResponse,
    ProductDetailResponse,
    ProductListPaginatedResponse,
    ProductVariantResponse
)

router = APIRouter(tags=["products"])

@router.get("/", response_model=ProductListPaginatedResponse)
async def get_products(
    category_id: Optional[int] = Query(None, description="카테고리 ID"),
    min_price: Optional[float] = Query(None, ge=0, description="최소 가격"),
    max_price: Optional[float] = Query(None, ge=0, description="최대 가격"),
    search: Optional[str] = Query(None, max_length=100, description="검색어"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지당 상품 수"),
    db: Session = Depends(get_db)
):
    """
    상품 목록 조회 (필터링 및 페이지네이션)
    
    - **category_id**: 특정 카테고리의 상품만 조회
    - **min_price**: 최소 가격 필터
    - **max_price**: 최대 가격 필터
    - **search**: 상품명 검색
    - **page**: 페이지 번호 (1부터 시작)
    - **size**: 페이지당 상품 수 (최대 100개)
    """
    try:
        # 페이지네이션 계산
        skip = (page - 1) * size
        
        # 필터링된 상품 조회
        products, total_count = get_products_with_filters(
            db=db,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            search=search,
            skip=skip,
            limit=size
        )
        
        # 페이지네이션 정보 계산
        total_pages = (total_count + size - 1) // size
        has_next = page < total_pages
        has_prev = page > 1
        
        # 응답 데이터 구성
        product_responses = []
        for product in products:
            # 사용 가능한 옵션 수 계산
            available_variants = len(product.variants) if product.variants else 0
            
            product_response = ProductListResponse(
                product_id=product.product_id,
                product_name=product.product_name,
                description=product.description,
                price=product.price,
                category_name=product.category.category_name if product.category else "카테고리 없음",
                created_at=product.created_at,
                available_variants=available_variants
            )
            product_responses.append(product_response)
        
        return ProductListPaginatedResponse(
            products=product_responses,
            total_count=total_count,
            total_pages=total_pages,
            current_page=page,
            page_size=size,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        print(f"상품 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="상품 목록 조회 중 오류가 발생했습니다.")

@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    상품 상세 정보 조회
    
    - **product_id**: 조회할 상품의 ID
    """
    try:
        # 상품 정보 조회
        product = get_product_by_id_with_variants(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
        
        # 상품 옵션 정보 조회
        variants = get_product_variants(db, product_id)
        
        # 옵션 응답 데이터 구성
        variant_responses = []
        for variant in variants:
            variant_response = ProductVariantResponse(
                variant_id=variant.variant_id,
                color=variant.color,
                size=variant.size,
                stock_quantity=variant.stock_quantity
            )
            variant_responses.append(variant_response)
        
        # 상품 상세 응답 데이터 구성
        return ProductDetailResponse(
            product_id=product.product_id,
            product_name=product.product_name,
            description=product.description,
            price=product.price,
            category_name=product.category.category_name if product.category else "카테고리 없음",
            created_at=product.created_at,
            variants=variant_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"상품 상세 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="상품 상세 조회 중 오류가 발생했습니다.")
