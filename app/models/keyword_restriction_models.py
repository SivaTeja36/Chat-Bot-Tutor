from datetime import datetime
from typing import List

from pydantic import (
    BaseModel
)

from app.models.kid_models import GetKidResponse

class KeywordRestrictionRequest(BaseModel):
    title: str 
    keywords: List[str] 


class GetKeywordRestrictionResponse(BaseModel):
    id: int 
    title: str 
    keywords: List[str] 
    created_at: datetime 
    created_by: str
    updated_at: datetime 
    updated_by: str


class KidKeywordRestrictionRequest(BaseModel):
    kid_id: int 
    restriction_id: int


class GetKidKeywordRestrictionResponse(BaseModel):
    kid: GetKidResponse
    keyword_restrictions: GetKeywordRestrictionResponse