"""
User Email Account Routes

Endpoints for registering user mailboxes and fetching user-scoped emails.
"""

from fastapi import APIRouter, HTTPException, status, Path, Query
from typing import Optional
import logging

from models.schemas import (
    UserEmailAccountSchema,
    UserEmailAccountResponseSchema,
    UserEmailAccountStatusSchema,
    EmailListResponseSchema,
    EmailFilterSchema,
)
from services.user_email_service import UserEmailService
from services.firebase_service import FirebaseService
from services.email_poller import email_poller

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook/users", tags=["User Email Accounts"])

user_email_service = UserEmailService()
firebase_service = FirebaseService()


@router.post("/{user_id}/email-account", response_model=UserEmailAccountResponseSchema)
async def register_user_email_account(
    user_id: str = Path(..., description="Firestore user document ID"),
    account: UserEmailAccountSchema = ...,
):
    """
    Register or update email credentials for a user.

    Call this when a user creates an account or connects their mailbox.
    The user's Firestore document will be updated with email and app_password.
    """
    try:
        result = await user_email_service.register_email_account(
            user_id=user_id,
            email=account.email,
            app_password=account.app_password,
            email_polling_enabled=account.email_polling_enabled,
            email_host=account.email_host,
            email_port=account.email_port,
            email_use_ssl=account.email_use_ssl,
        )
        return UserEmailAccountResponseSchema(
            success=True,
            message="Email account registered successfully",
            user_id=result["user_id"],
            email=result["email"],
            email_polling_enabled=result["email_polling_enabled"],
            imap_config=result["imap_config"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering email account for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering email account: {str(e)}",
        )


@router.get("/{user_id}/email-account", response_model=UserEmailAccountStatusSchema)
async def get_user_email_account_status(
    user_id: str = Path(..., description="Firestore user document ID"),
):
    """Get email account status for a user (password is never returned)."""
    status_data = await user_email_service.get_email_account_status(user_id)
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserEmailAccountStatusSchema(**status_data)


@router.get("/{user_id}/emails", response_model=EmailListResponseSchema)
async def get_user_emails(
    user_id: str = Path(..., description="Firestore user document ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    from_email: Optional[str] = Query(None),
    has_attachments: Optional[bool] = Query(None),
    processed: Optional[bool] = Query(None),
):
    """Retrieve emails received in a specific user's mailbox."""
    try:
        filters = EmailFilterSchema(
            owner_user_id=user_id,
            from_email=from_email,
            has_attachments=has_attachments,
            processed=processed,
        )
        result = await firebase_service.get_emails(
            limit=limit,
            offset=offset,
            filters=filters,
        )
        return EmailListResponseSchema(
            emails=result["emails"],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user emails: {str(e)}",
        )


@router.post("/{user_id}/poll")
async def poll_user_mailbox(
    user_id: str = Path(..., description="Firestore user document ID"),
):
    """Manually trigger email polling for a single user's mailbox."""
    try:
        account = await user_email_service.get_account_by_user_id(user_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User email account not configured",
            )
        await email_poller.poll_mailbox(account)
        return {
            "success": True,
            "message": f"Polling completed for {account['email']}",
            "user_id": user_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error polling user mailbox: {str(e)}",
        )
