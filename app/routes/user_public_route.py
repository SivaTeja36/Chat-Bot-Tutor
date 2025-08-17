from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.models.base_response_models import ApiResponse
from app.models.user_models import (
    ForgotPasswordRequest, 
    SetPasswordRequest, 
    UserResponse
)
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users", 
    tags=["USER PUBLIC MANAGEMENT SERVICE"]
)


@router.post(
    "/set-password", 
    response_model=ApiResponse[UserResponse], 
    status_code=status.HTTP_201_CREATED
)
async def set_password(
    request: SetPasswordRequest,
    service: UserService = Depends(UserService)
) -> ApiResponse[UserResponse]:
    """
        Reset the user's password.
    """
    return ApiResponse(data=service.set_user_password(request))


@router.post(
    "/forgot-password", 
    response_model=ApiResponse[UserResponse], 
    status_code=status.HTTP_201_CREATED
)
async def forgot_password(
    request: ForgotPasswordRequest,
    service: UserService = Depends(UserService)
) -> ApiResponse[UserResponse]:
    """
        Initiate the password recovery process.
    """
    return ApiResponse(data=await service.forgot_password(request))