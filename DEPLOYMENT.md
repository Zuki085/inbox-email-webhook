# Email Webhook Deployment Guide

This guide covers deploying the Email Webhook Service in different environments.

## 🚀 Quick Start

### 1. Standalone Deployment

```bash
# Navigate to email-webhook directory
cd email-webhook

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FIREBASE_PROJECT_ID="your-project-id"
export FIREBASE_SERVICE_ACCOUNT_KEY_PATH="/path/to/service-account-key.json"

# Run the service
python -m email_webhook.main
```

### 2. Integrated Deployment

The webhook is already integrated into your main application. Just ensure Firebase is configured:

```bash
# Set environment variables
export FIREBASE_PROJECT_ID="your-project-id"
export FIREBASE_SERVICE_ACCOUNT_KEY_PATH="/path/to/service-account-key.json"

# Run main application
python main.py
```

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# Firebase Configuration (choose one method)

# Method 1: Service Account Key File
export FIREBASE_SERVICE_ACCOUNT_KEY_PATH="/path/to/service-account-key.json"

# Method 2: Environment Variables (recommended for production)
export FIREBASE_PROJECT_ID="your-firebase-project-id"
export FIREBASE_PRIVATE_KEY_ID="your-private-key-id"
export FIREBASE_PRIVATE_KEY="your-private-key"
export FIREBASE_CLIENT_EMAIL="your-client-email"
export FIREBASE_CLIENT_ID="your-client-id"
export FIREBASE_AUTH_URI="https://accounts.google.com/o/oauth2/auth"
export FIREBASE_TOKEN_URI="https://oauth2.googleapis.com/token"
export FIREBASE_AUTH_PROVIDER_X509_CERT_URL="https://www.googleapis.com/oauth2/v1/certs"
export FIREBASE_CLIENT_X509_CERT_URL="https://www.googleapis.com/robot/v1/metadata/x509/your-client-email"
```

### Optional Environment Variables

```bash
# Application Settings
export DEBUG="false"
export LOG_LEVEL="INFO"
export CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"

# File Processing Settings
export MAX_FILE_SIZE="10485760"  # 10MB
export ALLOWED_FILE_TYPES="pdf,jpg,jpeg,png"
export UPLOAD_DIRECTORY="Static"

# Pagination Settings
export DEFAULT_PAGE_SIZE="10"
export MAX_PAGE_SIZE="100"
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY email-webhook/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY email-webhook/ ./email-webhook/
COPY main.py .
COPY global_functions.py .
COPY database.py .
COPY models.py .
COPY Routers/ ./Routers/

# Create upload directory
RUN mkdir -p Static

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
    email-webhook:
        build: .
        ports:
            - '8000:8000'
        environment:
            - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
            - FIREBASE_SERVICE_ACCOUNT_KEY_PATH=/app/service-account-key.json
        volumes:
            - ./service-account-key.json:/app/service-account-key.json:ro
            - ./Static:/app/Static
        restart: unless-stopped
```

## ☁️ Cloud Deployment

### Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/email-webhook

# Deploy to Cloud Run
gcloud run deploy email-webhook \
  --image gcr.io/PROJECT_ID/email-webhook \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=your-project-id
```

### AWS Lambda (using Mangum)

```python
# lambda_handler.py
from mangum import Mangum
from email_webhook.main import app

handler = Mangum(app)
```

### Heroku

```bash
# Create Procfile
echo "web: python main.py" > Procfile

# Deploy
git add .
git commit -m "Deploy email webhook"
git push heroku main
```

## 🔒 Security Considerations

### 1. Firebase Security Rules

```javascript
// firestore.rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /emails/{emailId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### 2. CORS Configuration

```python
# In production, configure CORS properly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

### 3. Environment Variables

-   Never commit `.env` files
-   Use secret management services (AWS Secrets Manager, Azure Key Vault, etc.)
-   Rotate credentials regularly

## 📊 Monitoring & Logging

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/webhook/health

# Detailed health check
curl http://localhost:8000/webhook/health | jq
```

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email-webhook.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics Collection

Consider integrating with:

-   Prometheus + Grafana
-   AWS CloudWatch
-   Google Cloud Monitoring
-   Datadog

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy Email Webhook

on:
    push:
        branches: [main]

jobs:
    deploy:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v3

            - name: Set up Python
              uses: actions/setup-python@v4
              with:
                  python-version: '3.11'

            - name: Install dependencies
              run: |
                  pip install -r email-webhook/requirements.txt

            - name: Run tests
              run: |
                  pip install pytest
                  pytest email-webhook/tests/

            - name: Deploy to production
              run: |
                  # Your deployment commands here
```

## 🐛 Troubleshooting

### Common Issues

1. **Firebase Authentication Error**

    ```
    Error: Failed to initialize Firebase: Invalid credentials
    ```

    - Check environment variables
    - Verify service account key file path
    - Ensure Firebase project exists

2. **Import Errors**

    ```
    ModuleNotFoundError: No module named 'email_webhook'
    ```

    - Ensure you're in the correct directory
    - Check Python path
    - Install the package: `pip install -e .`

3. **File Processing Errors**
    ```
    Error processing PDF attachment: No data extracted
    ```
    - Check PDF file integrity
    - Verify file size limits
    - Ensure proper base64 encoding

### Debug Mode

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debug output
python -m email_webhook.main
```

## 📈 Performance Optimization

### 1. Database Indexing

Create Firestore indexes for common queries:

```json
{
	"indexes": [
		{
			"collectionGroup": "emails",
			"queryScope": "COLLECTION",
			"fields": [
				{ "fieldPath": "user_token", "order": "ASCENDING" },
				{ "fieldPath": "created_at", "order": "DESCENDING" }
			]
		}
	]
}
```

### 2. Caching

Consider implementing Redis caching for frequently accessed data:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Cache email data
def get_cached_email(email_id):
    cached = redis_client.get(f"email:{email_id}")
    if cached:
        return json.loads(cached)
    return None
```

### 3. Rate Limiting

Implement rate limiting for webhook endpoints:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/email")
@limiter.limit("10/minute")
async def receive_email_webhook(request: Request, email_data: EmailDataSchema):
    # Your webhook logic here
```

## 📚 Additional Resources

-   [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin)
-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
-   [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
