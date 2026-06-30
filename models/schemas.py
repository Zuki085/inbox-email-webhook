"""
Pydantic Schemas for Email Webhook

Defines data models for email webhook requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class EmailAttachmentSchema(BaseModel):
    """Schema for email attachments"""
    filename: str = Field(..., description="Name of the attachment file")
    content_type: str = Field(..., description="MIME type of the attachment")
    size: int = Field(..., description="Size of the attachment in bytes")
    data: Optional[str] = Field(None, description="Base64 encoded attachment data")

class FileReferenceSchema(BaseModel):
    """Schema for file references stored in Firebase"""
    file_id: str = Field(..., description="Unique file identifier")
    original_filename: str = Field(..., description="Original filename")
    stored_filename: str = Field(..., description="Stored filename on disk")
    file_path: str = Field(..., description="Full file path")
    relative_path: str = Field(..., description="Relative path from storage root")
    content_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")
    email_id: str = Field(..., description="Associated email ID")
    stored_at: datetime = Field(..., description="When file was stored")
    year: int = Field(..., description="Storage year")
    month: int = Field(..., description="Storage month")

class EmailDataSchema(BaseModel):
    """Schema for incoming email data"""
    subject: str = Field(..., description="Email subject line")
    from_email: EmailStr = Field(..., description="Sender email address")
    to_email: EmailStr = Field(..., description="Recipient email address")
    cc_email: Optional[str] = Field(None, description="CC recipients (comma-separated)")
    bcc_email: Optional[str] = Field(None, description="BCC recipients (comma-separated)")
    body: str = Field(..., description="Plain text email body")
    html_body: Optional[str] = Field(None, description="HTML email body")
    attachments: Optional[List[EmailAttachmentSchema]] = Field(None, description="Email attachments")
    received_at: datetime = Field(..., description="When the email was received")
    message_id: str = Field(..., description="Unique message identifier")
    user_token: Optional[str] = Field(None, description="JWT token for user identification")
    owner_user_id: Optional[str] = Field(None, description="Firestore user ID of the mailbox owner")
    mailbox_email: Optional[str] = Field(None, description="Email address of the mailbox that received this email")
    
    # User and project lookup fields (populated during processing)
    sender_username: Optional[str] = Field(None, description="First name of sender (from users collection)")
    sender_user_id: Optional[str] = Field(None, description="User ID of sender")
    assigned_project: Optional[dict] = Field(None, description="Assigned project object from projects collection")

class WebhookResponseSchema(BaseModel):
    """Schema for webhook response"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    email_id: Optional[str] = Field(None, description="Firebase document ID of stored email")

class EmailListResponseSchema(BaseModel):
    """Schema for email list response"""
    emails: List[dict] = Field(..., description="List of email documents")
    total: int = Field(..., description="Total number of emails")
    limit: int = Field(..., description="Number of emails requested")
    offset: int = Field(0, description="Number of emails skipped")

class UserEmailAccountSchema(BaseModel):
    """Schema for registering a user's email mailbox credentials"""
    email: EmailStr = Field(..., description="User's email address for IMAP polling")
    app_password: str = Field(..., description="App password for the email account")
    email_polling_enabled: bool = Field(True, description="Whether to poll this mailbox")
    email_host: Optional[str] = Field(None, description="Custom IMAP host (auto-detected if omitted)")
    email_port: Optional[int] = Field(None, description="Custom IMAP port")
    email_use_ssl: Optional[bool] = Field(None, description="Use SSL for IMAP connection")

class UserEmailAccountResponseSchema(BaseModel):
    """Response after registering a user email account"""
    success: bool
    message: str
    user_id: str
    email: str
    email_polling_enabled: bool
    imap_config: dict

class UserEmailAccountStatusSchema(BaseModel):
    """Email account status without sensitive credentials"""
    user_id: str
    email: Optional[str] = None
    email_polling_enabled: bool = True
    has_credentials: bool = False
    last_polled_at: Optional[datetime] = None
    last_poll_status: Optional[str] = None
    last_poll_error: Optional[str] = None

class EmailFilterSchema(BaseModel):
    """Schema for email filtering"""
    user_token: Optional[str] = Field(None, description="Filter by user token")
    owner_user_id: Optional[str] = Field(None, description="Filter by mailbox owner user ID")
    mailbox_email: Optional[str] = Field(None, description="Filter by recipient mailbox email")
    from_email: Optional[str] = Field(None, description="Filter by sender email")
    subject_contains: Optional[str] = Field(None, description="Filter by subject containing text")
    has_attachments: Optional[bool] = Field(None, description="Filter by presence of attachments")
    processed: Optional[bool] = Field(None, description="Filter by processing status")
    date_from: Optional[datetime] = Field(None, description="Filter emails from this date")
    date_to: Optional[datetime] = Field(None, description="Filter emails until this date")

class ProcessingStatusSchema(BaseModel):
    """Schema for email processing status"""
    email_id: str = Field(..., description="Email document ID")
    processed: bool = Field(..., description="Whether email was processed")
    processed_at: Optional[datetime] = Field(None, description="When email was processed")
    user_id: Optional[int] = Field(None, description="User ID if processed")
    error: Optional[str] = Field(None, description="Error message if processing failed")
    pdf_processed: Optional[bool] = Field(None, description="Whether PDF was processed")
    extracted_data: Optional[str] = Field(None, description="Extracted data from PDF")
    file_path: Optional[str] = Field(None, description="Path to saved file")

class AttachmentInfoSchema(BaseModel):
    """Schema for attachment information"""
    index: int = Field(..., description="Attachment index")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")
    file_id: str = Field(..., description="Unique file identifier")
    stored_at: datetime = Field(..., description="When file was stored")
    download_url: str = Field(..., description="URL to download the attachment")

class AttachmentListResponseSchema(BaseModel):
    """Schema for attachment list response"""
    attachments: List[AttachmentInfoSchema] = Field(..., description="List of attachments")
    count: int = Field(..., description="Number of attachments")
    email_id: str = Field(..., description="Email document ID")
