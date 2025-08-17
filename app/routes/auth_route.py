from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.models.auth_models import (
    LoginRequest, 
    LoginResponse
)
from app.models.base_response_models import (
    ApiResponse, 
    SuccessMessageResponse
)
from app.models.user_models import RegisterUserRequest
from app.services.auth_service import AuthService

router = APIRouter(tags=["AUTHENTICATION MANAGEMENT SERVICE"])


@router.post(
    "/login",
    response_model=ApiResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest, 
    service: AuthService = Depends(AuthService)
) -> ApiResponse[LoginResponse]:
    return ApiResponse(data=service.login(request))


@router.post(
    "/verify-email",
    response_model=ApiResponse[SuccessMessageResponse],
    status_code=status.HTTP_200_OK
)
async def verify_email(
    request: RegisterUserRequest, 
    service: AuthService = Depends(AuthService)
) -> ApiResponse[SuccessMessageResponse]:
    """
        Authenticate a user and generate an jwt token.
    """
    return ApiResponse(data=await service.verify_email(request))