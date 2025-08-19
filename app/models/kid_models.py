from datetime import datetime

from pydantic import (
    BaseModel
)

class KidRequest(BaseModel):
    name: str 
    age: float
    gender: str 
    school: str  
    standard: str   


class GetKidResponse(BaseModel):
    id: int 
    name: str  
    age: float 
    gender: str  
    school: str 
    standard: str 
    created_at: datetime 
    created_by: str
    updated_at: datetime 
    updated_by: str 


class ChatRequest(BaseModel):
    title: str

class GetChatResponse(BaseModel):
    id: int 
    title: str
    created_at: datetime


class QuestionRequest(BaseModel):
    question: str


class GetChatConversationResponse(BaseModel):
    id: str
    question: str 
    answer: str 
    subject: str 
    created_at: datetime 