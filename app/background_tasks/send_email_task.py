import asyncio
import base64
import json
import os
import tempfile
import traceback
import uuid
from typing import (
    Dict, 
    List
)

from fastapi_mail import (
    FastMail, 
    MessageSchema, 
    ConnectionConfig, 
    MessageType
)
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.connectors.database_connector import build_db_session
from app.entities.email_notification import EmailNotification
from app.models.email_models import (
    Attachments,
    BulkEmailRequest, 
    EmailRequest
)
from app.utils.constants import PUBLIC_SCHEMA
from app.utils.enums import EMAIL_TASK_STATUS

MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
MAIL_FROM: str = os.getenv("MAIL_FROM")
MAIL_PORT: int = os.getenv("MAIL_PORT")
MAIL_SERVER: str = os.getenv("MAIL_SERVER")
MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS")
MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS")
USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS")
DISPLAY_SENDER_NAME: str = os.getenv("DISPLAY_SENDER_NAME")


def build_server_config():
    return ConnectionConfig(
        MAIL_USERNAME=MAIL_USERNAME,
        MAIL_PASSWORD=MAIL_PASSWORD,
        MAIL_FROM=MAIL_FROM,
        MAIL_PORT=MAIL_PORT,
        MAIL_SERVER=MAIL_SERVER,
        MAIL_STARTTLS=MAIL_STARTTLS,
        MAIL_SSL_TLS=MAIL_SSL_TLS,
        MAIL_FROM_NAME=DISPLAY_SENDER_NAME,
        USE_CREDENTIALS=USE_CREDENTIALS,
    )  


async def send_email_async(message: MessageSchema):
    fm = FastMail(build_server_config())
    await fm.send_message(message)


def process_attachments(attachments: List[Dict]) -> List[str]:
    """
        Process attachments by saving base64 content to temporary files
        and returning a list of file paths. The file name will match the attachment name.
    """
    temp_files = []

    for att in attachments:
        try:
            file_bytes = base64.b64decode(att.get("content"))
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, att.get("name"))
            
            with open(temp_path, 'wb') as temp_file:
                temp_file.write(file_bytes)
            
            temp_files.append(temp_path)
            
        except Exception as e:
            pass
            
    return temp_files


async def send_email_task(request_json: str, task_id: str):
    request = json.loads(request_json)
    temp_files = []
    
    try:
        attachments = []
        if request.get('attachments'):
            attachments = process_attachments(request.get('attachments', []))
            temp_files = attachments 
        
        message = MessageSchema(
            recipients=request['to'],
            cc=request.get('cc', []),
            bcc=request.get('bcc', []),
            subtype=MessageType.html,
            subject=request.get('subject'),
            template_body=request.get('placeholder_values', {}),
            attachments=attachments  
        )

        if request.get('content'):
            message.body = request.get('content')
            
        await send_email_async(message)

        update_email_status(task_id, is_success=True, fail_reason="")

    except Exception as e:
        update_email_status(task_id, is_success=False, fail_reason=traceback.format_exc())
        raise Exception(str(e))
    finally:
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                pass


def update_email_status(task_id: str, is_success: bool, fail_reason: str):
    db: Session = build_db_session(schema=PUBLIC_SCHEMA)

    try:
        email_notification = db.get(EmailNotification, task_id)

        if not email_notification:
            raise Exception("Email notification database object not found")
        
        if is_success:
            email_notification.status = EMAIL_TASK_STATUS.SENT
            email_notification.is_sent_successfully = True
            email_notification.fail_reason = ""
            email_notification.updated_at = func.now()  
        else:
            email_notification.status = EMAIL_TASK_STATUS.FAILED
            email_notification.updated_at = func.now()  
            email_notification.is_sent_successfully = False
            email_notification.fail_reason = fail_reason
    except:
        pass
    finally:
        db.commit()
        db.close()


def create_attachments_dicts(attachments: List[Attachments]) -> List[Dict]:
    return [
            {"name": attachment.name, "content": attachment.content}
            for attachment in (attachments or [])
        ]


def create_email_notification_entity(
    db: Session, 
    request: EmailRequest, 
    email_content: str
) -> EmailNotification:
    attachments_dicts = create_attachments_dicts(request.attachments) 

    email_notification = EmailNotification()
    email_notification.id = str(uuid.uuid4())
    email_notification.attachments = attachments_dicts
    email_notification.cc = request.cc
    email_notification.bcc = request.bcc
    email_notification.recipients = request.to
    email_notification.payload = request.placeholder_values or {}
    email_notification.subject = request.subject
    email_notification.template_identifier = request.template
    email_notification.content = email_content
    email_notification.status = EMAIL_TASK_STATUS.SENDING
    
    db.add(email_notification)
    db.commit()
    
    return email_notification


async def send_bulk_mails(bulk_email_request: BulkEmailRequest):
    db: Session = build_db_session(PUBLIC_SCHEMA)
    print("Start")
    try:
        task_data = []
        notifiation_list = []

        for request in bulk_email_request.requests:
            email_notification = create_email_notification_entity(
                db=db,
                request=request,
                email_content=request.content
            )
            task_data.append(
                {
                    "task_id": email_notification.id,
                    "request_json": request.model_dump_json()
                }
            )

            notifiation_list.append(email_notification)

        db.bulk_save_objects(notifiation_list)
        db.commit()

        for task in task_data:
            await send_email_task(
                request_json=task["request_json"],
                task_id=task["task_id"]
            )
    except Exception as e:       
        raise Exception(str(e))
    finally:
        db.close()   