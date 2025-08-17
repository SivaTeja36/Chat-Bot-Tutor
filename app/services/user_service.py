from datetime import datetime
from typing import Dict, List, Tuple

from dataclasses import dataclass
import uuid
from fastapi import (
    BackgroundTasks,
    Depends,
    Request, 
    status,
    HTTPException
)
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.background_tasks.send_email_task import send_bulk_mails
from app.connectors.database_connector import get_db
from app.entities.user import User
from app.models.user_models import (
    ForgotPasswordRequest,
    SetPasswordRequest,
    UpdateUserRequest,
    UserCreationRequest, 
    UserResponse,
    GetUserDetailsResponse,
    UserInfoResponse
)
from app.utils.constants import (
    A_PASSWORD_RESET_EMAIL_HAS_ALREADY_BEEN_SENT,
    EMAIL_ALREADY_EXISTS,
    INVALID_INVITATION_TOKEN,
    PASSWORD_IS_ALREADY_RESET,
    PASSWORD_RESET_SUCCESSFULLY,
    PHONE_NUMBER_ALREADY_EXISTS,
    SET_YOUR_PASSWORD,
    THE_PASSWORD_RESET_EMAIL_HAS_BEEN_SENT_SUCCESSFULLY,
    USER_CREATED_SUCCESSFULLY,
    USER_NOT_FOUND,
    USER_UPDATED_SUCCESSFULLY
)
from app.utils.db_queries import (
    get_user_by_email,
    get_user_by_id, 
    get_user_by_phone_number
)
from app.utils.email_utils import (
    create_bulk_email_request, 
    create_mail_content_for_set_password
)
from app.utils.helpers import (
    apply_filter, 
    apply_pagination, 
    apply_sorting, 
    get_all_users
)


@dataclass
class UserService:
    db: Session = Depends(get_db)

    def get_active_user_by_email(self, email: str):
        return (
            self.db.query(User)
            .filter(
                User.email == email,
                User.is_active == True
            ).first()
        )

    def validate_user_details(self, user_details: User):
        if not user_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND
            )
        
    def _validate_email_not_exists(self, email: str) -> None:
        if get_user_by_email(self.db, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=EMAIL_ALREADY_EXISTS
            )

    def _validate_phone_not_exists(self, phone_number: str) -> None:
        if get_user_by_phone_number(self.db, phone_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=PHONE_NUMBER_ALREADY_EXISTS
            ) 

    def add_user(self, request: UserCreationRequest, logged_in_user_id: int) -> User:
        user = User(
            name=request.name,
            email=request.email,
            gender=request.gender,
            password=request.password,
            role=request.role,
            phone_number=request.phone_number,
            is_password_reset=True,
            is_registered=True,
            created_by=logged_in_user_id,
            updated_by=logged_in_user_id
        )

        self.db.add(user)
        self.db.commit()       

        return user
   
    def create_user(
        self, 
        logged_in_user_id: int, 
        request: UserCreationRequest
    ) -> UserResponse:
        self._validate_email_not_exists(request.email)
        self._validate_phone_not_exists(request.phone_number)

        user = self.add_user(request, logged_in_user_id)

        return UserResponse(
            id=user.id,
            message=USER_CREATED_SUCCESSFULLY
        )
    
    def base_get_user_query(self):
        return self.db.query(User)
    
    def get_matched_user_based_on_search(
        self, 
        query, 
        search: str | None, 
    ):
        if search:
            search_pattern = f"%{search.strip()}%"

            query = query.filter(
                or_(
                    User.name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.phone_number.ilike(search_pattern)
                )
            )    

        return query 
    
    def get_all_user_data(
        self,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[User], int]:
        query = self.base_get_user_query()
        
        query = self.get_matched_user_based_on_search(query, search)
        
        query = apply_filter(
            query=query, 
            main_table=User, 
            filter_by=filter_by, 
            filter_values=filter_values
        )

        query = apply_sorting(
            query=query, 
            table=User, 
            custom_field_sorting=None, 
            sort_by=sort_by, 
            order_by=order_by
        ) 
    
        total_count = query.count()

        if page and page_size:
            query = apply_pagination(query, page, page_size)

        return total_count, query.all()
    
    def get_user_response(
        self, 
        user: User, 
        users: Dict[int, str]
    ) -> GetUserDetailsResponse:
        return GetUserDetailsResponse(
            id=user.id,
            name=user.name, 
            email=user.email,
            gender=user.gender, 
            phone_number=user.phone_number,
            role=user.role,
            created_at=user.created_at,
            created_by=users.get(user.created_by),
            updated_at=user.updated_at,
            updated_by=users.get(user.updated_by),
            is_active=user.is_active
        )
    
    def get_user_responses(
        self,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[GetUserDetailsResponse], int]:
        total_count, users_data = self.get_all_user_data(
            search=search,
            filter_by=filter_by,
            filter_values=filter_values,
            sort_by=sort_by,
            order_by=order_by,
            page=page, 
            page_size=page_size
        )

        users = get_all_users() 

        responses = [
            self.get_user_response(user, users)
            for user in users_data
        ]
        
        return total_count, responses
    
    def get_all_users(
        self,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[GetUserDetailsResponse], int]:
        return self.get_user_responses(
            search=search,
            filter_by=filter_by,
            filter_values=filter_values,
            sort_by=sort_by,
            order_by=order_by,
            page=page, 
            page_size=page_size
        )

    def get_user_by_id(self, user_id: int) -> GetUserDetailsResponse:
        user = get_user_by_id(self.db, user_id)
        self.validate_user_details(user)

        users = get_all_users() 
        return self.get_user_response(user, users)
    
    def update_user(
        self, 
        user: User, 
        request: UpdateUserRequest, 
        logged_in_user_id: int
    ) -> None:
        user.name = request.name
        user.gender = request.gender
        user.role = request.role
        user.phone_number = request.phone_number
        user.updated_at = datetime.now()
        user.updated_by = logged_in_user_id
    
    def update_user_by_id(
        self, 
        logged_in_user_id: int, 
        user_id: int, 
        request: UpdateUserRequest
    ) -> UserResponse:
        user = get_user_by_id(self.db, user_id)
        self.validate_user_details(user)
        
        if request.is_active is not None:
            user.is_active = request.is_active
            user.updated_at = datetime.now()
            user.updated_by = logged_in_user_id
        else:
            self.update_user(user, request, logged_in_user_id)

        self.db.commit()
        
        return UserResponse(
            id=user_id,
            message=USER_UPDATED_SUCCESSFULLY
        )

    def get_user_info(self, request_state: Request):
        return UserInfoResponse(
            id=request_state.state.user.id,
            name=request_state.state.user.name,
            email=request_state.state.user.email,
            role=request_state.state.user.role.capitalize()
        )
    
    def get_user_by_invitation_token(self, invitation_token: str) -> User | None:
        """
            Retrieve a user by their invitation token.
        """
        return (
            self.db.query(User)
            .filter(User.invitation_token == invitation_token)
            .first() 
        )
    
    def validate_user_for_password_reset(self, user: User | None) -> None:
        """
            Validate if the user can reset their password.
        """
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=INVALID_INVITATION_TOKEN,
            )
        
        if user.is_password_reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=PASSWORD_IS_ALREADY_RESET,
            ) 
    
    
    def set_user_password(self, request: SetPasswordRequest) -> UserResponse:
        """
            Reset the user's password and expire the JWT token based on the email.
        """
        user = self.get_user_by_invitation_token(
            invitation_token=request.invitation_token
        )
        self.validate_user_for_password_reset(user=user)

        user.password = request.password
        user.invitation_token = None
        user.is_password_reset = True
        
        self.db.commit()

        return UserResponse(message=PASSWORD_RESET_SUCCESSFULLY)

    def validate_user_for_forgot_password(self, user: User | None) -> None:
        """
            Validate if the user can reset their password.
        """
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND,
            )
        
        if user.invitation_token and not user.is_password_reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=A_PASSWORD_RESET_EMAIL_HAS_ALREADY_BEEN_SENT,
            )
        
    async def _send_set_password_email(
        self, 
        email: str, 
        invitation_token: str
    ) -> None:
        """
            Send a set password email to the user.
        """
        subject = SET_YOUR_PASSWORD
        email_content = create_mail_content_for_set_password(
            email=email, 
            invitation_token=invitation_token
        )
        bulk_email_request = create_bulk_email_request(
            template_id=None,
            placeholder_values={},
            content=email_content,
            subject=subject,
            recipients=[email]
        )
        
        await send_bulk_mails(bulk_email_request)      

    def get_user_by_email(self, email: str) -> User | None:
        """
            Retrieve a user by their email address.
        """
        return (
            self.db.query(User)
            .filter(
                User.email == email
            ).first()   
        )     

    async def forgot_password(self, request: ForgotPasswordRequest) -> UserResponse:
        """
            Handle forgotten password requests by sending a reset email.
        """
        user = self.get_user_by_email(email=request.email)
        self.validate_user_for_forgot_password(user)

        invitation_token = str(uuid.uuid4())
        
        await self._send_set_password_email(
            email=request.email, 
            invitation_token=invitation_token
        )

        user.invitation_token = invitation_token 
        user.is_password_reset = False
        self.db.commit()

        return UserResponse(message=THE_PASSWORD_RESET_EMAIL_HAS_BEEN_SENT_SUCCESSFULLY)
    