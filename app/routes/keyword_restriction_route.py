from typing import List, Optional

from fastapi import (
    APIRouter, 
    Depends,
    Query,
    Request,
    status
)
from pydantic import PositiveInt

from app.models.base_response_models import (
    ApiResponse, 
    GetApiResponse,
    SuccessMessageResponse
)
from app.models.keyword_restriction_models import (
    GetKeywordRestrictionResponse,
    KeywordRestrictionRequest,
    GetKidKeywordRestrictionResponse
)
from app.services.keyword_restriction_service import KeywordRestrictionService
from app.utils.constants import UPDATED_AT
from app.utils.enums import OrderByTypes

router = APIRouter(
    prefix="", 
    tags=["KEYWORD RESTRICTION MANAGEMENT SERVICE"]
)


@router.post(
    "/keyword-restrictions", 
    response_model=ApiResponse[SuccessMessageResponse], 
    status_code=status.HTTP_201_CREATED
)
async def create_keyword_restrictions(
    request_state: Request,
    request: KeywordRestrictionRequest, 
    service: KeywordRestrictionService = Depends(KeywordRestrictionService)
) -> ApiResponse[SuccessMessageResponse]:
    return ApiResponse(data=service.create_keyword_restrictions(
            logged_in_user_id=request_state.state.user.id, 
            request=request
        )
    )


@router.get(
    "/keyword-restrictions", 
    response_model=GetApiResponse[List[GetKeywordRestrictionResponse]], 
    status_code=status.HTTP_200_OK
)
async def get_all_keyword_restrictions( 
    search: Optional[str] = Query(default=None),
    filter_by: Optional[str] = Query(default=None),
    filter_values: Optional[str] = Query(default=None),
    sort_by: Optional[str] = Query(default=UPDATED_AT),
    order_by: Optional[OrderByTypes] = OrderByTypes.DESC,
    page: Optional[PositiveInt] = Query(default=1),
    page_size: Optional[PositiveInt] = Query(default=10),
    service: KeywordRestrictionService = Depends(KeywordRestrictionService)
) -> GetApiResponse[List[GetKeywordRestrictionResponse]]:
    total_count, response = service.get_all_keyword_restrictions(
        search=search,
        filter_by=filter_by,
        filter_values=filter_values,
        sort_by=sort_by,
        order_by=order_by,
        page=page,
        page_size=page_size
    )

    return GetApiResponse(
        total_items=total_count,
        page=page,
        page_size=page_size,
        data=response,
    )


@router.get(
    "/keyword-restrictions/{restriction_id}", 
    response_model=ApiResponse[GetKeywordRestrictionResponse], 
    status_code=status.HTTP_200_OK
)
async def get_keyword_restrictions_by_id( 
    restriction_id: PositiveInt,
    service: KeywordRestrictionService = Depends(KeywordRestrictionService)
) -> ApiResponse[List[GetKeywordRestrictionResponse]]:
    return ApiResponse(data=service.get_keyword_restrictions_by_id(restriction_id))
  

@router.put(
    "/keyword-restrictions/{restriction_id}", 
    response_model=ApiResponse[SuccessMessageResponse], 
    status_code=status.HTTP_201_CREATED
)
async def update_keyword_restrictions_by_id(
    request_state: Request,
    restriction_id: PositiveInt,
    request: KeywordRestrictionRequest, 
    service: KeywordRestrictionService = Depends(KeywordRestrictionService)
) -> ApiResponse[SuccessMessageResponse]:
    return ApiResponse(data=service.update_keyword_restrictions_by_id(
            logged_in_user_id=request_state.state.user.id, 
            restriction_id=restriction_id,
            request=request
        )
    )


@router.post(
    "/keyword-restrictions/{keyword_restriction_id}/kids", 
    response_model=ApiResponse[SuccessMessageResponse], 
    status_code=status.HTTP_201_CREATED
)
async def map_keyword_restriction_to_kid(
    request_state: Request,
    keyword_restriction_id: PositiveInt,
    kid_id: PositiveInt,
    service: KeywordRestrictionService = Depends(KeywordRestrictionService)
) -> ApiResponse[SuccessMessageResponse]:
    return ApiResponse(data=service.map_keyword_restriction_to_kid(
            keyword_restriction_id=keyword_restriction_id,
            kid_id=kid_id,
            logged_in_user_id=request_state.state.user.id
        )
    )


@router.get(
    "/kids-keyword-restrictions", 
    response_model=ApiResponse[List[GetKidKeywordRestrictionResponse]], 
    status_code=status.HTTP_200_OK
)
async def get_all_kids_mapped_keyword_restrictions(
    order_by: Optional[OrderByTypes] = OrderByTypes.DESC,
    sort_by: Optional[str] = UPDATED_AT,
    page: Optional[PositiveInt] = Query(default=1),
    page_size: Optional[PositiveInt] = Query(default=10),
    service: KeywordRestrictionService = Depends(KeywordRestrictionService)
) -> ApiResponse[List[GetKidKeywordRestrictionResponse]]:
    total_count, response = service.get_all_kids_mapped_keyword_restrictions(
        order_by=order_by,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )

    return GetApiResponse(
        total_items=total_count,
        page=page,
        page_size=page_size,
        data=response,
    )


@router.get(
    "/keyword-restrictions/{keyword_restriction_id}/kids", 
    response_model=ApiResponse[GetKidKeywordRestrictionResponse], 
    status_code=status.HTTP_200_OK
)
async def get_mapped_keyword_restriction_for_kid_by_id(
    keyword_restriction_id: PositiveInt,
    kid_id: PositiveInt,
    service: KeywordRestrictionService = Depends(KeywordRestrictionService)
) -> ApiResponse[GetKidKeywordRestrictionResponse]:
    return ApiResponse(data=service.get_mapped_keyword_restriction_for_kid(
            keyword_restriction_id=keyword_restriction_id,
            kid_id=kid_id
        )
    )


@router.put(
    "/keyword-restrictions/{keyword_restriction_id}/kids", 
    response_model=ApiResponse[SuccessMessageResponse], 
    status_code=status.HTTP_200_OK
)
async def update_mapped_keyword_restriction_for_kid_by_id(
    request_state: Request,
    keyword_restriction_id: PositiveInt,
    kid_id: PositiveInt,
    service: KeywordRestrictionService = Depends(KeywordRestrictionService)
) -> ApiResponse[SuccessMessageResponse]:
    return ApiResponse(data=service.update_mapped_keyword_restriction_for_kid_by_id(
            logged_in_user_id=request_state.state.user.id, 
            keyword_restriction_id=keyword_restriction_id,
            kid_id=kid_id
        )
    )


@router.delete(
    "/keyword-restrictions/{keyword_restriction_id}/kids", 
    response_model=ApiResponse[SuccessMessageResponse], 
    status_code=status.HTTP_200_OK
)
async def delete_mapped_keyword_restriction_for_kid_by_id(
    keyword_restriction_id: PositiveInt,
    kid_id: PositiveInt,
    service: KeywordRestrictionService = Depends(KeywordRestrictionService)
) -> ApiResponse[SuccessMessageResponse]:
    return ApiResponse(data=service.delete_mapped_keyword_restriction_for_kid_by_id(
            keyword_restriction_id=keyword_restriction_id,
            kid_id=kid_id
        )
    )