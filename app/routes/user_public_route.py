from fastapi import (
    APIRouter, 
    Depends, 
    status
)
from pydantic import EmailStr

from app.models.base_response_models import (
    ApiResponse, 
    SuccessMessageResponse
)
from app.models.user_models import (
    ForgotPasswordRequest,
    RegisterUserRequest, 
    SetPasswordRequest, 
    UserResponse
)
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users", 
    tags=["USER PUBLIC MANAGEMENT SERVICE"]
)


@router.post(
    "/send-verification",
    response_model=ApiResponse[SuccessMessageResponse],
    status_code=status.HTTP_201_CREATED
)
async def send_verification_mail_to_user(
    request: RegisterUserRequest, 
    service: UserService = Depends(UserService)
) -> ApiResponse[SuccessMessageResponse]:
    """
        Authenticate a user and generate an jwt token.
    """
    return ApiResponse(data=await service.send_verification_mail_to_user(request))


@router.get(
    "/verify-email", 
    response_model=ApiResponse[UserResponse], 
    status_code=status.HTTP_201_CREATED
)
async def verify_user_email(
    email: EmailStr,
    service: UserService = Depends(UserService)
) -> ApiResponse[UserResponse]:
    """
        Verify user in application
    """
    return ApiResponse(data=service.verify_user_email(email))


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