"""
상품 관련 API 엔드포인트
상품 목록 조회, 상세 조회 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.crud import (
    get_all_products,
    get_product_by_id_with_variants,
    get_product_variants
)
from db.schemas import (
    ProductListResponse,
    ProductDetailResponse,
    ProductVariantResponse
)

router = APIRouter(tags=["products"])

@router.get("/", response_model=List[ProductListResponse])
async def get_products(db: Session = Depends(get_db)):
    """
    전체 상품 목록 조회 (간단 버전)
    """
    try:
        # 전체 상품 조회
        products = get_all_products(db)
        
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
        
        return product_responses
        
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
