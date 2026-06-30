#!/usr/bin/env python3
"""
Email Configuration Test Script

This script helps you test your email configuration before running the main application.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.email_config import EmailConfig
from services.email_poller import EmailPoller
from config.firebase_config import initialize_firebase

async def test_firebase_connection():
    """Test Firebase connection"""
    print("🔍 Testing Firebase connection...")
    try:
        db = initialize_firebase()
        print("✅ Firebase connection successful")
        return True
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return False

def test_email_config():
    """Test email configuration"""
    print("🔍 Testing email configuration...")
    try:
        config = EmailConfig()
        
        print(f"📧 Email Provider: {config.provider.value}")
        print(f"🔗 IMAP Config: {config.get_imap_config()}")
        print(f"📤 SMTP Config: {config.get_smtp_config()}")
        print(f"🔐 Credentials configured: {config.validate_config()}")
        
        if config.validate_config():
            print("✅ Email configuration is valid")
            return True
        else:
            print("❌ Email configuration is invalid - check your credentials")
            return False
    except Exception as e:
        print(f"❌ Email configuration test failed: {e}")
        return False

async def test_email_connection():
    """Test email connection"""
    print("🔍 Testing email connection...")
    try:
        poller = EmailPoller()
        
        if not poller.poll_enabled:
            print("ℹ️ Email polling is disabled")
            return True
        
        # Test connection by attempting to connect
        import imaplib
        
        if poller.email_use_ssl:
            mail = imaplib.IMAP4_SSL(poller.email_host, poller.email_port)
        else:
            mail = imaplib.IMAP4(poller.email_host, poller.email_port)
        
        mail.login(poller.email_username, poller.email_password)
        mail.select('INBOX')
        mail.close()
        mail.logout()
        
        print("✅ Email connection successful")
        return True
    except Exception as e:
        print(f"❌ Email connection failed: {e}")
        return False

async def test_email_polling():
    """Test email polling (without storing)"""
    print("🔍 Testing email polling...")
    try:
        poller = EmailPoller()
        
        if not poller.poll_enabled:
            print("ℹ️ Email polling is disabled")
            return True
        
        # Test polling without storing
        await poller.poll_emails()
        print("✅ Email polling test successful")
        return True
    except Exception as e:
        print(f"❌ Email polling test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Email Webhook Configuration Tests\n")
    
    # Load environment variables
    load_dotenv()
    
    tests = [
        ("Firebase Connection", test_firebase_connection()),
        ("Email Configuration", test_email_config()),
        ("Email Connection", test_email_connection()),
        ("Email Polling", test_email_polling())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your configuration is ready.")
        print("\nNext steps:")
        print("1. Run: python -m email-webhook.main")
        print("2. Check: http://localhost:8001/webhook/health")
        print("3. Test: http://localhost:8001/webhook/email/config")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.")
        print("\nTroubleshooting:")
        print("1. Check your .env file")
        print("2. Verify Firebase credentials")
        print("3. Verify email credentials")
        print("4. Check the EMAIL_CONFIGURATION.md guide")

if __name__ == "__main__":
    asyncio.run(main())
