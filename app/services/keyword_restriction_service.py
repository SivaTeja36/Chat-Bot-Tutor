from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from fastapi import (
    Depends, 
    HTTPException, 
    status
)
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.connectors.database_connector import get_db
from app.entities.keyword_restriction import KeywordRestrictions
from app.entities.kid import Kid
from app.entities.kid_keyword_restriction import KidKeywordRestrictions
from app.models.base_response_models import SuccessMessageResponse
from app.models.keyword_restriction_models import (
    GetKeywordRestrictionResponse,
    GetKidKeywordRestrictionResponse,
    KeywordRestrictionRequest
)
from app.models.kid_models import GetKidResponse
from app.utils.constants import (
    A_KEYWORD_RESTRICTION_WITH_THIS_TITLE_ALREADY_EXISTS,
    KEYWORD_RESTRICTION_ALREADY_MAPPED_TO_KID,
    KEYWORD_RESTRICTION_NOT_FOUND,
    KEYWORD_RESTRICTION_NOT_MAPPED_TO_KID, 
    KEYWORD_RESTRICTIONS_CREATED_SUCCESSFULLY,
    KEYWORD_RESTRICTIONS_UPDATED_SUCCESSFULLY,
    KID_NOT_FOUND
)
from app.utils.db_queries import get_kid_by_id
from app.utils.helpers import (
    apply_filter, 
    apply_pagination, 
    apply_sorting, 
    get_all_users
)


load_dotenv()

@dataclass
class KeywordRestrictionService:
    db: Session = Depends(get_db)

    def validate_title_exists(self, title: str) -> bool:
        existing_restriction = self.db.query(KeywordRestrictions).filter(
            KeywordRestrictions.title == title
        ).first()

        if existing_restriction:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=A_KEYWORD_RESTRICTION_WITH_THIS_TITLE_ALREADY_EXISTS
            )

        return existing_restriction is not None

    def create_keyword_restrictions(
        self, 
        logged_in_user_id: int, 
        request: KeywordRestrictionRequest
    ) -> SuccessMessageResponse:
        self.validate_title_exists(request.title)

        new_keyword_restriction = KeywordRestrictions(
            title=request.title,
            keywords=list(set(request.keywords)),
            created_by=logged_in_user_id,
            updated_by=logged_in_user_id
        )

        self.db.add(new_keyword_restriction)
        self.db.commit()
   
        return SuccessMessageResponse(
            id=new_keyword_restriction.id,
            message=KEYWORD_RESTRICTIONS_CREATED_SUCCESSFULLY
        )
    
    def base_get_keyword_restrictions_query(self):
        return self.db.query(KeywordRestrictions)
    
    def get_matched_keyword_restrictions_based_on_search(
        self, 
        query, 
        search: str | None, 
    ):
        if search:
            search_pattern = f"%{search.strip()}%"

            query = query.filter(
                sa.or_(
                    KeywordRestrictions.title.ilike(search_pattern)
                )
            )    

        return query 
    
    def get_all_keyword_restrictions_data(
        self,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[KeywordRestrictions], int]:
        query = self.base_get_keyword_restrictions_query()
        
        query = self.get_matched_keyword_restrictions_based_on_search(query, search)
        
        query = apply_filter(
            query=query, 
            main_table=KeywordRestrictions, 
            filter_by=filter_by, 
            filter_values=filter_values
        )

        query = apply_sorting(
            query=query, 
            table=KeywordRestrictions, 
            custom_field_sorting=None, 
            sort_by=sort_by, 
            order_by=order_by
        ) 
    
        total_count = query.count()

        if page and page_size:
            query = apply_pagination(query, page, page_size)

        return total_count, query.all()
    
    def get_keyword_restrictions_response(
        self, 
        keyword_restrictions: KeywordRestrictions, 
        users: Dict[int, str]
    ) -> GetKeywordRestrictionResponse:
        return GetKeywordRestrictionResponse(
            id=keyword_restrictions.id, 
            title=keyword_restrictions.title, 
            keywords=keyword_restrictions.keywords,
            created_at=keyword_restrictions.created_at, 
            created_by=users.get(keyword_restrictions.created_by),
            updated_at=keyword_restrictions.updated_at,
            updated_by=users.get(keyword_restrictions.updated_by)
        )
    
    def get_keyword_restrictions_responses(
        self,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[GetKeywordRestrictionResponse], int]:
        total_count, keyword_restrictions = self.get_all_keyword_restrictions_data(
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
            self.get_keyword_restrictions_response(keyword_restriction, users)
            for keyword_restriction in keyword_restrictions
        ]
        
        return total_count, responses
    
    def get_all_keyword_restrictions(
        self,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[GetKeywordRestrictionResponse], int]:
        return self.get_keyword_restrictions_responses(
            search=search,
            filter_by=filter_by,
            filter_values=filter_values,
            sort_by=sort_by,
            order_by=order_by,
            page=page, 
            page_size=page_size
        )
    
    def get_keyword_restrictions_data_by_id(self, restriction_id: int) -> KeywordRestrictions:
        keyword_restriction = self.db.query(KeywordRestrictions).filter(
            KeywordRestrictions.id == restriction_id
        ).first()

        return keyword_restriction
    
    def validate_keyword_restriction_exists(self, keyword_restriction: KeywordRestrictions) -> bool:
        if not keyword_restriction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=KEYWORD_RESTRICTION_NOT_FOUND
            )
    
    def get_keyword_restrictions_by_id(self, restriction_id: int) -> GetKeywordRestrictionResponse:
        keyword_restriction = self.get_keyword_restrictions_data_by_id(restriction_id)
        self.validate_keyword_restriction_exists(keyword_restriction)

        users = get_all_users() 

        return self.get_keyword_restrictions_response(keyword_restriction, users)
        
    def update_keyword_restrictions_by_id(
        self, 
        logged_in_user_id: int, 
        restriction_id: int,
        request: KeywordRestrictionRequest
    ) -> SuccessMessageResponse:
        keyword_restriction = self.get_keyword_restrictions_data_by_id(restriction_id)
        self.validate_keyword_restriction_exists(keyword_restriction)
        
        if keyword_restriction.title != request.title:
            self.validate_title_exists(request.title)

        keyword_restriction.title = request.title
        keyword_restriction.keywords = list(set(request.keywords))
        keyword_restriction.updated_at = datetime.now()
        keyword_restriction.updated_by = logged_in_user_id

        self.db.commit()
   
        return SuccessMessageResponse(
            id=keyword_restriction.id,
            message=KEYWORD_RESTRICTIONS_UPDATED_SUCCESSFULLY
        )
    
    def get_kid_keyword_restriction_query(self, restriction_id: int, kid_id: int):
        return self.db.query(KidKeywordRestrictions).filter(
            KidKeywordRestrictions.id == restriction_id,
            KidKeywordRestrictions.kid_id == kid_id
        ).first()
    
    def validate_kid_keyword_restriction_already_exists(self, kid_keyword_restriction) -> bool:
        if kid_keyword_restriction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=KEYWORD_RESTRICTION_ALREADY_MAPPED_TO_KID
            )
    
    def map_keyword_restriction_to_kid(
        self, 
        restriction_id: int,
        kid_id: int,
        logged_in_user_id: int
    ) -> SuccessMessageResponse:
        kid_keyword_restriction = self.get_kid_keyword_restriction_query(restriction_id, kid_id)
        self.validate_kid_keyword_restriction_already_exists(kid_keyword_restriction)

        new_kid_keyword_restriction = KidKeywordRestrictions(
            kid_id=kid_id,
            restriction_id=restriction_id,
            created_by=logged_in_user_id,
            updated_by=logged_in_user_id
        )
        self.db.add(new_kid_keyword_restriction)
        self.db.commit()

        return SuccessMessageResponse(
            id=new_kid_keyword_restriction.id,
            message=KEYWORD_RESTRICTIONS_CREATED_SUCCESSFULLY
        )
    
    def validate_kid_keyword_restriction_exists(self, kid_keyword_restriction) -> bool:
        if not kid_keyword_restriction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=KEYWORD_RESTRICTION_NOT_MAPPED_TO_KID
            )
        
    def validate_kid_exists(self, kid: Kid) -> bool:
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=KID_NOT_FOUND
            )
    def base_get_kids_mapped_keyword_restrictions_query(self):
        return self.db.query(KidKeywordRestrictions)
    
    def get_all_kids_mapped_keyword_restrictions_data(
        self,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[KidKeywordRestrictions], int]:
        query = self.base_get_keyword_restrictions_query()
        
        query = apply_sorting(
            query=query, 
            table=KidKeywordRestrictions, 
            custom_field_sorting=None, 
            sort_by=sort_by, 
            order_by=order_by
        ) 
    
        total_count = query.count()

        if page and page_size:
            query = apply_pagination(query, page, page_size)

        return total_count, query.all()
    
    def get_kids_mapped_keyword_restrictions_response(
        self,
        kid_keyword_restriction: KidKeywordRestrictions,
        users: Dict[int, str]
    ) -> GetKidKeywordRestrictionResponse:
        kid = self.db.query(Kid).filter(Kid.id == kid_keyword_restriction.kid_id).first()
        keyword_restrictions = self.get_keyword_restrictions_by_id(kid_keyword_restriction.restriction_id)
        keyword_restrictions_response = self.get_keyword_restrictions_response(users, keyword_restrictions)

        get_kid_response = GetKidResponse(
            id=kid.id,
            name=kid.name,
            age=kid.age,
            gender=kid.gender,
            school=kid.school,
            standard=kid.standard,
            created_at=kid.created_at,
            created_by=users.get(kid.created_by),
            updated_at=kid.updated_at,
            updated_by=users.get(kid.updated_by)
        )

        return GetKidKeywordRestrictionResponse(
            kid=get_kid_response,
            keyword_restrictions=keyword_restrictions_response
        )

    def get_kids_mapped_keyword_restrictions_responses(
        self,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[GetKidKeywordRestrictionResponse], int]:
        total_count, kid_keyword_restrictions = self.get_all_kids_mapped_keyword_restrictions_data(
            sort_by=sort_by,
            order_by=order_by,
            page=page,
            page_size=page_size
        )

        users = get_all_users()

        responses = [
            self.get_kids_mapped_keyword_restrictions_response(kid_keyword_restriction, users)
            for kid_keyword_restriction in kid_keyword_restrictions
        ]

        return total_count, responses
        
    def get_all_kids_mapped_keyword_restrictions(
        self,
        order_by: str,
        sort_by: str,
        page: int | None,   
        page_size: int | None
    ) -> Tuple[List[GetKidKeywordRestrictionResponse], int]:
        return self.get_kids_mapped_keyword_restrictions_responses(
            order_by=order_by,
            sort_by=sort_by,
            page=page,
            page_size=page_size
        )

    def get_mapped_keyword_restriction_for_kid(
        self, 
        restriction_id: int,
        kid_id: int
    ) -> List[GetKeywordRestrictionResponse]:
        kid_keyword_restriction = self.get_kid_keyword_restriction_query(restriction_id, kid_id)
        self.validate_kid_keyword_restriction_exists(kid_keyword_restriction)

        keyword_restriction = self.get_keyword_restrictions_data_by_id(restriction_id)
        self.validate_keyword_restriction_exists(keyword_restriction)

        kid = get_kid_by_id(self.db, kid_id)
        self.validate_kid_exists(kid)

        users = get_all_users()

        return self.get_keyword_restrictions_response(keyword_restriction, users)

    def update_mapped_keyword_restriction_for_kid_by_id(
        self, 
        logged_in_user_id: int, 
        restriction_id: int,
        kid_id: int
    ) -> SuccessMessageResponse:
        kid_keyword_restriction = self.get_kid_keyword_restriction_query(restriction_id, kid_id)
        self.validate_kid_keyword_restriction_exists(kid_keyword_restriction)

        keyword_restriction = self.get_keyword_restrictions_data_by_id(restriction_id)
        self.validate_keyword_restriction_exists(keyword_restriction)

        kid_keyword_restriction.restriction_id = restriction_id
        kid_keyword_restriction.updated_at = datetime.now()
        kid_keyword_restriction.updated_by = logged_in_user_id

    def delete_mapped_keyword_restriction_for_kid_by_id(  
        self, 
        restriction_id: int,
        kid_id: int
    ) -> SuccessMessageResponse:
        kid_keyword_restriction = self.get_kid_keyword_restriction_query(restriction_id, kid_id)
        self.validate_kid_keyword_restriction_exists(kid_keyword_restriction)

        keyword_restriction = self.get_keyword_restrictions_data_by_id(restriction_id)
        self.validate_keyword_restriction_exists(keyword_restriction)

        self.db.delete(kid_keyword_restriction)
        self.db.commit()

        return SuccessMessageResponse(
            id=kid_keyword_restriction.id,
            message=KEYWORD_RESTRICTION_NOT_MAPPED_TO_KID
        )
    