#!/usr/bin/env python3
"""
Email Webhook Service Startup Script

This script starts the email webhook service with proper configuration.
"""

import os
import sys
import uvicorn
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    has_legacy_email = os.getenv('EMAIL_USERNAME') and os.getenv('EMAIL_PASSWORD')

    if not has_legacy_email:
        print("ℹ️  No legacy EMAIL_USERNAME/EMAIL_PASSWORD set.")
        print("   Multi-user mode: configure email + app_password on each user in Firestore.")
        print("   Or set EMAIL_USERNAME/EMAIL_PASSWORD for single-mailbox fallback.")

    return True

def check_firebase_config():
    """Check if Firebase is configured"""
    firebase_key_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
    firebase_project_id = os.getenv('FIREBASE_PROJECT_ID')
    
    if not firebase_key_path and not firebase_project_id:
        print("❌ Firebase configuration missing!")
        print("Please set either FIREBASE_SERVICE_ACCOUNT_KEY_PATH or FIREBASE_PROJECT_ID")
        print("See GMAIL_SETUP.md for detailed instructions.")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🚀 Starting Email Webhook Service")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check Firebase configuration
    if not check_firebase_config():
        sys.exit(1)
    
    # Display configuration
    print("✅ Environment configuration looks good!")
    print(f"📧 Legacy email: {os.getenv('EMAIL_USERNAME', 'Not set (using Firestore users)')}")
    print(f"🔥 Firebase: {'Configured' if os.getenv('FIREBASE_PROJECT_ID') else 'Using service account key'}")
    print(f"⏱️  Poll interval: {os.getenv('EMAIL_POLL_INTERVAL', '60')} seconds")
    
    # Start the service
    print("\n🌐 Starting webhook service...")
    print("📖 API documentation will be available at: http://localhost:8001/docs")
    print("🔗 Webhook endpoint: http://localhost:8001/webhook/email")
    print("📊 View emails: http://localhost:8001/webhook/emails")
    print("\nPress Ctrl+C to stop the service")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Service stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


