from datetime import datetime
from typing import Optional
from pydantic import (
    BaseModel, 
    EmailStr,
    validator,
    Field
)

from app.utils.validation import validate_password

class RegisterUserRequest(BaseModel):
    name: str
    email: EmailStr
    gender: str
    role: str
    phone_number: str


class ConfirmRegistrationRequest(BaseModel):
    password: str
    token: str

    @validator("password")
    def validate_user_creation_password(cls, password: str):
        return validate_password(password)


class UserCreationRequest(BaseModel):
    name: str
    email: EmailStr
    gender: str
    password: str
    role: str
    phone_number: str

    @validator("password")
    def validate_user_creation_password(cls, password: str):
        return validate_password(password)


class UserResponse(BaseModel):
    id: Optional[int] = None
    message: str


class GetUserDetailsResponse(BaseModel):
    id: int
    name: str 
    email: str 
    gender: str
    phone_number: str
    role: str
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    is_active: bool


class UpdateUserRequest(BaseModel):
    name: str
    gender: str
    role: str
    phone_number: str
    is_active: Optional[bool] = None


class CurrentContextUser:
    id: Optional[int] = None
    name: str
    email: str
    role: str
    gender: str
    phone_number: str


class UserInfoResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str


class SetPasswordRequest(BaseModel):
    """
        Model for handling requests to set a new password.
    """
    invitation_token: str = Field(..., min_length=36)
    password: str = Field(..., min_length=8, max_length=16)

    @validator("password")
    def validate_set_password(cls, password: str):
        return validate_password(password)
    

class ForgotPasswordRequest(BaseModel):
    """
        Model for handling requests to initiate a password reset.
    """
    email: EmailStr = Field(..., min_length=8, max_length=100)    
        