from dataclasses import dataclass
import os
from typing import (
    Dict,
    List, 
    Tuple
)
import uuid

from automapper import mapper
from dotenv import load_dotenv
from fastapi import (
    Depends, 
    HTTPException, 
    status
)
import sqlalchemy as sa
from sqlalchemy.orm import Session
from openai import OpenAI

from app.connectors.database_connector import get_db
from app.entities.kid import Kid
from app.entities.question_history import QuestionHistory
from app.models.base_response_models import SuccessMessageResponse
from app.models.kid_models import (
    GetKidResponse,
    GetQuestionsHistoryResponse, 
    KidRequest,
    QuestionRequest
)
from app.utils.constants import (
    KID_CREATED_SUCCESSFULLY, 
    KID_DELETED_SUCCESSFULLY, 
    KID_NOT_FOUND, 
    KID_UPDATED_SUCCESSFULLY,
    QUESTION_ANSWERED_AND_STORED
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
class KidService:
    db: Session = Depends(get_db)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def create_kid(self, logged_in_user_id: int, request: KidRequest) -> SuccessMessageResponse:
        new_kid = Kid(
            parent_id=logged_in_user_id,
            name=request.name,
            age=request.age,
            gender=request.gender,
            school=request.school,
            standard=request.standard,
            created_by=logged_in_user_id,
            updated_by=logged_in_user_id,
        )
        self.db.add(new_kid)
        self.db.commit()

        return SuccessMessageResponse(
            id=new_kid.id,
            message=KID_CREATED_SUCCESSFULLY
        )
    
    def base_get_kid_query(self):
        return self.db.query(Kid)
    
    def get_matched_kid_based_on_search(
        self, 
        query, 
        search: str | None, 
    ):
        if search:
            search_pattern = f"%{search.strip()}%"

            query = query.filter(
                sa.or_(
                    Kid.name.ilike(search_pattern),
                    Kid.gender.ilike(search_pattern),
                    Kid.school.ilike(search_pattern),
                    Kid.standard.ilike(search_pattern)
                )
            )    

        return query 
    
    def get_all_kids_data(
        self,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[Kid], int]:
        query = self.base_get_kid_query()
        
        query = self.get_matched_kid_based_on_search(query, search)
        
        query = apply_filter(
            query=query, 
            main_table=Kid, 
            filter_by=filter_by, 
            filter_values=filter_values
        )

        query = apply_sorting(
            query=query, 
            table=Kid, 
            custom_field_sorting=None, 
            sort_by=sort_by, 
            order_by=order_by
        ) 
    
        total_count = query.count()

        if page and page_size:
            query = apply_pagination(query, page, page_size)

        return total_count, query.all()
    
    def get_kid_response(
        self, 
        kid: Kid, 
        users: Dict[int, str]
    ) -> GetKidResponse:
        return GetKidResponse(
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
    
    def get_kid_responses(
        self,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[GetKidResponse], int]:
        total_count, users_data = self.get_all_kids_data(
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
            self.get_kid_response(user, users)
            for user in users_data
        ]
        
        return total_count, responses
    
    def get_all_kids(
        self,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[GetKidResponse], int]:
        return self.get_kid_responses(
            search=search,
            filter_by=filter_by,
            filter_values=filter_values,
            sort_by=sort_by,
            order_by=order_by,
            page=page, 
            page_size=page_size
        )
    
    def _validate_kid_exist(self, kid: Kid):
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=KID_NOT_FOUND
            )

    def get_kid_by_id(self, kid_id: int) -> GetKidResponse:
        kid = get_kid_by_id(self.db, kid_id)
        self._validate_kid_exist(kid)

        users = get_all_users() 
        
        return self.get_kid_response(kid, users)

    def update_kid_by_id(
        self, 
        logged_in_user_id: int, 
        kid_id: int, 
        request: KidRequest
    ) -> SuccessMessageResponse:
        kid = get_kid_by_id(self.db, kid_id)
        self._validate_kid_exist(kid)

        kid.name = request.name
        kid.age = request.age
        kid.gender = request.gender
        kid.school = request.school
        kid.standard = request.standard
        kid.updated_by = logged_in_user_id
        kid.updated_at = sa.func.now()

        self.db.commit()

        return SuccessMessageResponse(
            id=kid_id,
            message=KID_UPDATED_SUCCESSFULLY
        )
    
    def delete_kid_by_id(self, kid_id: int) -> SuccessMessageResponse:
        kid = get_kid_by_id(self.db, kid_id)
        self._validate_kid_exist(kid)

        self.db.delete(kid)
        self.db.commit()
        
        return SuccessMessageResponse(
            id=kid_id,
            message=KID_DELETED_SUCCESSFULLY
        )

    def create_question(self, kid_id: int, request: QuestionRequest) -> SuccessMessageResponse:
        kid = get_kid_by_id(self.db, kid_id)
        self._validate_kid_exist(kid)

        moderation = self.client.moderations.create(
            model="omni-moderation-latest",
            input=request.question
        )
        if moderation.results[0].flagged:
            new_entry = QuestionHistory(
                id=str(uuid.uuid4()),
                kid_id=kid_id,
                question=request.question,
                answer="This question is not allowed for kids.",
                subject="Restricted Content"
            )
            self.db.add(new_entry)
            self.db.commit()

            return SuccessMessageResponse(
                id=new_entry.id,
                message=QUESTION_ANSWERED_AND_STORED
            )

        category_prompt = f"""
            Categorize the following question into a subject.
            Options: [Maths, Science, Social, General Knowledge, Other].
            Question: "{request.question}"
            Answer with only one word from the options.
        """
        category_resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": category_prompt}]
        )
        subject = category_resp.choices[0].message.content.strip()

        answer_prompt = f"""
            You're a friendly teacher for 12-year-old kids.
            Answer the question below in simple, clear, and safe language.
            Avoid including any violent, sexual, or harmful content. Keep it short.

            Question: {request.question}
        """
        answer_resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": answer_prompt}]
        )
        answer = answer_resp.choices[0].message.content.strip()

        new_entry = QuestionHistory(
            id=str(uuid.uuid4()),
            kid_id=kid_id,
            question=request.question,
            answer=answer,
            subject=subject
        )
        self.db.add(new_entry)
        self.db.commit()

        return SuccessMessageResponse(
            message=QUESTION_ANSWERED_AND_STORED
        )

    def get_kid_questions_history_by_id(self, kid_id: int):
        kid = get_kid_by_id(self.db, kid_id)
        self._validate_kid_exist(kid)

        history = (
            self.db.query(QuestionHistory)
            .filter(QuestionHistory.kid_id == kid_id)
            .order_by(QuestionHistory.created_at.asc())
            .all()
        )

        return [mapper.to(GetQuestionsHistoryResponse).map(h) for h in history]