"""
Email Webhook Routes

FastAPI routes for handling email webhook requests.
"""

from fastapi import APIRouter, HTTPException, status, Query, Path, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import datetime
import logging
import io

# Set up logging
logger = logging.getLogger(__name__)

from models.schemas import (
    EmailDataSchema, 
    WebhookResponseSchema, 
    EmailListResponseSchema,
    EmailFilterSchema,
    ProcessingStatusSchema
)
from services.firebase_service import FirebaseService
from services.email_processor import EmailProcessor
from services.email_poller import email_poller
from services.email_config import email_config

router = APIRouter(prefix="/webhook", tags=["Email Webhook"])

# Initialize services
firebase_service = FirebaseService()
email_processor = EmailProcessor()

@router.post("/email", response_model=WebhookResponseSchema)
async def receive_email_webhook(email_data: EmailDataSchema):
    """
    Webhook endpoint to receive email data and store it in Firebase
    
    This endpoint can be used to manually send email data to the webhook system.
    For automatic email polling, the system polls Gmail every 60 seconds.
    
    Args:
        email_data: Email data to store
        
    Returns:
        WebhookResponseSchema: Response with success status and email ID
    """
    try:
        # Log the incoming email
        logger.info(f"Received email webhook: {email_data.subject} from {email_data.from_email}")
        
        # Store email in Firebase
        email_id = await firebase_service.store_email(email_data)
        
        # If there's a user token, process the email
        if email_data.user_token:
            await email_processor.process_email_with_user_token(email_data, email_id)
        
        logger.info(f"Email stored successfully with ID: {email_id}")
        
        return WebhookResponseSchema(
            success=True,
            message="Email data stored successfully",
            email_id=email_id
        )
        
    except Exception as e:
        logger.error(f"Error storing email data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing email data: {str(e)}"
        )

@router.get("/emails", response_model=EmailListResponseSchema)
async def get_emails(
    limit: int = Query(10, ge=1, le=100, description="Number of emails to retrieve"),
    offset: int = Query(0, ge=0, description="Number of emails to skip"),
    user_token: Optional[str] = Query(None, description="Filter by user token"),
    owner_user_id: Optional[str] = Query(None, description="Filter by mailbox owner user ID"),
    mailbox_email: Optional[str] = Query(None, description="Filter by recipient mailbox email"),
    from_email: Optional[str] = Query(None, description="Filter by sender email"),
    has_attachments: Optional[bool] = Query(None, description="Filter by presence of attachments"),
    processed: Optional[bool] = Query(None, description="Filter by processing status")
):
    """
    Retrieve stored emails with optional filtering
    
    Args:
        limit: Number of emails to retrieve (1-100)
        offset: Number of emails to skip
        user_token: Filter by user token
        from_email: Filter by sender email
        has_attachments: Filter by presence of attachments
        processed: Filter by processing status
        
    Returns:
        EmailListResponseSchema: List of emails with metadata
    """
    try:
        # Create filter object
        filters = EmailFilterSchema(
            user_token=user_token,
            owner_user_id=owner_user_id,
            mailbox_email=mailbox_email,
            from_email=from_email,
            has_attachments=has_attachments,
            processed=processed
        )
        
        result = await firebase_service.get_emails(
            limit=limit,
            offset=offset,
            filters=filters
        )
        
        return EmailListResponseSchema(
            emails=result['emails'],
            total=result['total'],
            limit=result['limit'],
            offset=result['offset']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving emails: {str(e)}"
        )

@router.get("/emails/{email_id}")
async def get_email_by_id(
    email_id: str = Path(..., description="Email document ID")
):
    """
    Retrieve a specific email by ID
    
    Args:
        email_id: Firebase document ID
        
    Returns:
        Dict containing email data
    """
    try:
        email_data = await firebase_service.get_email_by_id(email_id)
        return email_data
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving email: {str(e)}"
        )

@router.get("/emails/{email_id}/status", response_model=ProcessingStatusSchema)
async def get_email_processing_status(
    email_id: str = Path(..., description="Email document ID")
):
    """
    Get processing status for an email
    
    Args:
        email_id: Firebase document ID
        
    Returns:
        ProcessingStatusSchema: Processing status information
    """
    try:
        status_data = await email_processor.get_processing_status(email_id)
        
        if not status_data['success']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=status_data['error']
            )
        
        return ProcessingStatusSchema(
            email_id=email_id,
            processed=status_data['processed'],
            processed_at=status_data['processed_at'],
            user_id=status_data['user_id'],
            error=status_data['error'],
            pdf_processed=status_data['pdf_processed'],
            extracted_data=status_data['extracted_data'],
            file_path=status_data['file_path']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving processing status: {str(e)}"
        )

@router.post("/emails/{email_id}/process")
async def reprocess_email(
    email_id: str = Path(..., description="Email document ID")
):
    """
    Reprocess an email (useful for failed processing)
    
    Args:
        email_id: Firebase document ID
        
    Returns:
        Dict containing processing results
    """
    try:
        # Get email data
        email_data_dict = await firebase_service.get_email_by_id(email_id)
        
        # Convert to schema
        email_data = EmailDataSchema(**email_data_dict)
        
        # Process the email
        result = await email_processor.process_email_with_user_token(email_data, email_id)
        
        return {
            'success': result['success'],
            'message': 'Email reprocessed successfully' if result['success'] else 'Email reprocessing failed',
            'result': result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reprocessing email: {str(e)}"
        )

@router.delete("/emails/{email_id}")
async def delete_email(
    email_id: str = Path(..., description="Email document ID")
):
    """
    Delete an email document
    
    Args:
        email_id: Firebase document ID
        
    Returns:
        Dict containing deletion result
    """
    try:
        success = await firebase_service.delete_email(email_id)
        
        if success:
            return {
                'success': True,
                'message': 'Email deleted successfully'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete email"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting email: {str(e)}"
        )

@router.get("/search")
async def search_emails(
    q: str = Query(..., description="Search term"),
    fields: Optional[List[str]] = Query(None, description="Fields to search in"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    owner_user_id: Optional[str] = Query(None, description="Filter by mailbox owner user ID"),
):
    """
    Search emails by text content
    
    Args:
        q: Search term
        fields: Fields to search in (default: subject, body)
        limit: Maximum number of results
        
    Returns:
        Dict containing search results
    """
    try:
        result = await firebase_service.search_emails(
            search_term=q,
            search_fields=fields,
            limit=limit,
            owner_user_id=owner_user_id,
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching emails: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the webhook service
    
    Returns:
        Dict containing health status
    """
    try:
        # Test Firebase connection
        await firebase_service.get_emails(limit=1)
        
        # Test email configuration
        email_config_status = 'configured' if email_config.validate_config() else 'not_configured'
        email_polling_status = 'enabled' if email_poller.poll_enabled else 'disabled'
        active_accounts = await email_poller.get_active_account_count()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'firebase': 'connected',
                'email_processor': 'ready',
                'email_config': email_config_status,
                'email_polling': email_polling_status,
                'active_mailboxes': active_accounts,
            }
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'services': {
                'firebase': 'disconnected',
                'email_processor': 'error',
                'email_config': 'error',
                'email_polling': 'error'
            }
        }

@router.post("/email/poll")
async def trigger_email_poll():
    """
    Manually trigger email polling
    
    Returns:
        Dict containing polling results
    """
    try:
        await email_poller.poll_emails()
        return {
            'success': True,
            'message': 'Email polling completed successfully'
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during email polling: {str(e)}"
        )

@router.get("/email/config")
async def get_email_config():
    """
    Get current email configuration
    
    Returns:
        Dict containing email configuration
    """
    try:
        active_accounts = await email_poller.get_active_account_count()
        return {
            'mode': 'multi_user' if active_accounts > 0 else 'legacy',
            'active_mailboxes': active_accounts,
            'provider': email_config.provider.value,
            'imap_config': email_config.get_imap_config(),
            'smtp_config': email_config.get_smtp_config(),
            'connection_string': email_config.get_connection_string(),
            'configured': email_config.validate_config() or active_accounts > 0,
            'polling_enabled': email_poller.poll_enabled,
            'poll_interval': email_poller.poll_interval
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting email configuration: {str(e)}"
        )

# Attachment endpoints
@router.get("/emails/{email_id}/attachments")
async def get_email_attachments(
    email_id: str = Path(..., description="Email document ID")
):
    """
    Get list of attachments for an email
    
    Args:
        email_id: Email document ID
        
    Returns:
        List of attachment information
    """
    try:
        email_data = await firebase_service.get_email_by_id(email_id)
        
        if not email_data.get('attachments'):
            return {
                'attachments': [],
                'count': 0,
                'message': 'No attachments found'
            }
        
        # Get attachment info for each attachment
        attachment_info = []
        for i, attachment_ref in enumerate(email_data['attachments']):
            info = await firebase_service.get_attachment_info(email_id, i)
            if info:
                attachment_info.append({
                    'index': i,
                    'filename': info['original_filename'],
                    'content_type': info['content_type'],
                    'size': info['size'],
                    'file_id': info['file_id'],
                    'stored_at': info['stored_at'],
                    'download_url': f"/webhook/emails/{email_id}/attachments/{i}/download"
                })
        
        return {
            'attachments': attachment_info,
            'count': len(attachment_info),
            'email_id': email_id
        }
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving attachments: {str(e)}"
        )

@router.get("/emails/{email_id}/attachments/{attachment_index}/download")
async def download_attachment(
    email_id: str = Path(..., description="Email document ID"),
    attachment_index: int = Path(..., ge=0, description="Attachment index (0-based)")
):
    """
    Download a specific attachment
    
    Args:
        email_id: Email document ID
        attachment_index: Index of attachment to download
        
    Returns:
        File download response
    """
    try:
        # Get attachment data
        attachment_data = await firebase_service.get_attachment(email_id, attachment_index)
        
        if not attachment_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        # Create file-like object
        file_obj = io.BytesIO(attachment_data['data'])
        
        # Return streaming response
        return StreamingResponse(
            io.BytesIO(attachment_data['data']),
            media_type=attachment_data['content_type'],
            headers={
                "Content-Disposition": f"attachment; filename={attachment_data['filename']}",
                "Content-Length": str(attachment_data['size'])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading attachment: {str(e)}"
        )

@router.get("/emails/{email_id}/attachments/{attachment_index}/view")
async def view_attachment_inline(
    email_id: str = Path(..., description="Email document ID"),
    attachment_index: int = Path(..., ge=0, description="Attachment index (0-based)")
):
    """
    View attachment inline in browser (for images, PDFs, etc.)
    
    Args:
        email_id: Email document ID
        attachment_index: Index of attachment
        
    Returns:
        File content for inline viewing
    """
    try:
        # Get attachment data
        attachment_data = await firebase_service.get_attachment_data(email_id, attachment_index)
        
        if not attachment_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        # Return file for inline viewing (no download prompt)
        return StreamingResponse(
            io.BytesIO(attachment_data['data']),
            media_type=attachment_data['content_type'],
            headers={
                "Content-Disposition": f"inline; filename={attachment_data['filename']}",
                "Content-Length": str(attachment_data['size'])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error viewing attachment: {str(e)}"
        )

@router.get("/emails/{email_id}/attachments/urls")
async def get_attachment_urls(
    email_id: str = Path(..., description="Email document ID")
):
    """
    Get direct URLs for all attachments of an email
    
    Args:
        email_id: Email document ID
        
    Returns:
        List of attachment URLs that can be opened directly in browser
    """
    try:
        attachment_urls = await firebase_service.get_attachment_urls(email_id)
        
        return {
            'email_id': email_id,
            'attachment_urls': attachment_urls,
            'count': len(attachment_urls)
        }
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving attachment URLs: {str(e)}"
        )

@router.get("/emails/{email_id}/attachments/{attachment_index}/info")
async def get_attachment_info(
    email_id: str = Path(..., description="Email document ID"),
    attachment_index: int = Path(..., ge=0, description="Attachment index (0-based)")
):
    """
    Get information about a specific attachment without downloading
    
    Args:
        email_id: Email document ID
        attachment_index: Index of attachment
        
    Returns:
        Attachment information
    """
    try:
        info = await firebase_service.get_attachment_info(email_id, attachment_index)
        
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        return {
            'email_id': email_id,
            'attachment_index': attachment_index,
            'filename': info['original_filename'],
            'content_type': info['content_type'],
            'size': info['size'],
            'file_id': info['file_id'],
            'stored_at': info['stored_at'],
            'last_modified': info['last_modified'],
            'exists': info['exists'],
            'download_url': f"/webhook/emails/{email_id}/attachments/{attachment_index}/download"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting attachment info: {str(e)}"
        )

@router.delete("/emails/{email_id}/attachments/{attachment_index}")
async def delete_attachment(
    email_id: str = Path(..., description="Email document ID"),
    attachment_index: int = Path(..., ge=0, description="Attachment index (0-based)")
):
    """
    Delete a specific attachment
    
    Args:
        email_id: Email document ID
        attachment_index: Index of attachment to delete
        
    Returns:
        Deletion result
    """
    try:
        success = await firebase_service.delete_attachment(email_id, attachment_index)
        
        if success:
            return {
                'success': True,
                'message': f'Attachment {attachment_index} deleted successfully',
                'email_id': email_id,
                'attachment_index': attachment_index
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete attachment"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting attachment: {str(e)}"
        )
