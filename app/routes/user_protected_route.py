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
    GetApiResponse
)
from app.models.user_models import (
    UpdateUserRequest,
    UserCreationRequest, 
    UserResponse,
    GetUserDetailsResponse,
    UserInfoResponse
)
from app.services.user_service import UserService
from app.utils.constants import UPDATED_AT
from app.utils.enums import OrderByTypes

router = APIRouter(prefix="/users", tags=["USER MANAGEMENT SERVICE"])


@router.post(
    "", 
    response_model=ApiResponse[UserResponse], 
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    request_state: Request,
    password: str, 
    service: UserService = Depends(UserService)
) -> ApiResponse[UserResponse]:
    request = UserCreationRequest(
        name=request_state.state.user.name,
        email=request_state.state.user.email,
        gender=request_state.state.user.gender,
        password=password,
        role=request_state.state.user.role,
        phone_number=request_state.state.user.phone_number
    )
    return ApiResponse(data=service.create_user(
            logged_in_user_id=request_state.state.user.id, 
            request=request
        )
    )


@router.get(
    "", 
    response_model=GetApiResponse[List[GetUserDetailsResponse]], 
    status_code=status.HTTP_200_OK
)
async def get_all_users( 
    search: Optional[str] = Query(default=None),
    filter_by: Optional[str] = Query(default=None),
    filter_values: Optional[str] = Query(default=None),
    sort_by: Optional[str] = Query(default=UPDATED_AT),
    order_by: Optional[OrderByTypes] = OrderByTypes.DESC,
    page: Optional[PositiveInt] = Query(default=1),
    page_size: Optional[PositiveInt] = Query(default=10),
    service: UserService = Depends(UserService)
) -> GetApiResponse[List[GetUserDetailsResponse]]:
    total_count, response = service.get_all_users(
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
    "/data/{user_id}", 
    response_model=ApiResponse[GetUserDetailsResponse], 
    status_code=status.HTTP_200_OK
)
async def get_user_by_id(
    user_id: PositiveInt, 
    service: UserService = Depends(UserService)
) -> ApiResponse[GetUserDetailsResponse]:
    return ApiResponse(data=service.get_user_by_id(user_id))


@router.put(
    "/data/{user_id}", 
    response_model=ApiResponse[UserResponse], 
    status_code=status.HTTP_200_OK
)
async def update_user_by_id(
    request_state: Request,
    user_id: PositiveInt, 
    request: UpdateUserRequest,
    service: UserService = Depends(UserService)
) -> ApiResponse[UserResponse]:
    return ApiResponse(data=service.update_user_by_id(
            logged_in_user_id=request_state.state.user.id, 
            user_id=user_id,
            request=request
        )
    )


@router.get(
    "/info", 
    response_model=ApiResponse[UserInfoResponse], 
    status_code=status.HTTP_200_OK
)
async def get_user_info(
    request_state: Request,
    service: UserService = Depends(UserService)
) -> ApiResponse[UserInfoResponse]:
    return ApiResponse(data=service.get_user_info(request_state))