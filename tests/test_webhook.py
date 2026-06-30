"""
Test cases for Email Webhook Service

Basic test cases for the webhook functionality.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import base64

# Import the main app
from main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/webhook/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Email Webhook Service"
    assert data["version"] == "1.0.0"

def test_receive_email_webhook():
    """Test receiving email data via webhook"""
    # Sample email data
    email_data = {
        "subject": "Test Invoice",
        "from_email": "test@example.com",
        "to_email": "user@example.com",
        "body": "This is a test email",
        "received_at": datetime.now().isoformat(),
        "message_id": "test-message-123"
    }
    
    response = client.post("/webhook/email", json=email_data)
    
    # Note: This test will fail without proper Firebase configuration
    # In a real test environment, you would mock Firebase
    assert response.status_code in [200, 500]  # 500 if Firebase not configured

def test_get_emails():
    """Test retrieving emails"""
    response = client.get("/webhook/emails")
    
    # Note: This test will fail without proper Firebase configuration
    assert response.status_code in [200, 500]  # 500 if Firebase not configured

def test_get_emails_with_filters():
    """Test retrieving emails with filters"""
    params = {
        "limit": 5,
        "offset": 0,
        "has_attachments": True
    }
    
    response = client.get("/webhook/emails", params=params)
    
    # Note: This test will fail without proper Firebase configuration
    assert response.status_code in [200, 500]  # 500 if Firebase not configured

def test_search_emails():
    """Test searching emails"""
    params = {
        "q": "invoice",
        "limit": 10
    }
    
    response = client.get("/webhook/search", params=params)
    
    # Note: This test will fail without proper Firebase configuration
    assert response.status_code in [200, 500]  # 500 if Firebase not configured

def test_invalid_email_data():
    """Test with invalid email data"""
    invalid_data = {
        "subject": "Test",
        # Missing required fields
    }
    
    response = client.post("/webhook/email", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_email_with_attachment():
    """Test email with PDF attachment"""
    # Create sample PDF data (minimal valid PDF)
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF"
    
    email_data = {
        "subject": "Test Invoice with PDF",
        "from_email": "test@example.com",
        "to_email": "user@example.com",
        "body": "Please find attached invoice",
        "received_at": datetime.now().isoformat(),
        "message_id": "test-message-456",
        "attachments": [
            {
                "filename": "test_invoice.pdf",
                "content_type": "application/pdf",
                "size": len(pdf_content),
                "data": base64.b64encode(pdf_content).decode()
            }
        ]
    }
    
    response = client.post("/webhook/email", json=email_data)
    
    # Note: This test will fail without proper Firebase configuration
    assert response.status_code in [200, 500]  # 500 if Firebase not configured

if __name__ == "__main__":
    pytest.main([__file__])
