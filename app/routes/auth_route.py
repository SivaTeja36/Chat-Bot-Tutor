from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.models.auth_models import (
    LoginRequest, 
    LoginResponse
)
from app.models.base_response_models import ApiResponse
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