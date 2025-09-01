from dataclasses import dataclass
import os
from typing import (
    Dict,
    List, 
    Tuple
)

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

from app.background_tasks.send_email_task import send_bulk_mails
from app.connectors.database_connector import get_db
from app.entities.chat import Chat
from app.entities.kid import Kid
from app.entities.chat_conversation import ChatConversation
from app.models.base_response_models import SuccessMessageResponse
from app.models.kid_models import (
    ChatRequest,
    GetChatResponse,
    GetKidResponse,
    GetChatConversationResponse, 
    KidRequest,
    QuestionRequest
)
from app.utils.constants import (
    CHAT_CREATED_SUCCESSFULLY,
    CHAT_DELETED_SUCCESSFULLY,
    CHAT_NOT_FOUND,
    CHAT_UPDATED_SUCCESSFULLY,
    KID_CREATED_SUCCESSFULLY, 
    KID_DELETED_SUCCESSFULLY, 
    KID_NOT_FOUND, 
    KID_UPDATED_SUCCESSFULLY,
    QUESTION_ANSWERED_AND_STORED
)
from app.utils.db_queries import (
    get_chat_by_id, 
    get_chat_by_kid_and_chat_id,
    get_kid_by_id,
    get_kid_keyword_restriction_by_id
)
from app.utils.email_utils import (
    create_bulk_email_request, 
    create_mail_content_for_restricted_question_asked_by_kid
)
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
    
    def base_get_kid_query(self, parent_id: int):
        return self.db.query(Kid).filter(Kid.is_active == True, Kid.parent_id == parent_id)
    
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
        parent_id: int,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[Kid], int]:
        query = self.base_get_kid_query(parent_id)
        
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
            name=kid.name.title(),  
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
        parent_id: int,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[GetKidResponse], int]:
        total_count, users_data = self.get_all_kids_data(
            parent_id=parent_id,
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
        parent_id: int,
        search: str | None,
        filter_by: str | None,
        filter_values: str | None,
        sort_by: str,
        order_by: str,
        page: int | None,
        page_size: int | None
    ) -> Tuple[List[GetKidResponse], int]:
        return self.get_kid_responses(
            parent_id=parent_id,
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

        kid.is_active = False
        self.db.commit()
        
        return SuccessMessageResponse(
            id=kid_id,
            message=KID_DELETED_SUCCESSFULLY
        )
    
    def create_kid_chat(self, kid_id: int, request: ChatRequest) -> SuccessMessageResponse:
        new_chat = Chat(
            kid_id=kid_id,
            title=request.title
        )
        self.db.add(new_chat)
        self.db.commit()

        return SuccessMessageResponse(
            id=new_chat.id,
            message=CHAT_CREATED_SUCCESSFULLY
        )

    def get_all_kid_chats(self, kid_id: int) -> list[GetChatResponse]:
        chats = (
            self.db.query(Chat)
            .filter(Chat.kid_id == kid_id)
            .order_by(Chat.created_at.desc())
            .all()
        )
        return [
            GetChatResponse(
                id=chat.id,
                title=chat.title,
                created_at=chat.created_at
            )
            for chat in chats
        ]

    def update_kid_chat(self, kid_id: int, chat_id: int, request: ChatRequest) -> SuccessMessageResponse:
        chat = get_chat_by_kid_and_chat_id(self.db, kid_id, chat_id)
        self._validate_chat_exist(chat)

        chat.title = request.title
        self.db.commit()

        return SuccessMessageResponse(
            id=chat_id,
            message=CHAT_UPDATED_SUCCESSFULLY
        )

    def delete_kid_chat(self, kid_id: int, chat_id: int) -> SuccessMessageResponse:
        chat = get_chat_by_kid_and_chat_id(self.db, kid_id, chat_id)
        self._validate_chat_exist(chat)
        
        self.db.query(ChatConversation).filter(ChatConversation.chat_id == chat_id).delete()

        self.db.delete(chat)
        self.db.commit()

        return SuccessMessageResponse(
            id=chat_id,
            message=CHAT_DELETED_SUCCESSFULLY
        )

    def _validate_chat_exist(self, chat: Chat):
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CHAT_NOT_FOUND
            )   

    async def _notify_parent_of_restricted_question(
        self, parent_email: str, kid_name: str, question: str, keywords: list[str] | None = None
    ) -> None:
        """Send email alert to parent when restricted/flagged question is asked."""
        subject = f"Alert: Restricted Question Asked by {kid_name}"
        keywords_str = ", ".join(keywords) if keywords else "Indirectly flagged content"
        
        email_content = create_mail_content_for_restricted_question_asked_by_kid(
            kid_name=kid_name,
            keywords_str=keywords_str,
            question=question
        )
        
        bulk_email_request = create_bulk_email_request(
            template_id=None,
            placeholder_values={},
            content=email_content,
            subject=subject,
            recipients=[parent_email]
        )
        await send_bulk_mails(bulk_email_request)

    async def create_chat_conversation(
        self,
        chat_id: int,
        request: QuestionRequest,
        logged_in_user_email: str
    ) -> SuccessMessageResponse:
        """
        Creates a chat conversation for a given chat, processes the question for moderation and restriction,
        generates an answer using OpenAI, notifies the parent if the question is restricted, and stores the conversation.
        """
        chat = get_chat_by_id(self.db, chat_id)
        self._validate_chat_exist(chat)
        kid = get_kid_by_id(self.db, chat.kid_id)
        keywords_restriction = get_kid_keyword_restriction_by_id(self.db, chat.kid_id) or []

        # --- Step 1: Moderation + Restriction Check ---
        model_fall_back_message = "I cannot provide you any data on this topic as it is not suitable for children."
        moderation = self.client.moderations.create(
            model="omni-moderation-latest",
            input=request.question
        )
        is_moderation_flagged = moderation.results[0].flagged

        triggered_keywords = []
        is_restricted = False
        if keywords_restriction:
            triggered_keywords = [kw for kw in keywords_restriction.keywords if kw.lower() in request.question.lower()]
            
        is_restricted = is_moderation_flagged or bool(triggered_keywords)

        if is_restricted:
            safe_message = model_fall_back_message
            
            new_entry = ChatConversation(
                chat_id=chat_id,
                question=request.question,
                answer=safe_message,
                subject="Restricted Content"
            )
            self.db.add(new_entry)
            self.db.commit()

            # Always notify parent if restricted (direct or indirect)
            await self._notify_parent_of_restricted_question(
                parent_email=logged_in_user_email,
                kid_name=kid.name,
                question=request.question,
                keywords=triggered_keywords if triggered_keywords else None
            )

            return SuccessMessageResponse(id=new_entry.id, message=QUESTION_ANSWERED_AND_STORED)

        # --- Step 2: Categorization ---
        category_prompt = (
            f"Categorize this question into one of the subjects: "
            f"[Maths, Science, Social, General Knowledge, Other]. "
            f"Question: \"{request.question}\". "
            f"Respond with only one word from the options."
        )
        subject = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": category_prompt}]
        ).choices[0].message.content.strip()

        # Prepare keywords string separated by commas for prompt
        keywords_str = ""
        if keywords_restriction:
            keywords_str = ", ".join(keywords_restriction.keywords).lower() if keywords_restriction.keywords else ""

        # --- Step 3: Answer Generation ---
        kid_age_group = keywords_restriction.title if keywords_restriction else ""
        answer_prompt = (
            f"You are a friendly teacher answering for {kid_age_group} age people.\n\n"
            "Rules:\n"
            "- If the question is unsafe, harmful, or inappropriate for kids, "
            "reply ONLY with:\n"
            f"\"{model_fall_back_message}\"\n"
            "- If the question is directly or indirectly related to any of these restricted keywords, "
            "reply ONLY with the fallback message above.\n"
            f"- The restricted keywords are:\n{keywords_str}\n"
            "- Otherwise, answer simply and clearly in short language.\n"
            f"- Avoid content related to the restricted keywords.\n\n"
            f"Question: {request.question}"
        )

        answer = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": answer_prompt}]
        ).choices[0].message.content.strip()

        # If the generated answer is the restricted safe message, notify parent
        if answer == model_fall_back_message:
            await self._notify_parent_of_restricted_question(
                parent_email=logged_in_user_email,
                kid_name=kid.name,
                question=request.question,
                keywords=None
            )

        # --- Step 4: Save & Commit ---
        new_entry = ChatConversation(
            chat_id=chat_id,
            question=request.question,
            answer=answer,
            subject=subject
        )
        self.db.add(new_entry)
        self.db.commit()

        return SuccessMessageResponse(
            id=new_entry.id, 
            message=QUESTION_ANSWERED_AND_STORED
        )

    def get_chat_conversation_by_id(self, chat_id: int):
        chat = get_chat_by_id(self.db, chat_id)
        self._validate_chat_exist(chat)

        history = (
            self.db.query(ChatConversation)
            .filter(ChatConversation.chat_id == chat_id)
            .order_by(ChatConversation.created_at.asc())
            .all()
        )

        return [mapper.to(GetChatConversationResponse).map(h) for h in history]