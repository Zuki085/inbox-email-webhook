#!/usr/bin/env python3
"""
Migration script to move attachments from nested arrays to separate collection

This script helps migrate existing emails with attachments to the new structure.
"""

import asyncio
from services.firebase_service import FirebaseService

async def migrate_existing_attachments():
    """Migrate existing attachments to separate collection"""
    
    firebase_service = FirebaseService()
    
    try:
        print("Starting attachment migration...")
        
        # Get all emails with attachments
        result = await firebase_service.get_emails(limit=1000)
        
        emails_to_migrate = []
        for email in result['emails']:
            if email.get('has_attachments', False) and email.get('attachments'):
                emails_to_migrate.append(email)
        
        print(f"Found {len(emails_to_migrate)} emails with attachments to migrate")
        
        if not emails_to_migrate:
            print("No emails need migration.")
            return
        
        migrated_count = 0
        for email in emails_to_migrate:
            try:
                email_id = email['id']
                attachments = email['attachments']
                
                print(f"Migrating email {email_id} with {len(attachments)} attachments...")
                
                # Create separate documents for each attachment
                for i, attachment in enumerate(attachments):
                    attachment_doc = {
                        'email_id': email_id,
                        'filename': str(attachment.get('filename', f'attachment_{i}')),
                        'content_type': str(attachment.get('content_type', 'application/octet-stream')),
                        'size': int(attachment.get('size', 0)),
                        'data': str(attachment.get('data', '')),
                        'attachment_index': int(i),
                        'download_url': f"http://localhost:8000/webhook/emails/{email_id}/attachments/{i}/download",
                        'view_url': f"http://localhost:8000/webhook/emails/{email_id}/attachments/{i}/view",
                        'created_at': firebase_service.db.SERVER_TIMESTAMP
                    }
                    
                    # Store in separate collection
                    attachment_ref = firebase_service.db.collection('email_attachments').document()
                    attachment_ref.set(attachment_doc)
                
                # Remove attachments array from main email document
                email_ref = firebase_service.db.collection('emails').document(email_id)
                email_ref.update({
                    'attachments': firebase_service.db.DELETE_FIELD,
                    'attachment_urls': firebase_service.db.DELETE_FIELD,
                    'migrated': True,
                    'updated_at': firebase_service.db.SERVER_TIMESTAMP
                })
                
                migrated_count += 1
                print(f"✅ Migrated email {email_id}")
                
            except Exception as e:
                print(f"❌ Error migrating email {email.get('id', 'unknown')}: {e}")
        
        print(f"\n🎉 Migration completed! Migrated {migrated_count} emails.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

async def verify_migration():
    """Verify that the migration was successful"""
    
    firebase_service = FirebaseService()
    
    try:
        print("\nVerifying migration...")
        
        # Check emails collection
        emails_result = await firebase_service.get_emails(limit=10)
        emails_with_attachments = 0
        emails_without_attachments = 0
        
        for email in emails_result['emails']:
            if email.get('has_attachments', False):
                emails_with_attachments += 1
            else:
                emails_without_attachments += 1
        
        # Check attachments collection
        attachments_query = firebase_service.db.collection('email_attachments')
        attachments_docs = list(attachments_query.limit(10).stream())
        attachment_count = len(attachments_docs)
        
        print(f"Emails with attachments: {emails_with_attachments}")
        print(f"Emails without attachments: {emails_without_attachments}")
        print(f"Attachments in separate collection: {attachment_count}")
        
        if attachment_count > 0:
            print("✅ Attachments successfully moved to separate collection")
        else:
            print("⚠️  No attachments found in separate collection")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

async def show_attachment_urls():
    """Show examples of the new attachment URLs"""
    
    firebase_service = FirebaseService()
    
    try:
        print("\nAttachment URL Examples:")
        print("=" * 50)
        
        # Get first email with attachments
        result = await firebase_service.get_emails(limit=50)
        
        for email in result['emails']:
            if email.get('has_attachments', False):
                email_id = email['id']
                urls = await firebase_service.get_attachment_urls(email_id)
                
                if urls:
                    print(f"\nEmail: {email['subject']} (ID: {email_id})")
                    print(f"From: {email['from_email']}")
                    
                    for url_info in urls:
                        print(f"  📎 {url_info['filename']}")
                        print(f"     Download: {url_info['url']}")
                        print(f"     View: {url_info['view_url']}")
                        print(f"     Type: {url_info['content_type']}")
                        print(f"     Size: {url_info['size']} bytes")
                    
                    break  # Show only first example
        
    except Exception as e:
        print(f"❌ Error showing examples: {e}")

async def main():
    """Run migration and verification"""
    print("Firebase Attachment Migration Tool")
    print("=" * 40)
    
    # Run migration
    await migrate_existing_attachments()
    
    # Verify migration
    await verify_migration()
    
    # Show examples
    await show_attachment_urls()
    
    print("\n" + "=" * 40)
    print("Migration complete!")
    print("\nBenefits of the new structure:")
    print("✅ No more Firebase nested array errors")
    print("✅ Better performance for large attachments")
    print("✅ Easier to query and manage attachments")
    print("✅ Direct URLs for browser access")
    print("✅ Scalable for high-volume email processing")

if __name__ == "__main__":
    asyncio.run(main())
