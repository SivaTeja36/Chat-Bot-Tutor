import os
from typing import (
    Any, 
    List
)

from dotenv import load_dotenv
from urllib.parse import quote

from app.models.email_models import (
    Attachments,
    BulkEmailRequest, 
    EmailRequest
)

load_dotenv()

SET_PASSWORD_URL: str = os.getenv("SET_PASSWORD_URL")

def create_user_verification_email(url: str) -> str:
    """
        Create the HTML content for the user verification email.
    """
    return f"""
        <!DOCTYPE html>
        <html>
        <body>
            <div>
                <h1>Verify Your Email Address</h1>
                <p>Hi,</p>
                <p>Thank you for registering. Please click the link below to verify your email address:</p>
                <p>
                    <a href="{url}">Verify Email</a>
                </p>
                <p>If you did not request this, please ignore this email.</p>
                <p>Thank you,<br>Your Company</p>
            </div>
        </body>
        </html>
    """

def create_mail_content_for_set_password(email: str, invitation_token: str) -> str:
    """
        Create the HTML content for the password reset email.
    """
    encoded_email = quote(email)
    encoded_invitation_token = quote(invitation_token)
    redirect_link = f"{SET_PASSWORD_URL}?email={encoded_email}&token={encoded_invitation_token}"

    return f"""
        <!DOCTYPE html>
        <html>
        <body>
            <div>
                <h1>Set Your Password</h1>
                <p>Hi User,</p>
                <p>An account has been created for you in our application by the administrator. Please click the link below to set your password and activate your account:</p>
                <p>
                    <a href={redirect_link}>Set Password</a>
                </p>
                <p>If you did not expect this email, please contact the administrator for assistance.</p>
                <>Thank you,<br>Camin Cargo</p>
            </div>
        </body>
        </html>
    """

def create_mail_content_for_restricted_question_asked_by_kid(kid_name: str, keywords_str: str, question: str) -> str:
    """
        Create the HTML content for notifying parents about a restricted question asked by their child.
    """
    return f"""
        <!DOCTYPE html>
        <html>
        <body>
            <div>
                <h2>Restricted Question Alert</h2>
                <p>Dear Parent,</p>
                <p>
                    This is to inform you that your child <strong>{kid_name}</strong> has asked a question containing restricted keywords (<strong>{keywords_str}</strong>):
                </p>
                <blockquote>
                    <strong>Question:</strong> "{question}"
                </blockquote>
                <p>
                    Please review and discuss this with your child if needed.
                </p>
                <p>
                    Regards,<br>
                    ChatTutor Safety Team
                </p>
            </div>
        </body>
        </html>
    """

def get_bulk_email_request_body(
    template_id: str, 
    placeholder_values: dict[str, Any], 
    content: str,
    subject: str, 
    recipients: List[str],
    cc: list[str] = [],
    bcc: list[str] = [], 
    attachments: list[dict] = []
) -> BulkEmailRequest:
    """
        Construct the email request body for sending bulk emails.
    """
    requests = []
    attachments = [
        Attachments(name=attachment["name"], content=attachment["content"]) 
        for attachment in attachments
    ]

    for recipient in recipients:
        requests.append(
            EmailRequest(
                template=template_id,
                placeholder_values=placeholder_values,
                content=content,
                to=[recipient],
                cc=cc,
                bcc=bcc,
                subject=subject,
                attachments=attachments
            )
        )

    return BulkEmailRequest(requests=requests)

def create_bulk_email_request(
    template_id: None,
    placeholder_values: dict[str, Any],
    subject: str, 
    content: str, 
    recipients: List[str],
    attachments: list[dict] = []
) -> None:
    """
        Send bulk emails to users.
    """
    return get_bulk_email_request_body(
        template_id=template_id, 
        placeholder_values=placeholder_values, 
        content=content,
        subject=subject, 
        recipients=recipients,
        attachments=attachments
    )