#!/usr/bin/env python3
"""
Example script to view and access email attachments from Firebase

This script demonstrates different ways to access attachments stored in Firebase.
"""

import asyncio
import base64
import os
from services.firebase_service import FirebaseService

async def view_attachments_example():
    """Example of how to view and access attachments"""
    
    # Initialize Firebase service
    firebase_service = FirebaseService()
    
    # Example email ID (replace with actual email ID from your Firebase)
    email_id = "your-email-document-id-here"
    
    try:
        # Method 1: Get email data with attachments
        print("=== Method 1: Get Email with Attachments ===")
        email_data = await firebase_service.get_email_by_id(email_id)
        
        if email_data.get('attachments'):
            print(f"Email has {len(email_data['attachments'])} attachments:")
            for i, attachment in enumerate(email_data['attachments']):
                print(f"  {i}: {attachment['filename']} ({attachment['content_type']}, {attachment['size']} bytes)")
        else:
            print("No attachments found")
        
        # Method 2: Get specific attachment data
        if email_data.get('attachments'):
            print("\n=== Method 2: Get Specific Attachment Data ===")
            attachment_data = await firebase_service.get_attachment_data(email_id, 0)
            print(f"Attachment: {attachment_data['filename']}")
            print(f"Content Type: {attachment_data['content_type']}")
            print(f"Size: {attachment_data['size']} bytes")
            print(f"Base64 data preview: {attachment_data['data'][:50]}...")
        
        # Method 3: Decode and save attachment to file
        if email_data.get('attachments'):
            print("\n=== Method 3: Save Attachment to File ===")
            output_path = await firebase_service.decode_attachment_to_file(
                email_id, 
                0, 
                f"downloaded_{email_data['attachments'][0]['filename']}"
            )
            print(f"Attachment saved to: {output_path}")
            print(f"File size: {os.path.getsize(output_path)} bytes")
        
        # Method 4: Create a data URL for web viewing
        if email_data.get('attachments'):
            print("\n=== Method 4: Create Data URL for Web Viewing ===")
            attachment_data = await firebase_service.get_attachment_data(email_id, 0)
            data_url = f"data:{attachment_data['content_type']};base64,{attachment_data['data']}"
            print(f"Data URL (first 100 chars): {data_url[:100]}...")
            print("You can use this data URL directly in an <img> tag or <a> tag for web viewing")
        
    except Exception as e:
        print(f"Error: {e}")

async def list_all_emails_with_attachments():
    """List all emails that have attachments"""
    
    firebase_service = FirebaseService()
    
    try:
        # Get all emails
        result = await firebase_service.get_emails(limit=50)
        
        print("=== Emails with Attachments ===")
        for email in result['emails']:
            if email.get('has_attachments', False):
                print(f"Email ID: {email['id']}")
                print(f"Subject: {email['subject']}")
                print(f"From: {email['from_email']}")
                print(f"Attachments: {email.get('attachment_count', 0)}")
                print(f"Created: {email.get('created_at')}")
                print("-" * 50)
        
    except Exception as e:
        print(f"Error: {e}")

def create_html_viewer(email_id: str, attachment_index: int = 0):
    """
    Create an HTML file to view attachment in browser
    
    Args:
        email_id: Email document ID
        attachment_index: Index of attachment to view
    """
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Email Attachment Viewer</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .attachment {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; }}
        .download-btn {{ 
            background: #007bff; 
            color: white; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 5px; 
            display: inline-block;
            margin: 10px 0;
        }}
        .download-btn:hover {{ background: #0056b3; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Email Attachment Viewer</h1>
        <p>Email ID: {email_id}</p>
        <p>Attachment Index: {attachment_index}</p>
        
        <div class="attachment">
            <h3>View Attachment</h3>
            <p>To view this attachment, you can:</p>
            <ol>
                <li>Use the API endpoint: <code>GET /webhook/emails/{email_id}/attachments/{attachment_index}/download</code></li>
                <li>Use the Firebase service methods in Python</li>
                <li>Access the Base64 data directly from Firebase</li>
            </ol>
            
            <a href="/webhook/emails/{email_id}/attachments/{attachment_index}/download" 
               class="download-btn">Download Attachment</a>
        </div>
    </div>
</body>
</html>
    """
    
    with open("attachment_viewer.html", "w") as f:
        f.write(html_template)
    
    print("HTML viewer created: attachment_viewer.html")
    print("Open this file in your browser to see the interface")

if __name__ == "__main__":
    print("Email Attachment Viewer Examples")
    print("=" * 40)
    
    # Example 1: View attachments for a specific email
    # Replace 'your-email-document-id-here' with actual email ID
    print("1. To view attachments for a specific email:")
    print("   - Replace 'your-email-document-id-here' with actual email ID")
    print("   - Run: asyncio.run(view_attachments_example())")
    
    # Example 2: List all emails with attachments
    print("\n2. To list all emails with attachments:")
    print("   - Run: asyncio.run(list_all_emails_with_attachments())")
    
    # Example 3: Create HTML viewer
    print("\n3. To create an HTML viewer:")
    print("   - Run: create_html_viewer('your-email-id', 0)")
    
    print("\n" + "=" * 40)
    print("Available API Endpoints:")
    print("- GET /webhook/emails/{email_id}/attachments")
    print("- GET /webhook/emails/{email_id}/attachments/{attachment_index}/download")
