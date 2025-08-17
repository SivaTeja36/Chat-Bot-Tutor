from datetime import (
    datetime, 
    timedelta
)
from dataclasses import dataclass
import os
from urllib.parse import quote
from jose import jwt

from fastapi import (
    Depends,
    status,
    HTTPException,
)

from app.background_tasks.send_email_task import send_bulk_mails
from app.entities.user import User
from app.models.auth_models import (
    LoginRequest, 
    LoginResponse
)
from app.models.base_response_models import SuccessMessageResponse
from app.models.user_models import RegisterUserRequest
from app.utils.email_utils import (
    create_bulk_email_request, 
    create_user_verification_email
)
from .user_service import UserService
from app.utils.auth_dependencies import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)
from app.utils.constants import (
    INCORRECT_PASSWORD, 
    USER_NOT_FOUND,
    VERIFICATION_EMAIL_SENT_SUCCESSFULLY
)


@dataclass
class AuthService:
    user_service: UserService = Depends(UserService)
    VERIFICATION_URL = os.getenv("VERIFICATION_URL")
    
    def create_claims(self, user: User):
        claims = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "gender": user.gender,
                "phone_number": user.phone_number,
                "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            }
        return claims
    
    def generate_token_response(self, claims: dict) -> LoginResponse:
        """
            Generate JWT token and return the login response.
        """
        try:
            token = jwt.encode(
                claims=claims, 
                key=SECRET_KEY, 
                algorithm=ALGORITHM
            )
            return LoginResponse(
                token=token,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


    def login(self, request: LoginRequest) -> LoginResponse:
        """
            Authenticate a user and generate a JWT token upon successful login.
        """
        user = self.user_service.get_active_user_by_email(request.email)
        
        if user:
            if user.verify_password(request.password):
                claims = self.create_claims(user)
                
                return self.generate_token_response(
                    claims=claims
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=INCORRECT_PASSWORD
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=USER_NOT_FOUND
            )
        
    def create_claims_for_parent_registration(self, request: RegisterUserRequest) -> dict:
        """
            Create JWT claims for admin registration verification.
        """
        claims = {
            "name": request.name,
            "email": request.email,
            "phone_number": request.phone_number,
            "gender": request.gender,
            "role": "PARENT",
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        return claims    

    async def send_verification_email(self, user_email: str, token: str):
        """
            Generate a verificaStion token, create a verification URL, and send the email.
        """
        encoded_email = quote(user_email)
        encoded_invitation_token = quote(token)
        verification_url = f"{self.VERIFICATION_URL}?email={encoded_email}&token={encoded_invitation_token}"
        subject = "Verify your email address"
        email_content = create_user_verification_email(url=verification_url)
        
        bulk_email_request = create_bulk_email_request(
            template_id=None,
            placeholder_values={},
            content=email_content,
            subject=subject,
            recipients=[user_email]
        )
        await send_bulk_mails(
            bulk_email_request=bulk_email_request
        ) 
        
    async def verify_email(self, request: RegisterUserRequest) -> SuccessMessageResponse:
        """
            Initiate the email verification process for admin registration.
        """
        claims = self.create_claims_for_parent_registration(request)
        token = jwt.encode(
            claims=claims,
            key=SECRET_KEY,
            algorithm=ALGORITHM
        )
        await self.send_verification_email(request.email, token)
        return SuccessMessageResponse(message=VERIFICATION_EMAIL_SENT_SUCCESSFULLY)