from typing import (
    Any, 
    Optional
)
from pydantic import (
    BaseModel, 
    EmailStr
)


class Attachments(BaseModel):
    name: str
    content: str


class EmailRequest(BaseModel):
    template: Optional[str]
    placeholder_values: Optional[dict[str, Any]]
    content: Optional[str]
    to: list[EmailStr]
    cc: list[EmailStr] = []
    bcc: list[EmailStr] = []
    subject: str
    attachments: Optional[list[Attachments]]


class BulkEmailRequest(BaseModel):
    requests: list[EmailRequest]
