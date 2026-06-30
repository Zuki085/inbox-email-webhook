#!/usr/bin/env python3
"""
Migration script to add direct URLs to existing emails in Firebase

This script updates existing email documents to include direct URLs for attachments.
"""

import asyncio
from services.firebase_service import FirebaseService

async def migrate_emails_to_direct_urls(base_url: str = "http://localhost:8000"):
    """
    Migrate existing emails to include direct URLs for attachments
    
    Args:
        base_url: Base URL for generating attachment URLs
    """
    firebase_service = FirebaseService()
    
    try:
        print("Starting migration to add direct URLs...")
        
        # Get all emails with attachments
        result = await firebase_service.get_emails(limit=1000)  # Adjust limit as needed
        
        emails_to_update = []
        for email in result['emails']:
            if email.get('has_attachments', False) and not email.get('attachment_urls'):
                emails_to_update.append(email)
        
        print(f"Found {len(emails_to_update)} emails with attachments that need URL migration")
        
        if not emails_to_update:
            print("No emails need migration. All emails already have direct URLs.")
            return
        
        # Update each email
        updated_count = 0
        for email in emails_to_update:
            try:
                email_id = email['id']
                attachments = email.get('attachments', [])
                
                if not attachments:
                    continue
                
                # Generate attachment URLs
                attachment_urls = []
                for i, attachment in enumerate(attachments):
                    attachment_url = {
                        'filename': attachment['filename'],
                        'content_type': attachment['content_type'],
                        'size': attachment['size'],
                        'url': f"{base_url}/webhook/emails/{email_id}/attachments/{i}/download",
                        'attachment_index': i,
                        'view_url': f"{base_url}/webhook/emails/{email_id}/attachments/{i}/view"
                    }
                    attachment_urls.append(attachment_url)
                
                # Update the email document
                update_data = {
                    'attachment_urls': attachment_urls,
                    'updated_at': firebase_service.db.SERVER_TIMESTAMP
                }
                
                await firebase_service.update_email_status(email_id, update_data)
                updated_count += 1
                
                print(f"✅ Updated email {email_id} with {len(attachment_urls)} attachment URLs")
                
            except Exception as e:
                print(f"❌ Error updating email {email.get('id', 'unknown')}: {e}")
        
        print(f"\n🎉 Migration completed! Updated {updated_count} emails with direct URLs.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

async def verify_migration():
    """Verify that the migration was successful"""
    firebase_service = FirebaseService()
    
    try:
        print("\nVerifying migration...")
        
        # Get a sample of emails
        result = await firebase_service.get_emails(limit=10)
        
        emails_with_urls = 0
        emails_without_urls = 0
        
        for email in result['emails']:
            if email.get('has_attachments', False):
                if email.get('attachment_urls'):
                    emails_with_urls += 1
                    print(f"✅ Email {email['id']} has {len(email['attachment_urls'])} attachment URLs")
                else:
                    emails_without_urls += 1
                    print(f"❌ Email {email['id']} missing attachment URLs")
        
        print(f"\nVerification Results:")
        print(f"  Emails with URLs: {emails_with_urls}")
        print(f"  Emails without URLs: {emails_without_urls}")
        
        if emails_without_urls == 0:
            print("🎉 All emails with attachments now have direct URLs!")
        else:
            print("⚠️  Some emails still need migration.")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

async def show_url_examples():
    """Show examples of the generated URLs"""
    firebase_service = FirebaseService()
    
    try:
        print("\nURL Examples:")
        print("=" * 50)
        
        # Get first email with attachments
        result = await firebase_service.get_emails(limit=50)
        
        for email in result['emails']:
            if email.get('attachment_urls'):
                print(f"\nEmail: {email['subject']} (ID: {email['id']})")
                print(f"From: {email['from_email']}")
                
                for i, url_info in enumerate(email['attachment_urls']):
                    print(f"  Attachment {i}: {url_info['filename']}")
                    print(f"    Download: {url_info['url']}")
                    print(f"    View: {url_info['view_url']}")
                    print(f"    Type: {url_info['content_type']}")
                    print(f"    Size: {url_info['size']} bytes")
                
                break  # Show only first example
        
    except Exception as e:
        print(f"❌ Error showing examples: {e}")

if __name__ == "__main__":
    print("Firebase Direct URL Migration Tool")
    print("=" * 40)
    
    # Run migration
    asyncio.run(migrate_emails_to_direct_urls())
    
    # Verify migration
    asyncio.run(verify_migration())
    
    # Show examples
    asyncio.run(show_url_examples())
    
    print("\n" + "=" * 40)
    print("Migration complete! You can now use direct URLs to access attachments.")
    print("\nExample usage:")
    print("1. Get all attachment URLs: GET /webhook/emails/{email_id}/attachments/urls")
    print("2. Download attachment: GET /webhook/emails/{email_id}/attachments/0/download")
    print("3. View inline: GET /webhook/emails/{email_id}/attachments/0/view")
