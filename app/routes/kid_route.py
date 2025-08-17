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
from app.models.kid_models import (
    GetQuestionsHistoryResponse,
    KidRequest,
    GetKidResponse
)
from app.services.kid_service import KidService
from app.utils.constants import UPDATED_AT
from app.utils.enums import OrderByTypes

router = APIRouter(
    prefix="/kids", 
    tags=["KIDS MANAGEMENT SERVICE"]
)


@router.post(
    "", 
    response_model=ApiResponse[SuccessMessageResponse], 
    status_code=status.HTTP_201_CREATED
)
async def create_kid(
    request_state: Request,
    request: KidRequest, 
    service: KidService = Depends(KidService)
) -> ApiResponse[SuccessMessageResponse]:
    return ApiResponse(data=service.create_kid(
            logged_in_user_id=request_state.state.user.id, 
            request=request
        )
    )


@router.get(
    "", 
    response_model=GetApiResponse[List[GetKidResponse]], 
    status_code=status.HTTP_200_OK
)
async def get_all_kids( 
    search: Optional[str] = Query(default=None),
    filter_by: Optional[str] = Query(default=None),
    filter_values: Optional[str] = Query(default=None),
    sort_by: Optional[str] = Query(default=UPDATED_AT),
    order_by: Optional[OrderByTypes] = OrderByTypes.DESC,
    page: Optional[PositiveInt] = Query(default=1),
    page_size: Optional[PositiveInt] = Query(default=10),
    service: KidService = Depends(KidService)
) -> GetApiResponse[List[GetKidResponse]]:
    total_count, response = service.get_all_kids(
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
    "/{kid_id}", 
    response_model=ApiResponse[GetKidResponse], 
    status_code=status.HTTP_200_OK
)
async def get_kid_by_id(
    kid_id: PositiveInt, 
    service: KidService = Depends(KidService)
) -> ApiResponse[GetKidResponse]:
    return ApiResponse(data=service.get_kid_by_id(kid_id))


@router.put(
    "/{kid_id}", 
    response_model=ApiResponse[SuccessMessageResponse], 
    status_code=status.HTTP_200_OK
)
async def update_kid_by_id(
    request_state: Request,
    kid_id: PositiveInt, 
    request: KidRequest,
    service: KidService = Depends(KidService)
) -> ApiResponse[SuccessMessageResponse]:
    return ApiResponse(data=service.update_kid_by_id(
            logged_in_user_id=request_state.state.user.id, 
            kid_id=kid_id,
            request=request
        )
    )


@router.delete(
    "/{kid_id}", 
    response_model=ApiResponse[SuccessMessageResponse], 
    status_code=status.HTTP_200_OK
)
async def update_kid_by_id(
    kid_id: PositiveInt, 
    service: KidService = Depends(KidService)
) -> ApiResponse[SuccessMessageResponse]:
    return ApiResponse(data=service.delete_kid_by_id( 
            kid_id=kid_id
        )
    )


@router.post(
    "/{kid_id}", 
    response_model=ApiResponse[SuccessMessageResponse], 
    status_code=status.HTTP_201_CREATED
)
async def create_question(
    kid_id: PositiveInt,
    request: KidRequest, 
    service: KidService = Depends(KidService)
) -> ApiResponse[SuccessMessageResponse]:
    return ApiResponse(data=service.create_question(
            kid_id=kid_id,
            request=request
        )
    )


@router.get(
    "/{kid_id}", 
    response_model=ApiResponse[List[GetQuestionsHistoryResponse]], 
    status_code=status.HTTP_200_OK
)
async def get_kid_questions_history_by_id(
    kid_id: PositiveInt, 
    service: KidService = Depends(KidService)
) -> ApiResponse[List[GetQuestionsHistoryResponse]]:
    return ApiResponse(data=service.get_kid_questions_history_by_id(kid_id))