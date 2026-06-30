"""
Test script for user and project lookup functionality

This script demonstrates how the email webhook now includes user and project lookup.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.user_project_service import UserProjectService
from models.schemas import EmailDataSchema

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_user_project_lookup():
    """Test the user and project lookup functionality"""
    
    # Initialize the service
    user_project_service = UserProjectService()
    
    # Test email addresses
    test_emails = [
        "john.doe@example.com",
        "jane.smith@company.com", 
        "unknown@example.com"
    ]
    
    print("=" * 60)
    print("Testing User and Project Lookup Functionality")
    print("=" * 60)
    
    for email in test_emails:
        print(f"\n🔍 Testing lookup for: {email}")
        print("-" * 40)
        
        # Test user lookup
        user_result = await user_project_service.lookup_user_by_email(email)
        print(f"User Lookup Result:")
        print(f"  Found: {user_result['found']}")
        print(f"  First Name: {user_result['username']}")  # Note: 'username' key contains firstName
        print(f"  User ID: {user_result.get('user_id', 'N/A')}")
        
        # Test project lookup if user found
        if user_result['found']:
            project_result = await user_project_service.lookup_user_project(user_result['user_id'])
            print(f"\nProject Lookup Result:")
            print(f"  Found: {project_result['found']}")
            if project_result['found']:
                project = project_result['project']
                print(f"  Project Name: {project.get('name', 'N/A')}")
                print(f"  Project ID: {project.get('id', 'N/A')}")
            else:
                print(f"  Message: {project_result.get('message', 'No project assigned')}")
        
        # Test combined lookup
        print(f"\nCombined Lookup Result:")
        combined_result = await user_project_service.get_user_and_project_data(email)
        print(f"  User First Name: {combined_result['user']['username']} (found: {combined_result['user']['found']})")
        print(f"  Project: {combined_result['project']['found']}")
        if combined_result['project']['found']:
            project_name = combined_result['project']['project'].get('name', 'N/A')
            print(f"    Project Name: {project_name}")

async def test_email_processing():
    """Test how the enhanced email processing works"""
    
    print("\n" + "=" * 60)
    print("Testing Enhanced Email Processing")
    print("=" * 60)
    
    # Create a sample email
    sample_email = EmailDataSchema(
        subject="Test Email with User Lookup",
        from_email="john.doe@example.com",
        to_email="webhook@company.com",
        body="This is a test email to demonstrate user and project lookup functionality.",
        received_at=datetime.now(timezone.utc),
        message_id="test-message-123"
    )
    
    print(f"\n📧 Sample Email:")
    print(f"  Subject: {sample_email.subject}")
    print(f"  From: {sample_email.from_email}")
    print(f"  To: {sample_email.to_email}")
    
    # The FirebaseService will automatically lookup user and project data
    # when storing the email, and include it in the document
    print(f"\n✅ When this email is processed by the webhook:")
    print(f"  1. System looks up user by email: {sample_email.from_email}")
    print(f"  2. If user found, gets their firstName")
    print(f"  3. If user found, looks up their assigned project")
    print(f"  4. Stores email with user and project data included")
    
    # Show what fields will be added to the email document
    print(f"\n📝 Additional fields stored in Firebase:")
    print(f"  - sender_username: 'firstName' or 'unknown'")
    print(f"  - sender_user_id: user document ID or null")
    print(f"  - sender_found: true/false")
    print(f"  - assigned_project: project object or null")
    print(f"  - project_found: true/false")

def print_usage_instructions():
    """Print usage instructions"""
    
    print("\n" + "=" * 60)
    print("Usage Instructions")
    print("=" * 60)
    
    print("\n1. Firebase Collections Required:")
    print("   - 'users' collection with documents containing:")
    print("     - email: string (sender email address)")
    print("     - firstName: string (primary field used)")
    print("     - username: string (fallback field)")
    print("     - name: string (fallback field)")
    print("   - 'assignProjects' collection with documents containing:")
    print("     - userId: string (user document ID)")
    print("     - projectId: string (project document ID)")
    print("   - 'projects' collection with documents containing:")
    print("     - name: string (project name)")
    print("     - other project fields...")
    
    print("\n2. Email Processing Flow:")
    print("   - Email received via webhook")
    print("   - System looks up sender email in 'users' collection")
    print("   - If found, gets username and user ID")
    print("   - System looks up user ID in 'assignProjects' collection")
    print("   - If found, gets first assigned project ID")
    print("   - System fetches project details from 'projects' collection")
    print("   - Email stored with all lookup data included")
    
    print("\n3. API Endpoints:")
    print("   - POST /webhook/email (stores email with user/project lookup)")
    print("   - GET /webhook/emails (lists emails with user/project data)")
    print("   - GET /webhook/emails/{id} (get specific email with all data)")

if __name__ == "__main__":
    print("Email Webhook User & Project Lookup Test")
    print("Note: This test requires Firebase connection and collections setup")
    
    # Print usage instructions
    print_usage_instructions()
    
    # Uncomment to run actual tests (requires Firebase setup)
    # asyncio.run(test_user_project_lookup())
    # asyncio.run(test_email_processing())
