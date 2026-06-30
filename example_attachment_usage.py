"""
Example: How to use the new attachment functionality

This script demonstrates how to:
1. Store emails with attachments
2. Retrieve attachment information
3. Download attachments
4. Delete attachments
"""

import asyncio
import base64
from datetime import datetime, timezone
from services.firebase_service import FirebaseService
from models.schemas import EmailDataSchema, EmailAttachmentSchema

async def example_attachment_usage():
    """Example of using the attachment functionality"""
    
    # Initialize Firebase service
    firebase_service = FirebaseService()
    
    # Create sample attachment data (base64 encoded)
    sample_text = "This is a sample attachment content."
    sample_data = base64.b64encode(sample_text.encode('utf-8')).decode('utf-8')
    
    # Create email with attachment
    email_data = EmailDataSchema(
        subject="Test Email with Attachment",
        from_email="sender@example.com",
        to_email="recipient@example.com",
        body="This email contains an attachment.",
        html_body="<p>This email contains an attachment.</p>",
        attachments=[
            EmailAttachmentSchema(
                filename="sample.txt",
                content_type="text/plain",
                size=len(sample_text),
                data=sample_data
            )
        ],
        received_at=datetime.now(timezone.utc),
        message_id="test-message-123",
        user_token="test-token-123"
    )
    
    print("1. Storing email with attachment...")
    email_id = await firebase_service.store_email(email_data)
    print(f"   Email stored with ID: {email_id}")
    
    print("\n2. Getting email details...")
    email_details = await firebase_service.get_email_by_id(email_id)
    print(f"   Subject: {email_details['subject']}")
    print(f"   Has attachments: {email_details['has_attachments']}")
    print(f"   Attachment count: {email_details['attachment_count']}")
    
    print("\n3. Getting attachment information...")
    attachment_info = await firebase_service.get_attachment_info(email_id, 0)
    if attachment_info:
        print(f"   Filename: {attachment_info['original_filename']}")
        print(f"   Content type: {attachment_info['content_type']}")
        print(f"   Size: {attachment_info['size']} bytes")
        print(f"   File ID: {attachment_info['file_id']}")
        print(f"   Stored at: {attachment_info['stored_at']}")
    
    print("\n4. Downloading attachment...")
    attachment_data = await firebase_service.get_attachment(email_id, 0)
    if attachment_data:
        print(f"   Downloaded filename: {attachment_data['filename']}")
        print(f"   Downloaded size: {attachment_data['size']} bytes")
        print(f"   Content preview: {attachment_data['data'][:50].decode('utf-8')}...")
    
    print("\n5. Generating download URL...")
    download_url = await firebase_service.get_attachment_url(email_id, 0, "http://localhost:8000")
    print(f"   Download URL: {download_url}")
    
    print("\n6. Getting all emails with attachments...")
    emails_with_attachments = await firebase_service.get_emails(
        limit=10,
        filters=EmailFilterSchema(has_attachments=True)
    )
    print(f"   Found {emails_with_attachments['total']} emails with attachments")
    
    print("\n7. Deleting attachment...")
    delete_success = await firebase_service.delete_attachment(email_id, 0)
    print(f"   Attachment deleted: {delete_success}")
    
    print("\n8. Verifying deletion...")
    email_after_delete = await firebase_service.get_email_by_id(email_id)
    print(f"   Has attachments after delete: {email_after_delete['has_attachments']}")
    print(f"   Attachment count after delete: {email_after_delete['attachment_count']}")
    
    print("\n9. Cleaning up - deleting email...")
    email_deleted = await firebase_service.delete_email(email_id)
    print(f"   Email deleted: {email_deleted}")

if __name__ == "__main__":
    print("Attachment Usage Example")
    print("=" * 50)
    asyncio.run(example_attachment_usage())
