#!/usr/bin/env python3
"""
Test script for Email Webhook System

This script helps test the email webhook functionality by:
1. Testing the webhook endpoint with sample data
2. Checking email polling status
3. Verifying Firebase connection
"""

import requests
import json
from datetime import datetime, timezone
from typing import Dict, Any

# Configuration
WEBHOOK_BASE_URL = "http://localhost:8001"
WEBHOOK_ENDPOINT = f"{WEBHOOK_BASE_URL}/webhook"

def test_webhook_health():
    """Test if the webhook service is running"""
    try:
        response = requests.get(f"{WEBHOOK_ENDPOINT}/health")
        if response.status_code == 200:
            print("✅ Webhook service is running")
            print(f"Health status: {response.json()}")
            return True
        else:
            print(f"❌ Webhook service returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to webhook service. Make sure it's running on port 8001")
        return False

def test_manual_email_webhook():
    """Test the manual email webhook endpoint with sample data"""
    sample_email = {
        "subject": "Test Email from Webhook Test",
        "from_email": "test@example.com",
        "to_email": "zeework98@gmail.com",
        "body": "This is a test email sent to verify the webhook functionality.",
        "html_body": "<p>This is a <strong>test email</strong> sent to verify the webhook functionality.</p>",
        "received_at": datetime.now(timezone.utc).isoformat(),
        "message_id": f"test-{datetime.now().timestamp()}@example.com",
        "user_token": None
    }
    
    try:
        response = requests.post(
            f"{WEBHOOK_ENDPOINT}/email",
            json=sample_email,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Manual email webhook test successful")
            print(f"Email ID: {result.get('email_id')}")
            return result.get('email_id')
        else:
            print(f"❌ Manual email webhook test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing manual email webhook: {e}")
        return None

def test_get_emails():
    """Test retrieving stored emails"""
    try:
        response = requests.get(f"{WEBHOOK_ENDPOINT}/emails?limit=5")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email retrieval test successful")
            print(f"Found {result.get('total', 0)} emails")
            print(f"Retrieved {len(result.get('emails', []))} emails")
            
            # Print first email details if available
            emails = result.get('emails', [])
            if emails:
                first_email = emails[0]
                print(f"Latest email: {first_email.get('subject', 'No subject')} from {first_email.get('from_email', 'Unknown')}")
            
            return True
        else:
            print(f"❌ Email retrieval test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing email retrieval: {e}")
        return False

def test_email_polling():
    """Test manual email polling"""
    try:
        response = requests.post(f"{WEBHOOK_ENDPOINT}/email/poll")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email polling test successful")
            print(f"Result: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Email polling test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing email polling: {e}")
        return False

def test_email_config():
    """Test email configuration"""
    try:
        response = requests.get(f"{WEBHOOK_ENDPOINT}/email/config")
        
        if response.status_code == 200:
            config = response.json()
            print("✅ Email configuration retrieved")
            print(f"Provider: {config.get('provider', 'Unknown')}")
            print(f"Configured: {config.get('configured', False)}")
            print(f"Polling enabled: {config.get('polling_enabled', False)}")
            print(f"Poll interval: {config.get('poll_interval', 'Unknown')} seconds")
            return True
        else:
            print(f"❌ Email configuration test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing email configuration: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Email Webhook System")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing webhook service health...")
    if not test_webhook_health():
        print("❌ Service is not running. Please start the webhook service first.")
        print("Run: python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload")
        return
    
    # Test 2: Email configuration
    print("\n2. Testing email configuration...")
    test_email_config()
    
    # Test 3: Manual email webhook
    print("\n3. Testing manual email webhook...")
    email_id = test_manual_email_webhook()
    
    # Test 4: Get emails
    print("\n4. Testing email retrieval...")
    test_get_emails()
    
    # Test 5: Email polling
    print("\n5. Testing email polling...")
    test_email_polling()
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    
    if email_id:
        print(f"\n📧 Test email stored with ID: {email_id}")
        print(f"View it at: {WEBHOOK_BASE_URL}/webhook/emails/{email_id}")
    
    print(f"\n📊 View all emails at: {WEBHOOK_BASE_URL}/webhook/emails")
    print(f"📖 API documentation at: {WEBHOOK_BASE_URL}/docs")

if __name__ == "__main__":
    main()


